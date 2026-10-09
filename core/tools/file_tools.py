"""File System management tools for Helper-AI with user-friendly path resolution."""
import os
import shutil
import glob
from pathlib import Path
from typing import Any, Dict, List
from core.tools.base import BaseTool

def resolve_user_path(path_str: str) -> Path:
    """
    Expands user-friendly shortcuts like 'Desktop', 'Downloads', 'Documents', '~'
    into actual absolute paths on the user's operating system, accounting for OneDrive sync.
    """
    path_str = path_str.strip().strip('"').strip("'")
    home = Path.home()
    lower = path_str.lower()
    onedrive = home / "OneDrive"

    def get_known_folder(folder_name: str) -> Path:
        od_path = onedrive / folder_name
        std_path = home / folder_name
        # If OneDrive folder exists and has items, prioritize it
        if od_path.exists():
            try:
                if any(od_path.iterdir()):
                    return od_path
            except Exception:
                pass
        if std_path.exists():
            try:
                if any(std_path.iterdir()):
                    return std_path
            except Exception:
                pass
        if od_path.exists():
            return od_path
        return std_path

    if lower in ["desktop", "my desktop"]:
        return get_known_folder("Desktop")
    elif lower in ["downloads", "my downloads"]:
        return home / "Downloads"
    elif lower in ["documents", "my documents"]:
        return get_known_folder("Documents")
    elif lower in ["pictures", "my pictures"]:
        return get_known_folder("Pictures")
    elif lower in ["music"]:
        return home / "Music"
    elif lower in ["videos"]:
        return home / "Videos"
    
    # Handle paths starting with Desktop/ or Downloads/
    for folder in ["desktop", "downloads", "documents", "pictures"]:
        prefix = folder + "/"
        prefix_win = folder + "\\"
        if lower.startswith(prefix) or lower.startswith(prefix_win):
            remainder = path_str[len(folder)+1:]
            base_dir = get_known_folder(folder.capitalize()) if folder != "downloads" else (home / "Downloads")
            return base_dir / remainder

    # Handle standard path expansion
    expanded = os.path.expanduser(os.path.expandvars(path_str))
    p = Path(expanded)

    # If the user passed explicit path e.g. C:\Users\DELL\Desktop and it's empty, check OneDrive Desktop
    if p.name.lower() in ["desktop", "documents", "pictures"] and p.exists() and p.is_dir():
        try:
            if not any(p.iterdir()):
                od_alt = onedrive / p.name.capitalize()
                if od_alt.exists() and any(od_alt.iterdir()):
                    return od_alt
        except Exception:
            pass

    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p


