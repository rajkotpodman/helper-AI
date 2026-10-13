"""Web and Internet automation tools for Helper-AI."""
import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional
import requests
from core.tools.base import BaseTool
from core.tools.file_tools import resolve_user_path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Shared connection pool session for high-speed web scraping
_web_session = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    _adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=Retry(total=2, backoff_factor=0.3))
    _web_session.mount("https://", _adapter)
    _web_session.mount("http://", _adapter)
except Exception:
    pass

class SearchWebTool(BaseTool):
    name = "search_web"
    description = (
        "Search the internet for real-time information, documentation, news, or guides. "
        "Returns search result titles, snippets, and links without requiring any paid API key."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            },
            "max_results": {
                "type": "integer",
                "description": "Number of results to retrieve (default 5).",
                "default": 5
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        results = []
        # Attempt 1: ddgs / duckduckgo_search package if available
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results))
                for item in raw:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("body", ""),
                        "url": item.get("href", "")
                    })
        except Exception:
            # Attempt 2: Fallback to DuckDuckGo HTML search
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                resp = requests.get(url, headers=HEADERS, timeout=12)
                if BeautifulSoup:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for r in soup.select(".result"):
                        title_elem = r.select_one(".result__title")
                        snippet_elem = r.select_one(".result__snippet")
                        url_elem = r.select_one(".result__url")
                        
                        if title_elem and snippet_elem:
                            link = url_elem.get_text(strip=True) if url_elem else ""
                            if not link.startswith("http"):
                                link = f"https://{link}"
                            results.append({
                                "title": title_elem.get_text(strip=True),
                                "snippet": snippet_elem.get_text(strip=True),
                                "url": link
                            })
                            if len(results) >= max_results:
                                break
                else:
                    # Regex fallback for links
                    matches = re.findall(r'<a class="result__snippet[^>]*href="([^"]+)"[^>]*>(.*?)</a>', resp.text)
                    for m_link, m_snippet in matches[:max_results]:
                        clean_snip = re.sub(r'<[^>]+>', '', m_snippet)
                        results.append({
                            "title": "Search Result",
                            "snippet": clean_snip,
                            "url": m_link
                        })
            except Exception:
                pass

        # Attempt 3: High-reliability Bing fallback
        if not results:
            try:
                b_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
                b_resp = requests.get(b_url, headers=HEADERS, timeout=8)
                if b_resp.status_code == 200 and BeautifulSoup:
                    soup = BeautifulSoup(b_resp.text, "html.parser")
                    for card in soup.select("li.b_algo"):
                        t_elem = card.select_one("h2")
                        s_elem = card.select_one(".b_caption p") or card.select_one(".b_caption")
                        a_elem = card.select_one("h2 a")
                        if t_elem and s_elem:
                            raw_url = a_elem.get("href", "") if a_elem else ""
                            # Unwrap Bing click redirect (u=a1<base64>) to real destination URL
                            real_url = raw_url
                            u_match = re.search(r"[?&]u=a1([a-zA-Z0-9+/=_-]+)", raw_url)
                            if u_match:
                                import base64
                                b64 = u_match.group(1).replace("-", "+").replace("_", "/")
                                b64 += "=" * ((4 - len(b64) % 4) % 4)
                                try:
                                    real_url = base64.b64decode(b64).decode("utf-8", errors="ignore")
                                except Exception:
                                    pass

                            results.append({
                                "title": t_elem.get_text(strip=True),
                                "snippet": s_elem.get_text(strip=True),
                                "url": real_url
                            })
                            if len(results) >= max_results:
                                break
            except Exception:
                pass

        if not results:
            return {
                "success": True,
                "output": f"No web search results found for query: '{query}'. Try different keywords."
            }

        lines = [f"Web Search Results for '{query}':"]
        for idx, item in enumerate(results, start=1):
            lines.append(f"\n[{idx}] {item['title']}")
            lines.append(f"    URL: {item['url']}")
            lines.append(f"    Snippet: {item['snippet']}")

        return {
            "success": True,
            "output": "\n".join(lines),
            "results": results
        }


