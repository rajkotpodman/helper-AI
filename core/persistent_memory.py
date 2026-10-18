"""Persistent Multi-Session Memory Engine for Helper-AI.

Combines SQLite ACID storage with Mem0 / ChromaDB semantic memory
for complete recall across user sessions:
- Past GitHub repositories fetched
- Generated and published social posts (Facebook, LinkedIn, Blogger, etc.)
- User preferences, corrections, and explicit instructions
- Reflexion feedback and ground-truth execution outcomes
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("PersistentMemory")

DB_DIR = Path("data")
DB_PATH = DB_DIR / "helper_memory.db"


class PersistentMemoryManager:
    """Manages persistent multi-session recall using SQLite and Mem0."""

    _instance: Optional["PersistentMemoryManager"] = None

    @classmethod
    def get_instance(cls) -> "PersistentMemoryManager":
        if cls._instance is None:
            cls._instance = PersistentMemoryManager()
        return cls._instance

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_sqlite()
        self._mem0_instance = None
        self._init_mem0()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite(self):
        """Initializes SQLite schema for repos, posts, facts, and reflexion records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Repositories cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    language TEXT,
                    stars INTEGER DEFAULT 0,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Generated & Published Posts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    repo_name TEXT,
                    language TEXT DEFAULT 'en',
                    content TEXT NOT NULL,
                    status TEXT NOT NULL,
                    is_verified INTEGER DEFAULT 0,
                    file_path TEXT,
                    post_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. User facts and preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                )
            """)

            # 4. Reflexion actions and evaluations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    target TEXT,
                    was_successful INTEGER NOT NULL,
                    ground_truth_details TEXT,
                    failure_reason TEXT,
                    suggested_fix TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _init_mem0(self):
        """Attempts to initialize Mem0 client with safe fallback."""
        try:
            import mem0
            from mem0 import Memory
            self._mem0_instance = Memory()
            logger.info("Mem0 memory manager initialized successfully.")
        except Exception as e:
            logger.info(f"Mem0 initialized in offline-SQLite mode (semantic fallback active): {e}")
            self._mem0_instance = None

    # =========================================================================
    # Repository Memory
    # =========================================================================
    def remember_repo(
        self,
        full_name: str,
        description: str = "",
        language: str = "",
        stars: int = 0
    ) -> bool:
        """Saves or updates a GitHub repository in persistent memory."""
        name = full_name.strip()
        if not name:
            return False
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO repos (full_name, description, language, stars, fetched_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(full_name) DO UPDATE SET
                        description=excluded.description,
                        language=excluded.language,
                        stars=excluded.stars,
                        fetched_at=CURRENT_TIMESTAMP
                """, (name, description.strip(), language.strip(), stars))
                conn.commit()

            # Also push to mem0 if active
            if self._mem0_instance:
                try:
                    self._mem0_instance.add(
                        f"GitHub Repository: {name}. Description: {description}. Language: {language}.",
                        user_id="default_user",
                        metadata={"type": "github_repo", "repo_name": name}
                    )
                except Exception:
                    pass

            return True
        except Exception as e:
            logger.error(f"Error remembering repo {full_name}: {e}")
            return False

    def get_known_repos(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Returns list of all known repositories stored in persistent memory."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT full_name, description, language, stars, fetched_at
                    FROM repos
                    ORDER BY fetched_at DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"Error fetching known repos: {e}")
            return []

    # =========================================================================
    # Social Posts Memory
    # =========================================================================
    def remember_post(
        self,
        platform: str,
        content: str,
        repo_name: Optional[str] = None,
        language: str = "gu",
        status: str = "published",
        is_verified: bool = True,
        file_path: Optional[str] = None,
        post_url: Optional[str] = None
    ) -> int:
        """Saves a generated/published post to persistent memory."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO posts (platform, repo_name, language, content, status, is_verified, file_path, post_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    platform.lower().strip(),
                    (repo_name or "").strip(),
                    language.strip(),
                    content.strip(),
                    status.strip(),
                    1 if is_verified else 0,
                    str(file_path or ""),
                    str(post_url or "")
                ))
                conn.commit()
                post_id = cursor.lastrowid or 0

            # Also index into mem0 if active
            if self._mem0_instance and content:
                try:
                    summary = content[:300].replace("\n", " ")
                    self._mem0_instance.add(
                        f"Published {platform} post for repo '{repo_name}' ({language}): {summary}",
                        user_id="default_user",
                        metadata={"type": "social_post", "platform": platform, "repo_name": repo_name or ""}
                    )
                except Exception:
                    pass

            return post_id
        except Exception as e:
            logger.error(f"Error remembering post: {e}")
            return 0

    def get_posts(
        self,
        platform: Optional[str] = None,
        repo_name: Optional[str] = None,
        only_verified: bool = False,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Retrieves stored posts matching platform or repository filters."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM posts WHERE 1=1"
                params = []

                if platform:
                    query += " AND platform = ?"
                    params.append(platform.lower().strip())
                if repo_name:
                    query += " AND repo_name LIKE ?"
                    params.append(f"%{repo_name.strip()}%")
                if only_verified:
                    query += " AND is_verified = 1"

                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, tuple(params))
                return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error querying posts: {e}")
            return []

    def is_repo_already_posted(self, repo_name: str, platform: str = "facebook") -> bool:
        """Checks if a verified post already exists for this repository and platform."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM posts
                    WHERE platform = ? AND repo_name = ? AND is_verified = 1
                    LIMIT 1
                """, (platform.lower().strip(), repo_name.strip()))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking repo post status: {e}")
            return False

    # =========================================================================
    # User Facts & Preferences
    # =========================================================================
    def remember_fact(self, category: str, key: str, value: str):
        """Stores a persistent fact or user preference."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_facts (category, key, value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(category, key) DO UPDATE SET
                        value=excluded.value,
                        updated_at=CURRENT_TIMESTAMP
                """, (category.strip(), key.strip(), value.strip()))
                conn.commit()

            if self._mem0_instance:
                try:
                    self._mem0_instance.add(
                        f"User Fact [{category}] {key}: {value}",
                        user_id="default_user",
                        metadata={"category": category, "key": key}
                    )
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error remembering fact: {e}")

    def get_fact(self, category: str, key: str) -> Optional[str]:
        """Retrieves a stored user fact."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM user_facts
                    WHERE category = ? AND key = ?
                """, (category.strip(), key.strip()))
                row = cursor.fetchone()
                return row["value"] if row else None
        except Exception as e:
            logger.error(f"Error getting fact: {e}")
            return None

    # =========================================================================
    # Reflexion & Action Records
    # =========================================================================
    def record_reflection(
        self,
        action: str,
        target: str,
        was_successful: bool,
        ground_truth_details: str,
        failure_reason: Optional[str] = None,
        suggested_fix: Optional[str] = None
    ):
        """Records ground-truth evaluation and self-reflection outcome."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO action_reflections (
                        action, target, was_successful, ground_truth_details, failure_reason, suggested_fix, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    action.strip(),
                    target.strip(),
                    1 if was_successful else 0,
                    ground_truth_details.strip(),
                    (failure_reason or "").strip(),
                    (suggested_fix or "").strip()
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Error recording reflection: {e}")

    def get_recent_reflections(self, action: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns recent reflexion evaluations to prevent repeating errors."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if action:
                    cursor.execute("""
                        SELECT * FROM action_reflections
                        WHERE action = ?
                        ORDER BY created_at DESC LIMIT ?
                    """, (action.strip(), limit))
                else:
                    cursor.execute("""
                        SELECT * FROM action_reflections
                        ORDER BY created_at DESC LIMIT ?
                    """, (limit,))
                return [dict(r) for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting reflections: {e}")
            return []

    # =========================================================================
    # Context Formatting for Agent Prompt
    # =========================================================================
    def format_memory_for_prompt(self, goal: str) -> str:
        """
        Synthesizes relevant multi-session persistent memories
        (known repos, past posts, user rules, and past reflections)
        into a concise, high-impact context block for the LLM.
        """
        lines = []
        lower_goal = goal.lower()

        # 1. Repositories
        repos = self.get_known_repos(limit=10)
        if repos:
            lines.append("📁 KNOWN GITHUB REPOSITORIES (From Multi-Session Persistent Memory):")
            for r in repos:
                desc = f" - {r['description'][:80]}..." if r.get('description') else ""
                lines.append(f"  • {r['full_name']}{desc}")
            lines.append("")

        # 2. Existing Verified Posts
        posts = self.get_posts(limit=10)
        if posts:
            lines.append("📝 PREVIOUSLY PUBLISHED POSTS (DO NOT DUPLICATE THESE):")
            for p in posts:
                v_badge = "✅ Live" if p.get("is_verified") else "⚠️ Unverified"
                repo_tag = f" [Repo: {p['repo_name']}]" if p.get('repo_name') else ""
                lines.append(f"  • {p['platform'].upper()}{repo_tag} ({v_badge}) on {p['created_at']}")
            lines.append("")

        # 3. Recent Action Reflections / Lessons Learned
        reflections = self.get_recent_reflections(limit=4)
        failures = [rf for rf in reflections if not rf.get("was_successful")]
        if failures:
            lines.append("🛡️ GROUND-TRUTH REFLEXION LESSONS (Avoid Repeating Past Mistakes):")
            for f in failures:
                lines.append(f"  • {f['action']}: {f['failure_reason']}. Solution: {f['suggested_fix']}")
            lines.append("")

        # 4. Mem0 Semantic Search (if active)
        if self._mem0_instance:
            try:
                results = self._mem0_instance.search(goal, user_id="default_user", limit=3)
                if results and "results" in results:
                    mem_hits = results["results"]
                    if mem_hits:
                        lines.append("🧠 SEMANTIC MEM0 ASSOCIATIONS:")
                        for hit in mem_hits:
                            text = hit.get("memory") or hit.get("text", "")
                            if text:
                                lines.append(f"  • {text}")
                        lines.append("")
            except Exception:
                pass

        return "\n".join(lines).strip()
