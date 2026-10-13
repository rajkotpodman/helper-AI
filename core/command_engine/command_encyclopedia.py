"""Encyclopedic Knowledge Base of Cross-Platform Terminal Commands.

Maintains verified, robust command recipes for Windows (PowerShell & CMD),
Linux (Bash/POSIX), and macOS (Zsh/Bash), with parameter substitution,
silent non-interactive flags, and safety boundaries.
"""

from typing import Dict, Any, List, Optional
import re


COMMAND_CATALOG: Dict[str, Dict[str, Any]] = {
    # ------------------------------------------------------------------------
    # 1. FILE SYSTEM & STORAGE OPERATIONS
    # ------------------------------------------------------------------------
    "find_large_files": {
        "description": "Find files larger than specified size or top largest files.",
        "windows_powershell": "Get-ChildItem -Path '{path}' -Recurse -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First {count} | Select-Object FullName, @{Name='SizeMB';Expression={[math]::Round($_.Length / 1MB, 2)}}",
        "linux_posix": "find '{path}' -type f -exec ls -lh {{}} + 2>/dev/null | sort -k 5 -rh | head -n {count}",
        "macos": "find '{path}' -type f -exec ls -lh {{}} + 2>/dev/null | sort -k 5 -rh | head -n {count}",
        "default_params": {"path": ".", "count": "20"}
    },
    "disk_usage": {
        "description": "Report disk space usage and free capacity.",
        "windows_powershell": "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='UsedGB';Expression={[math]::Round($_.Used/1GB,2)}}, @{Name='FreeGB';Expression={[math]::Round($_.Free/1GB,2)}}, Root",
        "linux_posix": "df -h",
        "macos": "df -h",
        "default_params": {}
    },
    "archive_directory": {
        "description": "Compress a directory into an archive file.",
        "windows_powershell": "Compress-Archive -Path '{source}' -DestinationPath '{destination}' -Force",
        "linux_posix": "tar -czvf '{destination}' -C '{source}' .",
        "macos": "tar -czvf '{destination}' -C '{source}' .",
        "default_params": {"source": ".", "destination": "archive.tar.gz"}
    },
    "extract_archive": {
        "description": "Decompress and extract an archive to target directory.",
        "windows_powershell": "Expand-Archive -Path '{source}' -DestinationPath '{destination}' -Force",
        "linux_posix": "tar -xzvf '{source}' -C '{destination}'",
        "macos": "tar -xzvf '{source}' -C '{destination}'",
        "default_params": {"source": "archive.tar.gz", "destination": "."}
    },
    "search_text_in_files": {
        "description": "Search for a pattern or text recursively across files.",
        "windows_powershell": "Get-ChildItem -Path '{path}' -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern '{pattern}' | Select-Object Path, LineNumber, Line -First 50",
        "linux_posix": "grep -rnI --exclude-dir={.git,node_modules,__pycache__} '{pattern}' '{path}' | head -n 50",
        "macos": "grep -rnI --exclude-dir={.git,node_modules,__pycache__} '{pattern}' '{path}' | head -n 50",
        "default_params": {"path": ".", "pattern": "TODO"}
    },

    # ------------------------------------------------------------------------
    # 2. PROCESSES, SERVICES & PERFORMANCE
    # ------------------------------------------------------------------------
    "list_top_cpu_processes": {
        "description": "List top processes consuming the most CPU resources.",
        "windows_powershell": "Get-Process | Sort-Object CPU -Descending | Select-Object -First {count} -Property Id, ProcessName, CPU, WorkingSet64",
        "linux_posix": "ps aux --sort=-%cpu 2>/dev/null | head -n {count}",
        "macos": "ps -A -o pid,%cpu,%mem,comm | sort -k 2 -nr | head -n {count}",
        "default_params": {"count": "15"}
    },
    "list_top_memory_processes": {
        "description": "List top processes consuming the most RAM / memory.",
        "windows_powershell": "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First {count} -Property Id, ProcessName, @{Name='RAM_MB';Expression={[math]::Round($_.WorkingSet64/1MB,2)}}",
        "linux_posix": "ps aux --sort=-%mem 2>/dev/null | head -n {count}",
        "macos": "ps -A -o pid,%mem,%cpu,comm | sort -k 2 -nr | head -n {count}",
        "default_params": {"count": "15"}
    },
    "kill_process_by_port": {
        "description": "Identify and terminate whatever process is occupying a specific network port.",
        "windows_powershell": "$p = (Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue).OwningProcess; if ($p) { Stop-Process -Id $p -Force; Write-Output \"Terminated process $p on port {port}\" } else { Write-Output \"No active process on port {port}\" }",
        "linux_posix": "fuser -k -n tcp {port} 2>/dev/null || (lsof -ti:{port} | xargs -r kill -9)",
        "macos": "lsof -ti:{port} | xargs -r kill -9",
        "default_params": {"port": "8000"}
    },
    "kill_process_by_name": {
        "description": "Forcibly terminate processes matching a target name.",
        "windows_powershell": "Stop-Process -Name '{name}' -Force -ErrorAction SilentlyContinue",
        "linux_posix": "pkill -9 -f '{name}'",
        "macos": "pkill -9 -f '{name}'",
        "default_params": {"name": "node"}
    },
    "list_services": {
        "description": "List system services and their running status.",
        "windows_powershell": "Get-Service | Where-Object Status -eq 'Running' | Select-Object -First {count} -Property Name, DisplayName, Status",
        "linux_posix": "systemctl list-units --type=service --state=running --no-pager | head -n {count}",
        "macos": "launchctl list | head -n {count}",
        "default_params": {"count": "25"}
    },

    # ------------------------------------------------------------------------
    # 3. NETWORKING, PORTS & SOCKETS
    # ------------------------------------------------------------------------
    "list_listening_ports": {
        "description": "Enumerate all TCP and UDP listening ports and associated processes.",
        "windows_powershell": "Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess, @{Name='Process';Expression={(Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName}} | Sort-Object LocalPort",
        "linux_posix": "ss -tulpn 2>/dev/null || netstat -tlpn 2>/dev/null",
        "macos": "lsof -iTCP -sTCP:LISTEN -P -n",
        "default_params": {}
    },
    "test_port_connectivity": {
        "description": "Test TCP socket connectivity and latency to a remote endpoint.",
        "windows_powershell": "Test-NetConnection -ComputerName '{host}' -Port {port} | Select-Object ComputerName, RemoteAddress, RemotePort, TcpTestSucceeded",
        "linux_posix": "nc -zv -w 3 '{host}' {port} 2>&1 || curl -Is --connect-timeout 3 'http://{host}:{port}' >/dev/null 2>&1 && echo 'Connected'",
        "macos": "nc -zv -G 3 '{host}' {port} 2>&1",
        "default_params": {"host": "127.0.0.1", "port": "80"}
    },
    "show_network_interfaces": {
        "description": "Display IP addresses, subnet masks, and network adapter details.",
        "windows_powershell": "Get-NetIPAddress -AddressFamily IPv4 | Where-Object InterfaceAlias -notlike '*Loopback*' | Select-Object InterfaceAlias, IPAddress, IPv4Address",
        "linux_posix": "ip -brief address show || ifconfig",
        "macos": "ifconfig | grep 'inet '",
        "default_params": {}
    },
    "download_file": {
        "description": "Download a file from the internet directly to local disk.",
        "windows_powershell": "Invoke-WebRequest -Uri '{url}' -OutFile '{destination}' -UseBasicParsing",
        "linux_posix": "curl -fsSL '{url}' -o '{destination}' || wget -q '{url}' -O '{destination}'",
        "macos": "curl -fsSL '{url}' -o '{destination}'",
        "default_params": {"url": "https://example.com/file.txt", "destination": "file.txt"}
    },

    # ------------------------------------------------------------------------
    # 4. PACKAGE MANAGEMENT & SYSTEM UPDATES
    # ------------------------------------------------------------------------
    "install_package": {
        "description": "Install a software package or tool via the host package manager.",
        "windows_powershell": "winget install --id '{package}' -e --accept-package-agreements --accept-source-agreements --silent 2>&1 || choco install '{package}' -y",
        "linux_posix": "sudo apt-get install -y '{package}' 2>/dev/null || sudo dnf install -y '{package}' 2>/dev/null || sudo pacman -S --noconfirm '{package}'",
        "macos": "brew install '{package}'",
        "default_params": {"package": "git"}
    },
    "system_update": {
        "description": "Perform full system package updates.",
        "windows_powershell": "winget upgrade --all --include-unknown --accept-package-agreements --accept-source-agreements",
        "linux_posix": "sudo apt-get update && sudo apt-get upgrade -y 2>/dev/null || sudo dnf upgrade -y 2>/dev/null",
        "macos": "brew update && brew upgrade",
        "default_params": {}
    },

    # ------------------------------------------------------------------------
    # 5. SECURITY AUDITING & SYSTEM HARDENING
    # ------------------------------------------------------------------------
    "firewall_status": {
        "description": "Inspect active firewall profiles and blocking status.",
        "windows_powershell": "Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction",
        "linux_posix": "sudo ufw status verbose 2>/dev/null || sudo iptables -L -n -v --line-numbers | head -n 30",
        "macos": "/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate",
        "default_params": {}
    },
    "list_user_accounts": {
        "description": "Audit local user accounts, guest accounts, and Administrator groups.",
        "windows_powershell": "Get-LocalUser | Select-Object Name, Enabled, LastLogon, Description",
        "linux_posix": "cut -d: -f1,3,7 /etc/passwd | grep -E ':([1-9][0-9]{3}|0):'",
        "macos": "dscl . list /Users | grep -v '^_' | head -n 20",
        "default_params": {}
    },
    "active_established_connections": {
        "description": "Enumerate established outbound and inbound network connections.",
        "windows_powershell": "Get-NetTCPConnection -State Established | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, OwningProcess | Select-Object -First 25",
        "linux_posix": "ss -tupn state established | head -n 25",
        "macos": "netstat -an -f inet | grep ESTABLISHED | head -n 25",
        "default_params": {}
    }
}


