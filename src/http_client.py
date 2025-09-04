import requests
from urllib.parse import urlparse
from typing import Optional
from .constants import ALLOWED_HOSTS, ALLOWED_CT

def build_session() -> requests.Session:
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    s = requests.Session()
    s.headers.update({"User-Agent":"RCC-Agent/1.0 (+contact@example.com)", "Accept":"*/*"})
    retry = Retry(total=3, connect=3, read=3, status=3,
                  allowed_methods=frozenset(["HEAD","GET"]),
                  status_forcelist=[429,500,502,503,504],
                  backoff_factor=0.5, raise_on_status=False)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

def _is_allowed(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in ALLOWED_HOSTS)

def head_ok(session: requests.Session, url: str, timeout: float = 12.0, referer: Optional[str] = None) -> bool:
    if not _is_allowed(url): return False
    try:
        headers = {"Referer": referer} if referer else {}
        r = session.head(url, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code >= 400 or r.status_code in (405, 403):
            r = session.get(url, stream=True, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code >= 400:
            ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            if _is_allowed(url) and (url.lower().endswith((".pdf",".csv",".tsv",".xlsx",".xls",".zip")) or ct in ALLOWED_CT):
                return True
            return False
        ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if not ct:
            return url.lower().endswith((".html",".htm",".pdf",".csv",".tsv",".xlsx",".xls",".zip"))
        return ct in ALLOWED_CT
    except Exception:
        return False
