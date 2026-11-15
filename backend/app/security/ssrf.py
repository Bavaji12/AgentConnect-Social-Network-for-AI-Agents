import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple
from app.core.config import settings
from app.core.exceptions import SSRFSecurityException

def validate_webhook_url(url: str) -> Tuple[bool, str]:
    """
    Validates webhook URL to protect against Server-Side Request Forgery (SSRF).
    Blocks non-HTTP/HTTPS schemes, localhost, private IP ranges, link-local addresses,
    cloud metadata endpoints (e.g. 169.254.169.254) in production.
    """
    if not url:
        return False, "Webhook URL cannot be empty."

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, f"Invalid scheme '{parsed.scheme}'. Only http and https are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Invalid URL: missing hostname."

    # If allowed in local development/testing mode
    if settings.ALLOW_PRIVATE_IPS:
        return True, "Allowed by local development configuration."

    # In production, strictly block loopback, metadata, and private IP networks
    if hostname.lower() in ("localhost", "127.0.0.1", "::1", "metadata.google.internal"):
        return False, f"Access to localhost/internal host '{hostname}' is blocked."

    try:
        # Resolve hostname to IPv4/IPv6 addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)

            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                return False, f"Target host resolves to restricted private/internal IP: {ip_str}"

            # Specifically guard AWS/GCP/Azure link-local metadata endpoints
            if str(ip).startswith("169.254."):
                return False, f"Access to cloud metadata address '{ip_str}' is strictly forbidden."

    except socket.gaierror:
        return False, f"Failed to resolve hostname '{hostname}'"
    except Exception as e:
        return False, f"DNS resolution error: {str(e)}"

    return True, "Valid"
