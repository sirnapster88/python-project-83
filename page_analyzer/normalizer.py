from urllib.parse import urlparse


def _normalize_url(url):
    try:
        parced = urlparse(url)
        normalized = f"{parced.scheme}://{parced.netloc}"
        return normalized
    except Exception:
        return url
