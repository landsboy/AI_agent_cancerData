import json, re
from typing import Optional, Sequence, List, Any
from .constants import FIELDS
from .models import Paper

def parse_years_from_text(text: str) -> tuple[Optional[str], Optional[str]]:
    s = re.sub(r'https?://\S+', ' ', text)
    s = re.sub(r'10\.\d{4,9}/\S+', ' ', s)
    m = re.search(r'(?<!\d)(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}(?!\d)', s)
    if m:
        y = re.findall(r'(?:19|20)\d{2}', m.group(0)); return (min(y), max(y))
    for pat in [r'between\s+(?:19|20)\d{2}\s+and\s+(?:19|20)\d{2}',
                r'from\s+(?:19|20)\d{2}\s+to\s+(?:19|20)\d{2}']:
        m = re.search(pat, s, flags=re.I)
        if m:
            y = re.findall(r'(?:19|20)\d{2}', m.group(0)); return (min(y), max(y))
    m = re.search(r'(since|after)\s+(?:19|20)\d{2}', s, flags=re.I)
    if m: return (re.search(r'(?:19|20)\d{2}', m.group(0)).group(0), None)
    m = re.search(r'(until|before|up to)\s+(?:19|20)\d{2}', s, flags=re.I)
    if m: return (None, re.search(r'(?:19|20)\d{2}', m.group(0)).group(0))
    m = re.search(r'years?\s+(?:19|20)\d{2}\s*[-–]\s*(?:19|20)\d{2}', s, flags=re.I)
    if m:
        y = re.findall(r'(?:19|20)\d{2}', m.group(0)); return (min(y), max(y))
    return (None, None)

def _extract_top_level_json_array(s: str) -> str:
    in_str = False; escape = False; depth = 0; start = None
    for i, ch in enumerate(s):
        if ch == '"' and not escape: in_str = not in_str
        if ch == "\\" and not escape: escape = True; continue
        if not in_str:
            if ch == "[":
                if depth == 0: start = i
                depth += 1
            elif ch == "]" and depth > 0:
                depth -= 1
                if depth == 0 and start is not None: return s[start:i+1]
        escape = False
    raise json.JSONDecodeError("No top-level JSON array found", s, 0)

def parse_agent_output(raw: str) -> Any:
    t = raw.strip()
    if t.startswith("[") or t.startswith("{"): return json.loads(t)
    i = t.rfind("Final Answer:")
    if i != -1:
        cand = t[i + len("Final Answer:"):].strip()
        if cand.startswith("```"):
            end = cand.find("```", 3)
            if end != -1:
                body = cand[3:end]; nl = body.find("\n")
                cand = body[nl+1:] if nl != -1 else body
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            arr = _extract_top_level_json_array(cand)
            return json.loads(arr)
    arr = _extract_top_level_json_array(t)
    return json.loads(arr)

def coerce_item(x) -> dict:
    if isinstance(x, dict):
        d = {k: x.get(k, "") for k in FIELDS}
    elif isinstance(x, (list, tuple)) and len(x) >= 7:
        d = dict(zip(FIELDS, list(x)[:7]))
    else:
        raise ValueError(f"Unexpected item shape: {type(x)}")
    try:
        d["year"] = int(d["year"])
    except Exception:
        d["year"] = None
    return d

def dedup(items: Sequence[Paper]) -> List[Paper]:
    seen, out = set(), []
    for p in items:
        if p.doi.lower() not in seen:
            seen.add(p.doi.lower()); out.append(p)
    return out
