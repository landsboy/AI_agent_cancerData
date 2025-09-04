from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Sequence, Tuple
from .models import Paper
from .http_client import head_ok, _is_allowed

def verify_paper_lenient(session, p: Paper) -> bool:
    ft, tb, dt = str(p.full_text_url), str(p.tables_url), str(p.data_url)
    if not head_ok(session, ft): return False
    tables_ok = (tb == ft) or head_ok(session, tb, referer=ft) or (
        _is_allowed(tb) and (tb.lower().endswith((".pdf",".csv",".tsv",".xlsx",".xls",".zip"))
                             or any(k in tb.lower() for k in ("supplement","supplementary","/esm/")))
    )
    if not tables_ok: return False
    data_ok = (dt == ft) or _is_allowed(dt) or head_ok(session, dt, referer=ft)
    return bool(data_ok)

def verify_all(session, papers: Sequence[Paper], max_workers: int = 8, strict: bool = False) -> List[Paper]:
    def verify_one(p: Paper) -> Tuple[Paper, bool]:
        if strict:
            ok = head_ok(session, str(p.full_text_url)) \
                 and head_ok(session, str(p.tables_url), referer=str(p.full_text_url)) \
                 and head_ok(session, str(p.data_url), referer=str(p.full_text_url))
            return p, ok
        return p, verify_paper_lenient(session, p)

    out: List[Paper] = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(verify_one, p) for p in papers]
        for fut in as_completed(futures):
            p, ok = fut.result()
            if ok: out.append(p)
    return out
