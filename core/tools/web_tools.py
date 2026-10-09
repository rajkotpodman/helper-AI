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
        # Attempt 1: duckduckgo_search package if available
        try:
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
                            results.append({
                                "title": t_elem.get_text(strip=True),
                                "snippet": s_elem.get_text(strip=True),
                                "url": a_elem.get("href", "") if a_elem else ""
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
                "default": 4000
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, max_characters: int = 4000) -> Dict[str, Any]:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()

            if BeautifulSoup:
                soup = BeautifulSoup(resp.text, "html.parser")
                for s in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    s.extract()
                text = soup.get_text(separator="\n")
                title = soup.title.string.strip() if soup.title and soup.title.string else url
            else:
                # Regex fallback for pure python without bs4
                cleaned = re.sub(r"<(script|style).*?</\1>", "", resp.text, flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", cleaned)
                title_match = re.search(r"<title>(.*?)</title>", resp.text, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else url

            return {
                "success": True,
                "title": title,
                "output": f"Title: {title}\nURL: {url}\n\n{truncated}"
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Failed to fetch webpage content: {str(e)}",
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
