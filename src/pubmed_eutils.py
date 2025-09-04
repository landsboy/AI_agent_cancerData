import xml.etree.ElementTree as ET
from urllib.parse import urlencode
import requests
from typing import List, Optional
from .constants import EUTILS_BASE, PUBMED_FILTERS, TREATMENT_CORE
from .models import Paper
from .parsing import dedup

def pubmed_esearch(query: str, retmax: int = 50,
                   mindate: Optional[str] = None, maxdate: Optional[str] = None,
                   disease_clause: Optional[str] = None) -> list[str]:
    core = disease_clause or '("renal cell carcinoma"[Title/Abstract] OR RCC[Title/Abstract])'
    term = f"({query}) AND {core} AND {TREATMENT_CORE} AND {PUBMED_FILTERS}"
    params = {"db": "pubmed","term": term,"retmax": retmax,"retmode": "json","sort":"relevance","datetype":"pdat"}
    if mindate: params["mindate"] = mindate
    if maxdate: params["maxdate"] = maxdate
    url = f"{EUTILS_BASE}/esearch.fcgi?{urlencode(params)}"
    r = requests.get(url, timeout=15); r.raise_for_status()
    return r.json().get("esearchresult", {}).get("idlist", []) or []

def pubmed_efetch(pmids: list[str]) -> list[dict]:
    if not pmids: return []
    params = {"db":"pubmed","id":",".join(pmids),"retmode":"xml"}
    url = f"{EUTILS_BASE}/efetch.fcgi?{urlencode(params)}"
    r = requests.get(url, timeout=20); r.raise_for_status()
    root = ET.fromstring(r.text); out=[]
    for art in root.iterfind(".//PubmedArticle"):
        art_md = art.find(".//Article"); 
        if art_md is None: continue
        title = (art_md.findtext("ArticleTitle") or "").strip()
        journal = (art_md.findtext("Journal/Title") or "").strip()
        year = art_md.findtext("Journal/JournalIssue/PubDate/Year")
        year = int(year) if (year and year.isdigit()) else None
        doi = None
        for aid in art.iterfind(".//ArticleIdList/ArticleId"):
            if (aid.get("IdType") or "").lower() == "doi":
                doi = (aid.text or "").strip(); break
        if not doi: continue
        full_link = f"https://doi.org/{doi}"
        out.append({"title":title,"doi":doi,"journal":journal,"year":year,"full_text_url":full_link})
    return out

def from_pubmed_records(records: list[dict]) -> List[Paper]:
    papers: List[Paper] = []
    for rec in records:
        papers.append(Paper(
            title=rec["title"], doi=rec["doi"], journal=rec["journal"], year=rec.get("year"),
            full_text_url=rec["full_text_url"], tables_url=rec["full_text_url"], data_url=rec["full_text_url"]
        ))
    return dedup(papers)
