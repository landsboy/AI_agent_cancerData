from typing import Protocol, Optional, Sequence, Tuple
from ..models import Paper


class Discovery(Protocol):
    """Unified interface for discovery strategies."""

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
        """
        Return (papers, raw_debug_text).
        Implementations should:
        - produce up to ~n_results Paper objects (dedup if needed),
        - return a short 'raw' string useful for logging/debugging.
        """
        ...
