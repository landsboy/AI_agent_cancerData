# discovery/llm_grounded.py
from __future__ import annotations

from typing import Optional, Sequence, Tuple, List
from pydantic import ValidationError
from .base import Discovery
from ..models import Paper
from ..pubmed_eutils import pubmed_esearch, pubmed_efetch
from ..agent import build_agent
from ..parsing import parse_agent_output, coerce_item, dedup
from ..tools import make_pubmed_tool, make_web_tool, make_safe_get_tool
from ..http_client import _is_allowed  # or re-export a checker you already have


class LlmGroundedDiscovery(Discovery):
    def discover(
        self,
        query: str,
        *,
        n_results: int,
        mindate: Optional[str],
        maxdate: Optional[str],
        disease_clause: Optional[str],
        disease_name: str,
    ) -> Tuple[Sequence[Paper], str]:
        # 1) PubMed candidates
        pmids = pubmed_esearch(
            query,
            retmax=max(n_results * 4, 40),
            mindate=mindate,
            maxdate=maxdate,
            disease_clause=disease_clause,
        )
        recs = pubmed_efetch(pmids)
        cand_dois = {r["doi"].lower() for r in recs}
        candidate_blob = "\n".join([f"- DOI: {r['doi']} | TITLE: {r['title']}" for r in recs[:100]])

        # 2) Agent restricted to those DOIs
        tools = [
            make_pubmed_tool(mindate, maxdate, disease_clause or ""),
            make_web_tool(),
            make_safe_get_tool(_is_allowed),
        ]
        agent = build_agent(
            n_results=n_results,
            temperature=0.0,
            mindate=mindate,
            maxdate=maxdate,
            disease_clause=disease_clause,
            disease_name=disease_name,
            tools=tools,
        )
        grounded_query = (
            f"Select up to {n_results} items STRICTLY from the CANDIDATES list below.\n"
            f"CANDIDATES (DOI+TITLE):\n{candidate_blob}\n\n"
            f"Original user query: {query}"
        )
        raw = agent.invoke({"input": grounded_query})["output"]
        payload = parse_agent_output(raw)

        records = []
        for item in payload:
            try:
                records.append(coerce_item(item))
            except Exception:
                pass

        tmp: List[Paper] = []
        for rec in records:
            try:
                tmp.append(Paper(**rec))
            except ValidationError:
                pass

        papers = [p for p in dedup(tmp) if p.doi.lower() in cand_dois]
        return papers, raw