class FetchWebContentTool(BaseTool):
    name = "fetch_web_content"
    description = (
        "Fetch and read the contents of any webpage or public URL. "
        "Extracts readable article text, removing HTML noise and advertisements."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Full URL of the webpage to read (e.g. https://en.wikipedia.org/...)."
            },
            "max_characters": {
                "type": "integer",
                "description": "Maximum characters of text to return (default 4000).",
                "default": 10000
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, max_characters: int = 15000) -> Dict[str, Any]:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()

            resp_headers = getattr(resp, "headers", {}) or {}
            content_type = str(resp_headers.get("Content-Type", "")).lower()

            # 1. Handle JSON APIs (e.g. GitHub API, REST endpoints, JSON catalogs)
            if ("application/json" in content_type or url.endswith(".json") or "/api." in url or "/api/" in url) and hasattr(resp, "json"):
                try:
                    data = resp.json()
                    if isinstance(data, list):
                        lines = [f"🌐 API Endpoint: {url} (Total Items: {len(data)})"]
                        for idx, item in enumerate(data, start=1):
                            if isinstance(item, dict):
                                name = item.get("name") or item.get("full_name") or item.get("title") or item.get("id") or f"Item {idx}"
                                desc = item.get("description") or item.get("summary") or item.get("body") or ""
                                link = item.get("html_url") or item.get("url") or item.get("link") or ""
                                is_priv = item.get("private")
                                priv_str = "Private" if is_priv is True else ("Public" if is_priv is False else "")
                                extra = f" [{priv_str}]" if priv_str else ""
                                lang = f" | Lang: {item.get('language')}" if item.get("language") else ""
                                stars = f" | ⭐ {item.get('stargazers_count')}" if item.get("stargazers_count") is not None else ""
                                desc_str = f" - {desc}" if desc else ""
                                link_str = f" ({link})" if link else ""
                                lines.append(f"{idx}. {name}{extra}{desc_str}{link_str}{lang}{stars}")
                            else:
                                lines.append(f"{idx}. {str(item)}")
                        formatted_output = "\n".join(lines)
                        return {
                            "success": True,
                            "title": f"API JSON Response ({len(data)} items)",
                            "url": url,
                            "items_count": len(data),
                            "content": formatted_output,
                            "output": formatted_output
                        }
                    elif isinstance(data, dict):
                        import json
                        formatted_output = f"🌐 API JSON Object from {url}:\n\n" + json.dumps(data, indent=2)[:max_characters]
                        return {
                            "success": True,
                            "title": "API JSON Object",
                            "url": url,
                            "content": formatted_output,
                            "output": formatted_output
                        }
                except Exception:
                    pass

            # 2. Handle HTML Webpages
            extracted_links = []
            extracted_headings = []

            if BeautifulSoup:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Extract headings
                for h in soup.find_all(["h1", "h2", "h3"]):
                    htxt = h.get_text(strip=True)
                    if htxt and htxt not in extracted_headings:
                        extracted_headings.append(htxt)

                # Extract links (e.g. repository links, documentation, articles)
                for a in soup.find_all("a", href=True):
                    atxt = a.get_text(strip=True)
                    ahref = a["href"]
                    if atxt and ahref and len(atxt) < 80:
                        full_link = urllib.parse.urljoin(url, ahref)
                        if not any(l["url"] == full_link for l in extracted_links):
                            extracted_links.append({"text": atxt, "url": full_link})
                            if len(extracted_links) >= 60:
                                break

                for s in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                    s.extract()
                text = soup.get_text(separator="\n")
                title = soup.title.string.strip() if soup.title and soup.title.string else url
            else:
                # Regex fallback for pure python without bs4
                cleaned = re.sub(r"<(script|style).*?</\1>", "", resp.text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", cleaned)
                title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else url

            # Clean and normalize whitespace
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            clean_text = "\n".join(lines)

            # If static content is abnormally short (< 250 chars) or detected as JS-only shell, attempt dynamic browser fallback
            if len(clean_text) < 250 or "enable javascript" in clean_text.lower() or "javascript is required" in clean_text.lower():
                try:
                    from core.browser_driver import BrowserDriver
                    driver = BrowserDriver.get_instance().get_driver()
                    if driver:
                        driver.get(url)
                        import time
                        time.sleep(2.0)
                        dyn_html = driver.page_source
                        if BeautifulSoup and dyn_html and len(dyn_html) > len(resp.text):
                            soup_dyn = BeautifulSoup(dyn_html, "html.parser")
                            for s in soup_dyn(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                                s.extract()
                            dyn_lines = [l.strip() for l in soup_dyn.get_text(separator="\n").splitlines() if l.strip()]
                            dyn_text = "\n".join(dyn_lines)
                            if len(dyn_text) > len(clean_text):
                                clean_text = dyn_text
                except Exception:
                    pass
            
            if max_characters and max_characters > 0 and len(clean_text) > max_characters:
                content = clean_text[:max_characters] + f"\n\n... [Content truncated at {max_characters} characters. Total page size: {len(clean_text)} characters]"
            else:
                content = clean_text

            headings_summary = "\n- ".join(extracted_headings[:20]) if extracted_headings else "None"
            links_summary = "\n".join(f"- {l['text']}: {l['url']}" for l in extracted_links[:40]) if extracted_links else "None"

            return {
                "success": True,
                "title": title,
                "url": url,
                "total_characters": len(clean_text),
                "headings": extracted_headings[:25],
                "links": extracted_links[:60],
                "content": clean_text,
                "output": (
                    f"🌐 Webpage: '{title}'\nURL: {url} ({len(clean_text)} total characters)\n\n"
                    f"### Key Headings:\n- {headings_summary}\n\n"
                    f"### Page Content:\n{content}\n\n"
                    f"### Discovered Links ({len(extracted_links)} total):\n{links_summary}"
                )
            }
        except Exception as e:
            # Automatic Dynamic Browser Fallback on HTTP errors (e.g. 403 Forbidden / Cloudflare)
            try:
                from core.browser_driver import BrowserDriver
                driver = BrowserDriver.get_instance().get_driver()
                if driver:
                    driver.get(url)
                    import time
                    time.sleep(2.5)
                    dyn_html = driver.page_source
                    dyn_title = driver.title or url
                    if BeautifulSoup and dyn_html:
                        soup_dyn = BeautifulSoup(dyn_html, "html.parser")
                        for s in soup_dyn(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                            s.extract()
                        dyn_lines = [l.strip() for l in soup_dyn.get_text(separator="\n").splitlines() if l.strip()]
                        dyn_text = "\n".join(dyn_lines)
                        if len(dyn_text) > 100:
                            content = dyn_text[:max_characters] if (max_characters and len(dyn_text) > max_characters) else dyn_text
                            return {
                                "success": True,
                                "title": dyn_title,
                                "url": url,
                                "total_characters": len(dyn_text),
                                "content": dyn_text,
                                "output": f"🌐 Webpage (Dynamic Browser Rendered): '{dyn_title}'\nURL: {url} ({len(dyn_text)} characters)\n\n{content}"
                            }
            except Exception:
                pass

            return {
                "success": False,
                "output": f"Failed to fetch webpage content from {url}: {str(e)}",
                "error": str(e)
            }


class DownloadFileTool(BaseTool):
    name = "download_file"
    description = "Download a file from an internet URL directly to the user's computer."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Direct download URL of the file."
            },
            "destination_path": {
                "type": "string",
                "description": "Path where to save the file (e.g. 'Downloads/setup.exe', 'Desktop/data.csv')."
            }
        },
        "required": ["url", "destination_path"]
    }

    def execute(self, url: str, destination_path: str) -> Dict[str, Any]:
        try:
            target = resolve_user_path(destination_path)
            target.parent.mkdir(parents=True, exist_ok=True)

            resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
            resp.raise_for_status()

            total_bytes = 0
            with open(target, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_bytes += len(chunk)

            size_mb = round(total_bytes / (1024 * 1024), 2)
            return {
                "success": True,
                "output": f"Successfully downloaded file to {target} ({size_mb} MB).",
                "path": str(target),
                "size_mb": size_mb
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Failed to download file from {url}: {str(e)}",
                "error": str(e)
            }


class DeepWebCrawlerTool(BaseTool):
    name = "deep_web_crawl"
    description = (
        "Recursively crawl a website, documentation portal, or article knowledge base. "
        "Discovers child pages, extracts clean readable content across multiple pages, "
        "and compiles an exhaustive knowledge dossier or saves to a local markdown file."
    )
    parameters = {
        "type": "object",
        "properties": {
            "start_url": {
                "type": "string",
                "description": "The root URL to start crawling from."
            },
            "max_pages": {
                "type": "integer",
                "description": "Maximum number of pages to crawl (default 6, up to 25).",
                "default": 6
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum link depth to traverse (1 = start page + direct links, default 1).",
                "default": 1
            },
            "same_domain": {
                "type": "boolean",
                "description": "Stay within the same domain/host (default True).",
                "default": True
            },
            "save_to_path": {
                "type": "string",
                "description": "Optional file path to save the full compiled dossier (e.g. 'Desktop/crawled_docs.md')."
            }
        },
        "required": ["start_url"]
    }

    def execute(
        self,
        start_url: str,
        max_pages: int = 6,
        max_depth: int = 1,
        same_domain: bool = True,
        save_to_path: str = None
    ) -> Dict[str, Any]:
        from collections import deque
        import urllib.parse

        if not start_url.startswith("http://") and not start_url.startswith("https://"):
            start_url = "https://" + start_url

        parsed_start = urllib.parse.urlparse(start_url)
        base_netloc = parsed_start.netloc.lower()

        queue = deque([(start_url, 0)])
        visited = set()
        crawled_pages = []
        all_discovered_links = set()

        max_pages = min(max(1, max_pages), 25)
        max_depth = min(max(0, max_depth), 3)

        while queue and len(crawled_pages) < max_pages:
            current_url, depth = queue.popleft()
            if current_url in visited:
                continue
            visited.add(current_url)

            try:
                resp = _web_session.get(current_url, headers=HEADERS, timeout=12)
                if resp.status_code != 200:
                    continue

                page_title = current_url
                page_text = ""
                extracted_headings = []
                child_links = []

                if BeautifulSoup:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    if soup.title and soup.title.string:
                        page_title = soup.title.string.strip()

                    for h in soup.find_all(["h1", "h2", "h3"]):
                        htxt = h.get_text(strip=True)
                        if htxt and htxt not in extracted_headings:
                            extracted_headings.append(htxt)

                    for a in soup.find_all("a", href=True):
                        href = a["href"].strip()
                        if href and not href.startswith("javascript:") and not href.startswith("mailto:") and not href.startswith("#"):
                            full_u = urllib.parse.urljoin(current_url, href)
                            # Remove hash fragments
                            full_u = urllib.parse.urldefrag(full_u)[0]
                            all_discovered_links.add(full_u)
                            child_links.append(full_u)

                    for s in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                        s.extract()
                    lines = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]
                    page_text = "\n".join(lines)
                else:
                    lines = [l.strip() for l in resp.text.splitlines() if l.strip()]
                    page_text = "\n".join(lines[:200])

                crawled_pages.append({
                    "url": current_url,
                    "title": page_title,
                    "depth": depth,
                    "headings": extracted_headings[:15],
                    "content": page_text[:12000],
                    "char_count": len(page_text)
                })

                # Queue child links if within depth
                if depth < max_depth:
                    for cl in child_links:
                        if cl not in visited:
                            cl_netloc = urllib.parse.urlparse(cl).netloc.lower()
                            if same_domain and cl_netloc != base_netloc:
                                continue
                            queue.append((cl, depth + 1))

            except Exception:
                continue

        if not crawled_pages:
            return {
                "success": False,
                "output": f"Failed to crawl any valid pages from {start_url}.",
                "error": "NoPagesCrawled"
            }

        # Build comprehensive markdown dossier
        dossier_lines = [
            f"# 📚 Comprehensive Web Crawl Dossier: {start_url}",
            f"- **Pages Crawled:** {len(crawled_pages)}",
            f"- **Total Discovered Links:** {len(all_discovered_links)}",
            f"- **Root Domain:** {base_netloc}",
            "\n## 📋 Table of Contents"
        ]
        for idx, page in enumerate(crawled_pages, start=1):
            dossier_lines.append(f"{idx}. [{page['title']}]({page['url']}) ({page['char_count']} chars, Depth {page['depth']})")

        dossier_lines.append("\n---\n")

        for idx, page in enumerate(crawled_pages, start=1):
            dossier_lines.append(f"## Page {idx}: {page['title']}")
            dossier_lines.append(f"**URL:** {page['url']} | **Depth:** {page['depth']}")
            if page['headings']:
                dossier_lines.append(f"**Key Headings:** {', '.join(page['headings'][:8])}\n")
            dossier_lines.append(page['content'])
            dossier_lines.append("\n---\n")

        full_dossier = "\n".join(dossier_lines)

        saved_path_str = None
        if save_to_path:
            try:
                dest = resolve_user_path(save_to_path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(full_dossier)
                saved_path_str = str(dest)
            except Exception as se:
                saved_path_str = f"Error saving file: {se}"

        summary_preview = full_dossier[:16000]
        if len(full_dossier) > 16000:
            summary_preview += f"\n\n... [Dossier continued; total {len(full_dossier)} characters across {len(crawled_pages)} pages]"

        output_msg = f"🌐 Deep Crawl Completed Successfully! Crawled {len(crawled_pages)} pages from {start_url}."
        if saved_path_str:
            output_msg += f"\n📁 Complete knowledge dossier saved to: {saved_path_str}"
        output_msg += f"\n\n{summary_preview}"

        return {
            "success": True,
            "pages_crawled": len(crawled_pages),
            "total_links_discovered": len(all_discovered_links),
            "saved_to": saved_path_str,
            "dossier": full_dossier,
            "output": output_msg
        }


class BatchWebFetchTool(BaseTool):
    name = "batch_fetch_web"
    description = (
        "Concurrently fetch multiple web pages or search results in parallel. "
        "Combines all pages into a structured multi-source research dossier."
    )
    parameters = {
        "type": "object",
        "properties": {
            "urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of URLs to fetch concurrently."
            },
            "max_characters_per_url": {
                "type": "integer",
                "description": "Character limit per page (default 8000).",
                "default": 8000
            }
        },
        "required": ["urls"]
    }

    def execute(self, urls: List[str], max_characters_per_url: int = 8000) -> Dict[str, Any]:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        if not urls:
            return {"success": False, "output": "No URLs provided to batch fetch.", "error": "EmptyUrls"}

        results = []

        def _fetch_single(u: str) -> Dict[str, Any]:
            try:
                target_u = u if u.startswith("http") else f"https://{u}"
                resp = _web_session.get(target_u, headers=HEADERS, timeout=12)
                if resp.status_code != 200:
                    return {"url": target_u, "success": False, "error": f"HTTP {resp.status_code}"}

                title = target_u
                if BeautifulSoup:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()
                    for s in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                        s.extract()
                    lines = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]
                    text = "\n".join(lines)
                else:
                    text = resp.text

                return {
                    "url": target_u,
                    "title": title,
                    "success": True,
                    "content": text[:max_characters_per_url],
                    "total_chars": len(text)
                }
            except Exception as e:
                return {"url": u, "success": False, "error": str(e)}

        with ThreadPoolExecutor(max_workers=min(len(urls), 8)) as executor:
            futures = {executor.submit(_fetch_single, u): u for u in urls[:12]}
            for fut in as_completed(futures):
                results.append(fut.result())

        successful = [r for r in results if r.get("success")]
        lines = [f"🌐 Batch Fetch Results ({len(successful)}/{len(results)} successful):\n"]
        for idx, r in enumerate(successful, start=1):
            lines.append(f"### [{idx}] {r['title']}")
            lines.append(f"**URL:** {r['url']} ({r.get('total_chars', 0)} characters)")
            lines.append(r.get("content", ""))
            lines.append("\n" + "=" * 40 + "\n")

        for r in results:
            if not r.get("success"):
                lines.append(f"❌ Failed to fetch {r['url']}: {r.get('error')}")

        output_str = "\n".join(lines)
        return {
            "success": len(successful) > 0,
            "total_requested": len(urls),
            "successful_count": len(successful),
            "results": results,
            "output": output_str
        }


