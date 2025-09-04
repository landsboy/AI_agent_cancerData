# cli.py
import argparse
from pathlib import Path
from .constants import DEFAULT_N_RESULTS

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="IO+TKI literature mining agent (PubMed + web).")
    p.add_argument("-i", "--input", help="Agent query (string). If omitted, uses a sensible default.",
        default="RCC IO+TKI, human patients. Return diverse trials and cohorts.")
    p.add_argument("-n", "--n-results", type=int, default=DEFAULT_N_RESULTS, help="Target number of results to collect (default: %(default)s).")
    p.add_argument("-o", "--output", type=Path, default=Path("results/io_tki_papers.json"), help="Output path (json/jsonl/csv) (default: %(default)s).")
    p.add_argument("--no-verify", action="store_true", help="Do not verify URLs (faster, but may include dead links).")
    p.add_argument("--strict-verify", action="store_true", help="Strict verification (require 200 for data_url as well).")
    p.add_argument("--workers", type=int, default=8, help="Max workers for verification (default: %(default)s).")
    p.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity (-v, -vv).")
    p.add_argument("--discovery", choices=["pubmed", "llm-grounded", "llm"], default="llm",
        help="Candidate discovery: 'pubmed' (deterministic, safest), 'llm-grounded' (LLM restricted to PubMed DOIs), or 'llm' (free-form).")
    p.add_argument("--disease", help="Disease of interest (e.g., 'renal cell carcinoma', 'nsclc', 'melanoma'). "
         "If omitted, inferred from --input when possible; otherwise defaults to RCC.")

    return p
