# discovery/llm_free.py
from __future__ import annotations

from typing import Optional, Sequence, Tuple, List
from pydantic import ValidationError
from .base import Discovery
from ..models import Paper
from ..agent import build_agent
from ..parsing import parse_agent_output, coerce_item, dedup
from ..tools import make_pubmed_tool, make_web_tool, make_safe_get_tool
from ..http_client import _is_allowed


class LlmFreeDiscovery(Discovery):
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
        raw = agent.invoke({"input": query})["output"]
        payload = parse_agent_output(raw)

        records: List[dict] = []
        for item in payload:
            try:
                records.append(coerce_item(item))
            except Exception:
                pass

        papers: List[Paper] = []
        for rec in records:
            try:
                papers.append(Paper(**rec))
            except ValidationError:
                pass

        return list(dedup(papers)), raw