class FetchGitHubRepoTool(BaseTool):
    name = "fetch_github_repo"
    description = (
        "Deeply inspect, search, and fetch entire codebases, file trees, or raw source files "
        "from any public GitHub repository (e.g. 'rajkotpodman/helper-AI') without truncation."
    )
    parameters = {
        "type": "object",
        "properties": {
            "repo": {
                "type": "string",
                "description": "Repository identifier e.g. 'owner/repo' (or full GitHub URL)."
            },
            "action": {
                "type": "string",
                "enum": ["overview", "tree", "file", "readme", "releases"],
                "description": "Action: 'overview' (metadata & stats), 'tree' (full file tree), 'file' (read exact file), 'readme' (get README), 'releases' (latest releases).",
                "default": "overview"
            },
            "file_path": {
                "type": "string",
                "description": "Path to file inside repository (required when action is 'file', e.g. 'core/agent.py' or 'package.json')."
            },
            "branch": {
                "type": "string",
                "description": "Branch name (default 'main').",
                "default": "main"
            }
        },
        "required": ["repo"]
    }

    def execute(self, repo: str, action: str = "overview", file_path: str = None, branch: str = "main") -> Dict[str, Any]:
        import re

        clean_repo = repo.strip()
        # Extract owner/repo if full URL was passed
        url_match = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git|/|$)", clean_repo)
        if url_match:
            clean_repo = url_match.group(1)
        clean_repo = clean_repo.strip("/")

        if "/" not in clean_repo:
            return {"success": False, "output": f"Invalid repository format '{repo}'. Expected 'owner/repo' e.g. 'rajkotpodman/helper-AI'.", "error": "InvalidRepo"}

        owner, repo_name = clean_repo.split("/", 1)
        repo_name = repo_name.replace(".git", "")

        try:
            if action == "readme":
                # Direct raw fetch for README
                for cand_file in ["README.md", "readme.md", "README", "Readme.md"]:
                    raw_u = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{cand_file}"
                    r = _web_session.get(raw_u, headers=HEADERS, timeout=12)
                    if r.status_code == 200:
                        return {
                            "success": True,
                            "repo": clean_repo,
                            "branch": branch,
                            "file": cand_file,
                            "content": r.text,
                            "output": f"📖 README for {clean_repo} ({len(r.text)} characters):\n\n{r.text}"
                        }
                # Fallback to master branch
                for cand_file in ["README.md", "readme.md"]:
                    raw_u = f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/{cand_file}"
                    r = _web_session.get(raw_u, headers=HEADERS, timeout=12)
                    if r.status_code == 200:
                        return {
                            "success": True,
                            "repo": clean_repo,
                            "branch": "master",
                            "file": cand_file,
                            "content": r.text,
                            "output": f"📖 README for {clean_repo} ({len(r.text)} characters):\n\n{r.text}"
                        }

            elif action == "file":
                if not file_path:
                    return {"success": False, "output": "Parameter 'file_path' is required when action is 'file'.", "error": "MissingFilePath"}

                clean_path = file_path.strip().lstrip("/")
                raw_u = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/{clean_path}"
                r = _web_session.get(raw_u, headers=HEADERS, timeout=15)
                if r.status_code == 200:
                    return {
                        "success": True,
                        "repo": clean_repo,
                        "branch": branch,
                        "file_path": clean_path,
                        "content": r.text,
                        "output": f"📄 File '{clean_path}' from {clean_repo} ({len(r.text)} characters):\n\n{r.text}"
                    }
                # Try master branch
                raw_u_master = f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/{clean_path}"
                r_m = _web_session.get(raw_u_master, headers=HEADERS, timeout=15)
                if r_m.status_code == 200:
                    return {
                        "success": True,
                        "repo": clean_repo,
                        "branch": "master",
                        "file_path": clean_path,
                        "content": r_m.text,
                        "output": f"📄 File '{clean_path}' from {clean_repo} ({len(r_m.text)} characters):\n\n{r_m.text}"
                    }
                return {"success": False, "output": f"Could not find file '{clean_path}' in {clean_repo} (HTTP {r.status_code}).", "error": "FileNotFound"}

            elif action == "tree":
                api_u = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/{branch}?recursive=1"
                r = _web_session.get(api_u, headers=HEADERS, timeout=15)
                if r.status_code != 200:
                    # Try master branch
                    api_u = f"https://api.github.com/repos/{owner}/{repo_name}/git/trees/master?recursive=1"
                    r = _web_session.get(api_u, headers=HEADERS, timeout=15)

                if r.status_code == 200:
                    tree_data = r.json().get("tree", [])
                    files = [item["path"] for item in tree_data if item.get("type") == "blob"]
                    dirs = [item["path"] for item in tree_data if item.get("type") == "tree"]
                    lines = [f"🌲 File Tree for {clean_repo} (Total Files: {len(files)}, Directories: {len(dirs)}):"]
                    for f in files[:80]:
                        lines.append(f"  📄 {f}")
                    if len(files) > 80:
                        lines.append(f"  ... and {len(files) - 80} more files.")

                    return {
                        "success": True,
                        "repo": clean_repo,
                        "total_files": len(files),
                        "files": files,
                        "directories": dirs,
                        "output": "\n".join(lines)
                    }

            elif action == "releases":
                api_u = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
                r = _web_session.get(api_u, headers=HEADERS, timeout=12)
                if r.status_code == 200:
                    releases = r.json()
                    lines = [f"🚀 Releases for {clean_repo} (Total: {len(releases)}):"]
                    for rel in releases[:5]:
                        tag = rel.get("tag_name", "")
                        name = rel.get("name", "")
                        date = rel.get("published_at", "")[:10]
                        lines.append(f"\n- **{tag}** ({name}) - {date}")
                        body = rel.get("body", "")
                        if body:
                            lines.append(f"  {body[:300]}...")
                    return {"success": True, "repo": clean_repo, "releases": releases[:5], "output": "\n".join(lines)}

            # Default: overview
            api_u = f"https://api.github.com/repos/{owner}/{repo_name}"
            r = _web_session.get(api_u, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                data = r.json()
                summary_lines = [
                    f"⭐ GitHub Repository: {data.get('full_name')}",
                    f"Description: {data.get('description') or 'No description'}",
                    f"Language: {data.get('language') or 'N/A'}",
                    f"Stars: {data.get('stargazers_count')} | Forks: {data.get('forks_count')} | Open Issues: {data.get('open_issues_count')}",
                    f"Default Branch: {data.get('default_branch')}",
                    f"License: {data.get('license', {}).get('name') if data.get('license') else 'None'}",
                    f"URL: {data.get('html_url')}"
                ]
                return {
                    "success": True,
                    "repo": clean_repo,
                    "metadata": data,
                    "output": "\n".join(summary_lines)
                }
            else:
                return {"success": False, "output": f"Could not fetch repository overview for {clean_repo} (HTTP {r.status_code}).", "error": f"HTTP {r.status_code}"}

        except Exception as e:
            return {"success": False, "output": f"GitHub API error for {clean_repo}: {str(e)}", "error": str(e)}

