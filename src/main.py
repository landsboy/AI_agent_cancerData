# main.py
import logging, sys
from typing import Optional, Sequence
from .cli import build_arg_parser
from .parsing import parse_years_from_text
from .disease import build_disease_clause, infer_disease_from_text
from .io_utils import save_by_suffix
from .http_client import build_session
from .verify import verify_all
from .discovery.pubmed import PubMedDiscovery
from .discovery.llm_grounded import LlmGroundedDiscovery
from .discovery.llm import LlmFreeDiscovery
import os
from dotenv import load_dotenv

# Load .env once, so PERPLEXITY_API_KEY, TAVILY_API_KEY, etc. are available
load_dotenv()

REQUIRED_KEYS = ["OPENAI_API_KEY", "NCBI_API_KEY", "TAVILY_API_KEY"]

def _assert_env():
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing required env var(s): {', '.join(missing)}. "
                         "Create a .env file or export them in your shell.")

def setup_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

def get_discovery(mode: str):
    return {"pubmed": PubMedDiscovery(), "llm-grounded": LlmGroundedDiscovery(), "llm": LlmFreeDiscovery()}[mode]

def main(argv: Optional[Sequence[str]] = None) -> int:
    _assert_env()
    args = build_arg_parser().parse_args(argv)
    setup_logging(args.verbose)

    mindate, maxdate = parse_years_from_text(args.input)

    # Resolve disease: CLI flag takes precedence; otherwise infer from input; fallback to RCC.
    disease = (args.disease or "").strip() or infer_disease_from_text(args.input) or "renal cell carcinoma"
    disease_clause, disease_name = build_disease_clause(disease)

    disc = get_discovery(args.discovery)
    papers, raw = disc.discover(args.input, n_results=args.n_results, mindate=mindate, maxdate=maxdate, disease_clause=disease_clause, disease_name=disease_name)

    if not args.no_verify and papers:
        session = build_session()
        papers = verify_all(session, papers, strict=args.strict_verify)

    save_by_suffix(args.output, papers)
    print(f"Wrote {len(papers)} items to {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
