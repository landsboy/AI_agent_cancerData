# Canonical constants used across modules.
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

ALLOWED_CT = {
    "text/html", "application/pdf", "application/json", "text/csv", "text/plain",
    "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/zip", "application/octet-stream",
}

ALLOWED_HOSTS = {
    "pmc.ncbi.nlm.nih.gov", "www.ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "www.nature.com", "www.sciencedirect.com", "link.springer.com",
    "jamanetwork.com", "www.nejm.org", "ascopubs.org", "www.esmoopen.com",
    "academic.oup.com", "bmj.com", "www.frontiersin.org",
    "www.pnas.org", "www.ebi.ac.uk", "www.ensembl.org",
    "www.thelancet.com", "aacrjournals.org", "clincancerres.aacrjournals.org",
    "www.cell.com", "www.elsevier.com", "europepmc.org",
    "static-content.springer.com", "media.springernature.com",
    "www.annalsofoncology.org", "annalsofoncology.org",
    "www.europeanurology.com", "europeanurology.com",
}

PUBMED_FILTERS = (
    'Humans[Mesh] AND (Clinical Trial[ptyp] OR Randomized Controlled Trial[ptyp]) '
    'AND (supplementary OR "supplementary materials" OR dataset OR "data availability" OR "supplementary information")'
)

TREATMENT_CORE = (
    '((tyrosine kinase inhibitor) OR TKI) AND '
    '((immune checkpoint) OR ICI OR PD-1 OR PD-L1 OR CTLA-4 OR immunotherapy)'
)

FIELDS = ["title", "doi", "journal", "year", "full_text_url", "tables_url", "data_url"]

DEFAULT_N_RESULTS = 12
LOGGER_NAME = "AI_agent"

# Canonical, normalized synonym map (all lowercase).
DISEASE_SYNONYMS: dict[str, tuple[str, ...]] = {
    "renal cell carcinoma": ("renal cell carcinoma", "rcc"),
    "non-small cell lung cancer": ("non-small cell lung cancer", "non small cell lung cancer", "nsclc"),
    "small cell lung cancer": ("small cell lung cancer", "sclc"),
    "hepatocellular carcinoma": ("hepatocellular carcinoma", "hcc"),
    "urothelial carcinoma": ("urothelial carcinoma", "bladder cancer", "bca"),
    "colorectal cancer": ("colorectal cancer", "crc"),
    "breast cancer": ("breast cancer", "brca"),
    "prostate cancer": ("prostate cancer", "pca"),
    "melanoma": ("melanoma",),
    "gastric cancer": ("gastric cancer", "stomach cancer"),
    "pancreatic ductal adenocarcinoma": ("pancreatic ductal adenocarcinoma", "pdac", "pancreatic cancer"),
    "glioblastoma": ("glioblastoma", "gbm"),
    "ovarian cancer": ("ovarian cancer", "eoc"),
}

