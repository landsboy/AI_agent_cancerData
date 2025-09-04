from __future__ import annotations

from typing import Optional, Sequence, Tuple, List
from .base import Discovery
from ..models import Paper
from ..pubmed_eutils import pubmed_esearch, pubmed_efetch, from_pubmed_records


class PubMedDiscovery(Discovery):
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
        pmids = pubmed_esearch(
            query,
            retmax=max(n_results * 4, 40),
            mindate=mindate,
            maxdate=maxdate,
            disease_clause=disease_clause,
        )
        recs = pubmed_efetch(pmids)[: max(n_results * 2, n_results)]
        papers: List[Paper] = from_pubmed_records(recs)
        raw = f"[pubmed] pmids={len(pmids)}, records={len(recs)}, papers={len(papers)}"
        return papers, raw
