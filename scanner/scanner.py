"""
scanner/scanner.py
-------------------
Lightweight network security scanner (Prototype 4).

Per Section 4.1/4.3 of the methodology, this module does NOT try to
replicate a full-scale scanner such as Nessus. It performs simple,
targeted checks:

    1. Host discovery  - is a given IP/hostname reachable?
    2. Port scanning   - which common ports are open on that host?
    3. Vulnerability flagging - open ports 21 (FTP) and 23 (Telnet) are
       flagged because they are unencrypted protocols. A few other
       commonly-risky ports are flagged too, for a slightly richer demo.

IMPORTANT DEPLOYMENT NOTE (flagged to the user in the chat as well):
The original methodology (Section 4.1) specifies Anaconda/local Python
as the development environment specifically BECAUSE a network scanner
must run on the SME's local network, which a hosted cloud platform
(Render, PythonAnywhere, Replit) cannot see. When this app is deployed
to one of those platforms, this module can only scan hosts that are
reachable FROM the cloud server (e.g. public IPs/domains) - it cannot
discover or scan devices on an SME's private LAN (192.168.x.x, etc.).
The code below is written to still work correctly in that situation
(demonstrating the logic against reachable targets), and the UI shows
a visible warning about this limitation.
"""

import socket
import subprocess
import platform
import ipaddress
from concurrent.futures import ThreadPoolExecutor

# Ports considered interesting for a lightweight SME-focused scan
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt",
}

# Ports flagged as insecure/unencrypted per the methodology's example
VULNERABLE_PORTS = {
    21: "Open FTP (port 21) - unencrypted file transfer protocol",
    23: "Open Telnet (port 23) - unencrypted remote access protocol",
    139: "Open NetBIOS (port 139) - legacy file-sharing service, often exploitable",
    445: "Open SMB (port 445) - target of ransomware worms (e.g. EternalBlue) if unpatched",
    3389: "Open RDP (port 3389) - common brute-force target if exposed to the internet",
}


def is_valid_target(target: str) -> bool:
    """Accept either a valid IP address or a resolvable hostname."""
    try:
        ipaddress.ip_address(target)
        return True
    except ValueError:
        try:
            socket.gethostbyname(target)
            return True
        except socket.error:
            return False


def ping_host(target: str, timeout_sec: int = 1) -> bool:
    """Cross-platform ping using subprocess. Returns True if the host replies.
    Note: many cloud hosting platforms block outbound ICMP, so this can
    return False even for a genuinely reachable host - the port scan
    below (TCP connect) is the more reliable signal in that environment."""
    system = platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"
    timeout_flag = "-w" if system == "windows" else "-W"
    timeout_val = str(timeout_sec * 1000) if system == "windows" else str(timeout_sec)

    try:
        result = subprocess.run(
            ["ping", count_flag, "1", timeout_flag, timeout_val, target],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout_sec + 2,
        )
        return result.returncode == 0
    except Exception:
        return False


def scan_port(target: str, port: int, timeout_sec: float = 0.6) -> bool:
    """TCP connect scan for a single port. Returns True if open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout_sec)
            result = sock.connect_ex((target, port))
            return result == 0
    except Exception:
        return False


def scan_host(target: str) -> dict:
    """Run the full lightweight scan against a single target.
    Returns a dict ready to be stored via database.models.save_scan_result.
    """
    if not is_valid_target(target):
        return {
            "device_ip": target,
            "device_name": "Unknown",
            "reachable": False,
            "open_ports": [],
            "vulnerabilities": [],
            "error": "Target could not be resolved or is not a valid IP/hostname.",
        }

    try:
        resolved_ip = target if _looks_like_ip(target) else socket.gethostbyname(target)
    except Exception:
        resolved_ip = target

    reachable = ping_host(target)

    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_port, target, p): p for p in COMMON_PORTS}
        for future in futures:
            port = futures[future]
            try:
                if future.result():
                    open_ports.append(port)
            except Exception:
                continue

    # A port responded even if ping failed (ICMP often blocked) -> reachable
    if open_ports:
        reachable = True

    open_ports.sort()
    vulnerabilities = [VULNERABLE_PORTS[p] for p in open_ports if p in VULNERABLE_PORTS]

    return {
        "device_ip": resolved_ip,
        "device_name": target,
        "reachable": reachable,
        "open_ports": open_ports,
        "open_ports_named": [f"{p}/{COMMON_PORTS.get(p, 'unknown')}" for p in open_ports],
        "vulnerabilities": vulnerabilities,
        "error": None,
    }


def _looks_like_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False
