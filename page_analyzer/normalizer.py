from urllib.parse import urlparse


def normalize_url(url):
    parced = urlparse(url)
    normalized = f"{parced.scheme}://{parced.netloc}"
    return normalized
   
