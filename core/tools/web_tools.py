"""Web and Internet automation tools for Helper-AI."""
import os
import re
import urllib.parse
from typing import Any, Dict
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
            
            if max_characters and max_characters > 0 and len(clean_text) > max_characters:
                content = clean_text[:max_characters] + f"\n\n... [Content truncated at {max_characters} characters. Total page size: {len(clean_text)} characters]"
            else:
                content = clean_text

            headings_summary = "\n- ".join(extracted_headings[:15]) if extracted_headings else "None"
            links_summary = "\n".join(f"- {l['text']}: {l['url']}" for l in extracted_links[:35]) if extracted_links else "None"

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