class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = (
        "List all files and subfolders in a folder. Supports shortcuts like 'Desktop', "
        "'Downloads', 'Documents', or relative and absolute paths."
    )
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Folder path to list (e.g., 'Desktop', 'Downloads', '.', or 'C:/Projects').",
                "default": "."
            },
            "include_hidden": {
                "type": "boolean",
                "description": "Whether to list hidden/system files (default false).",
                "default": False
            }
        },
        "required": []
    }

    def execute(self, path: str = ".", include_hidden: bool = False) -> Dict[str, Any]:
        try:
            target_path = resolve_user_path(path)
            if not target_path.exists():
                return {"success": False, "output": f"Directory not found: {target_path}"}
            if not target_path.is_dir():
                return {"success": False, "output": f"Path is a file, not a directory: {target_path}"}

            items = []
            for item in target_path.iterdir():
                if not include_hidden and item.name.startswith("."):
                    continue
                is_dir = item.is_dir()
                try:
                    size = item.stat().st_size if not is_dir else 0
                    size_str = f"{round(size / 1024, 1)} KB" if not is_dir else "<DIR>"
                except OSError:
                    size_str = "???"

                items.append({
                    "name": item.name,
                    "is_dir": is_dir,
                    "size": size_str
                })

            items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
            lines = [f"Contents of {target_path} ({len(items)} items):"]
            for it in items[:100]:
                prefix = "[DIR] " if it["is_dir"] else "      "
                lines.append(f"{prefix}{it['name']:<35} {it['size']}")
            if len(items) > 100:
                lines.append(f"... and {len(items) - 100} more items.")

            return {"success": True, "output": "\n".join(lines), "path": str(target_path)}
        except Exception as e:
            return {"success": False, "output": f"Error listing directory: {str(e)}", "error": str(e)}


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the text contents of a file. Supports line limits for large files."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path of the file to read (supports 'Desktop/file.txt', etc.)."
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum lines to read (default 500).",
                "default": 500
            }
        },
        "required": ["file_path"]
    }

    def execute(self, file_path: str, max_lines: int = 500) -> Dict[str, Any]:
        try:
            target = resolve_user_path(file_path)
            if not target.exists():
                return {"success": False, "output": f"File does not exist: {target}"}
            if target.is_dir():
                return {"success": False, "output": f"Path is a directory, not a file: {target}"}

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
                content = "".join([l for l in lines if l])
            
            return {
                "success": True,
                "output": content if content else "(File is empty)",
                "path": str(target)
            }
        except Exception as e:
            return {"success": False, "output": f"Error reading file: {str(e)}", "error": str(e)}


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Create a new file or overwrite an existing file with the provided content."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path where the file should be saved (e.g. 'Desktop/report.md', 'output.txt')."
            },
            "content": {
                "type": "string",
                "description": "The exact text content to write into the file."
            },
            "append": {
                "type": "boolean",
                "description": "If true, appends content instead of overwriting (default false).",
                "default": False
            }
        },
        "required": ["file_path", "content"]
    }

    def execute(self, file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
        try:
            target = resolve_user_path(file_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            with open(target, mode, encoding="utf-8") as f:
                f.write(content)

            verb = "appended to" if append else "written to"
            return {
                "success": True,
                "output": f"Successfully {verb} {target} ({len(content)} characters).",
                "path": str(target)
            }
        except Exception as e:
            return {"success": False, "output": f"Error writing file: {str(e)}", "error": str(e)}


class MoveOrCopyFileTool(BaseTool):
    name = "move_or_copy_file"
    description = "Move, rename, or copy files or directories."
    parameters = {
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Source file or directory path."},
            "destination": {"type": "string", "description": "Destination file or directory path."},
            "action": {
                "type": "string",
                "enum": ["move", "copy"],
                "description": "'move' to move/rename, 'copy' to duplicate.",
                "default": "move"
            }
        },
        "required": ["source", "destination"]
    }

    def execute(self, source: str, destination: str, action: str = "move") -> Dict[str, Any]:
        try:
            src = resolve_user_path(source)
            dst = resolve_user_path(destination)
            if not src.exists():
                return {"success": False, "output": f"Source does not exist: {src}"}

            if action == "copy":
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                return {"success": True, "output": f"Copied {src} to {dst}"}
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src, dst)
                return {"success": True, "output": f"Moved {src} to {dst}"}
        except Exception as e:
            return {"success": False, "output": f"Error in file operation: {str(e)}", "error": str(e)}


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files by pattern (e.g., '*.pdf', '*invoice*', '*.xlsx') in a directory."
    parameters = {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to search in (e.g., 'Downloads', 'Desktop', '.').",
                "default": "."
            },
            "pattern": {
                "type": "string",
                "description": "Filename pattern to match (e.g. '*.pdf', '*notes*', '*.jpg').",
                "default": "*"
            },
            "recursive": {
                "type": "boolean",
                "description": "Search subfolders recursively (default true).",
                "default": True
            }
        },
        "required": ["pattern"]
    }

    def execute(self, pattern: str, directory: str = ".", recursive: bool = True) -> Dict[str, Any]:
        try:
            base = resolve_user_path(directory)
            if not base.exists():
                return {"success": False, "output": f"Directory not found: {base}"}

            search_pattern = f"{base}/**/{pattern}" if recursive else f"{base}/{pattern}"
            matches = glob.glob(search_pattern, recursive=recursive)

            if not matches:
                return {"success": True, "output": f"No files found matching '{pattern}' in {base}"}

            lines = [f"Found {len(matches)} matches for '{pattern}' in {base}:"]
            for m in matches[:50]:
                lines.append(f"  - {m}")
            if len(matches) > 50:
                lines.append(f"... and {len(matches) - 50} more matches.")

            return {"success": True, "output": "\n".join(lines), "matches": matches[:50]}
        except Exception as e:
            return {"success": False, "output": f"Error searching files: {str(e)}", "error": str(e)}
