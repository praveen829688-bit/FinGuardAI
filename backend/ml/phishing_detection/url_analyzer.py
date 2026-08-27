import ipaddress
import re
from urllib.parse import urlparse


SUSPICIOUS_KEYWORDS = {
    "login",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "password",
    "signin",
    "confirm",
    "wallet",
    "banking",
    "payment",
    "recover",
    "suspended",
    "unlock",
}


SUSPICIOUS_TLDS = {
    ".tk",
    ".ml",
    ".ga",
    ".cf",
    ".gq",
}


def is_ip_address(hostname: str) -> bool:
    if not hostname:
        return False

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def extract_url_features(url: str):
    normalized_url = url.strip()

    if not re.match(
        r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
        normalized_url
    ):
        normalized_url = "http://" + normalized_url

    parsed = urlparse(normalized_url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    hostname_lower = hostname.lower()
    full_url_lower = normalized_url.lower()

    subdomain_count = 0

    if hostname:
        subdomain_count = max(
            len(hostname.split(".")) - 2,
            0
        )

    keyword_matches = [
        keyword
        for keyword in SUSPICIOUS_KEYWORDS
        if keyword in full_url_lower
    ]

    suspicious_tld = any(
        hostname_lower.endswith(tld)
        for tld in SUSPICIOUS_TLDS
    )

    features = {
        "https": int(
            parsed.scheme.lower() == "https"
        ),

        "url_length": len(normalized_url),

        "hostname_length": len(hostname),

        "path_length": len(path),

        "query_length": len(query),

        "is_ip_address": int(
            is_ip_address(hostname)
        ),

        "has_at_symbol": int(
            "@" in normalized_url
        ),

        "has_double_slash_path": int(
            "//" in path
        ),

        "subdomain_count": subdomain_count,

        "suspicious_keyword_count": len(
            keyword_matches
        ),

        "suspicious_tld": int(
            suspicious_tld
        ),

        "has_punycode": int(
            "xn--" in hostname_lower
        ),

        "has_percent_encoding": int(
            "%" in normalized_url
        ),

        "has_port": int(
            parsed.port is not None
        ),

        "has_fragment": int(
            bool(parsed.fragment)
        ),
    }

    return {
        "normalized_url": normalized_url,
        "hostname": hostname,
        "features": features,
        "keyword_matches": keyword_matches,
    }
