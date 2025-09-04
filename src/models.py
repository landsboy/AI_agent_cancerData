import re
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_serializer, field_validator

class Paper(BaseModel):
    title: str
    doi: str
    journal: str
    year: Optional[int] = None
    full_text_url: HttpUrl
    tables_url: HttpUrl
    data_url: HttpUrl

    @field_validator("doi")
    @classmethod
    def norm_doi(cls, v: str) -> str:
        m = re.search(r"(10\.\d{4,9}/\S+)", v.strip(), flags=re.I)
        if m:
            return m.group(1).rstrip(".,)")
        raise ValueError("Invalid DOI")

    @field_serializer("full_text_url", "tables_url", "data_url")
    def _ser_url(self, v):
        return str(v)
