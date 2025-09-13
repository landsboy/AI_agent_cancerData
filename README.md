# AI_agent_cancerData
IO+TKI Literature Mining Agent

Retrieval-aware agent that mines peer-reviewed oncology literature (default: RCC with IO+TKI) and exports structured results.
Designed to minimize hallucinations via deterministic PubMed discovery, strict schema validation, and optional URL/DIO checks.

## Key Features

• Discovery modes

    • pubmed — deterministic PubMed E-utilities only (no LLM guesses).

    • llm-grounded — LLM chooses only from PubMed-derived candidates (safer).

    • llm — free LLM discovery (flexible, but may hallucinate).

• Disease control — not locked to RCC. Pass --disease "non-small cell lung cancer" etc.

• Date handling — the tool infers date ranges from your input string (e.g., “since 2020”, “2019–2024”). If no years are present, no date filter is applied.

• Verification — lenient/strict URL checks; optional Crossref title validation (if enabled in your code).

• CLI — outputs JSON, JSONL, or CSV (chosen by the output file suffix).

• Robust parsing of agent outputs (when using LLM modes).

## Installation

1) **Create the conda env**

```
conda env create -f environment.yml
conda activate AI_data_agent
```
2) **Environment variables**

Create a `.env` in the project root:
```
PERPLEXITY_API_KEY=your_perplexity_key
NCBI_API_KEY=your_ncbi_key
TAVILY_API_KEY=your_tavily_key
```
Only the keys you actually use are required. The code loads `.env` automatically (via python-dotenv).

## Running

Assuming your package is src and the entrypoint is src/main.py, run from the project root:

```
python -m src.main [FLAGS...]
```

## Common examples

**AI LLM Agent:**

```
python -m src.main \
  -i "IO+TKI in metastatic RCC, 2020–2025, with RNA-seq or H&E" \
  --discovery llm \
  -o results/rcc_papers.json \
  -v
```

**LLM grounded to PubMed candidates (safer than free LLM):**

```
python -m src.main \
  -i "First-line IO+TKI outcomes" \
  --discovery llm-grounded \
  -o results/papers.jsonl \
  -vv
```

**Different disease (e.g., NSCLC) + strict verification + CSV output:**

```
python -m src.main \
  -i "IO+TKI outcomes in advanced NSCLC, since 2019" \
  --disease "non-small cell lung cancer" \
  --discovery pubmed \
  --strict-verify \
  -o results/nsclc_papers.csv
```

**Fast run without URL verification (may include dead links):**

```
python -m src.main \
  -i "RCC IO+TKI with survival tables" \
  --discovery pubmed \
  --no-verify \
  -o results/fast.json
```

## Output Schema

Each item adheres to:

```
{
  "title": "string",
  "doi": "10.xxxx/xxxx",
  "journal": "string",
  "year": 2021,
  "full_text_url": "https://...",
  "tables_url": "https://...",
  "data_url": "https://..."
}
```

•  year is an integer when available, otherwise null.

•  Export format is chosen by the --output suffix:

    • .json → pretty JSON array

    • .jsonl → one JSON object per line

    • .csv → header + rows