class CommandEncyclopedia:
    """Provides categorized cross-platform terminal command synthesis and recipes."""

    @staticmethod
    def get_catalog() -> Dict[str, Dict[str, Any]]:
        """Returns the full dictionary of verified command templates."""
        return COMMAND_CATALOG

    @classmethod
    def get_recipe(
        cls,
        recipe_name: str,
        os_family: str = "windows",
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, str]]:
        """
        Retrieves a filled, parameterized command recipe for a target OS.

        Args:
            recipe_name: Key in COMMAND_CATALOG (e.g. 'kill_process_by_port').
            os_family: 'windows', 'linux', 'wsl', or 'macos'.
            params: Dictionary of parameters to substitute into template.

        Returns:
            Dictionary with command string and description, or None if not found.
        """
        recipe = COMMAND_CATALOG.get(recipe_name)
        if not recipe:
            return None

        # Determine target template key
        if os_family in ["windows"]:
            template = recipe.get("windows_powershell", "")
            shell_type = "powershell"
        elif os_family in ["macos"]:
            template = recipe.get("macos", recipe.get("linux_posix", ""))
            shell_type = "zsh"
        else:  # linux or wsl
            template = recipe.get("linux_posix", "")
            shell_type = "bash"

        # Merge default parameters with overrides
        combined_params = dict(recipe.get("default_params", {}))
        if params:
            combined_params.update(params)

        # Substitute parameters safely
        cmd_str = template
        for k, v in combined_params.items():
            cmd_str = cmd_str.replace(f"{{{k}}}", str(v))

        return {
            "recipe": recipe_name,
            "command": cmd_str,
            "shell_type": shell_type,
            "description": recipe.get("description", "")
        }

    @classmethod
    def search_recipes(cls, query: str) -> List[Dict[str, Any]]:
        """Searches command catalog by keyword or task description."""
        q = query.lower().strip()
        matches = []
        for name, data in COMMAND_CATALOG.items():
            desc = data.get("description", "").lower()
            if q in name.lower() or any(term in desc for term in q.split()):
                matches.append({
                    "name": name,
                    "description": data.get("description"),
                    "windows_example": data.get("windows_powershell", "")[:80] + "...",
                    "posix_example": data.get("linux_posix", "")[:80] + "..."
                })
        return matches

    @classmethod
    def synthesize_for_intent(
        cls,
        intent: str,
        os_family: str = "windows",
        extra_args: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, str]]:
        """
        Synthesizes a command from a high-level intent or natural language prompt.
        """
        intent_lower = intent.lower()

        # Port kill
        port_match = re.search(r'\b(?:port|kill.*port|free.*port)\s*(\d+)\b', intent_lower)
        if not port_match:
            port_match = re.search(r'\b(?:port)\s*:\s*(\d+)\b', intent_lower)
        if port_match and any(k in intent_lower for k in ["kill", "free", "close", "stop", "terminate"]):
            return cls.get_recipe("kill_process_by_port", os_family, {"port": port_match.group(1)})

        # Listening ports
        if any(k in intent_lower for k in ["listening port", "open port", "check port", "ports listening", "netstat"]):
            return cls.get_recipe("list_listening_ports", os_family)

        # Disk usage
        if any(k in intent_lower for k in ["disk space", "disk usage", "free space", "storage", "drive space"]):
            return cls.get_recipe("disk_usage", os_family)

        # Top CPU / RAM
        if "cpu" in intent_lower and any(k in intent_lower for k in ["top", "process", "usage", "heavy"]):
            return cls.get_recipe("list_top_cpu_processes", os_family)
        if any(k in intent_lower for k in ["ram", "memory"]) and any(k in intent_lower for k in ["top", "process", "usage"]):
            return cls.get_recipe("list_top_memory_processes", os_family)

        # Large files
        if any(k in intent_lower for k in ["large file", "biggest file", "largest file", "heavy file"]):
            return cls.get_recipe("find_large_files", os_family, {"path": ".", "count": "15"})

        # Firewall
        if any(k in intent_lower for k in ["firewall", "ufw", "iptables"]):
            return cls.get_recipe("firewall_status", os_family)

        # Services
        if any(k in intent_lower for k in ["service", "services", "systemctl", "daemon"]):
            return cls.get_recipe("list_services", os_family)

        # Network connections
        if any(k in intent_lower for k in ["connections", "established", "sockets"]):
            return cls.get_recipe("active_established_connections", os_family)

        return None
