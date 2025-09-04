import requests
from langchain.tools import Tool
from langchain_community.utilities.pubmed import PubMedAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults 
from .constants import PUBMED_FILTERS, TREATMENT_CORE

def make_pubmed_tool(mindate, maxdate, disease_clause: str) -> Tool:
    api = PubMedAPIWrapper(top_k_results=8, load_max_docs=8, doc_content_chars_max=5000)
    def run(q: str) -> str:
        date_clause = ""
        if mindate or maxdate:
            if mindate and maxdate:
                date_clause = f' AND ("{mindate}"[Date - Publication] : "{maxdate}"[Date - Publication])'
            elif mindate:
                date_clause = f' AND ("{mindate}"[Date - Publication] : "3000"[Date - Publication])'
            else:
                date_clause = f' AND ("0001"[Date - Publication] : "{maxdate}"[Date - Publication])'
        term = f"({q}) AND {disease_clause} AND {TREATMENT_CORE} AND {PUBMED_FILTERS}{date_clause}"
        return api.run(term)
    return Tool(name="pubmed_filtered", func=run, description="PubMed with enforced filters and dynamic disease/date.")

def make_web_tool():
    return TavilySearchResults(k=6)

def make_safe_get_tool(_is_allowed):
    def safe_get(url: str) -> str:
        if not _is_allowed(url): return "blocked: domain not allowed"
        try:
            r = requests.get(url, timeout=10); r.raise_for_status()
            return r.text[:20000]
        except Exception as e:
            return f"error: {e}"
    return Tool(name="safe_get", func=safe_get, description="Fetch HTML only from approved domains.")
