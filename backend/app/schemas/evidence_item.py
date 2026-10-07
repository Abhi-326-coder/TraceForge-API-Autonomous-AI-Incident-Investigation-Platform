from pydantic import BaseModel


class EvidenceItem(BaseModel):

    id: int

    source_type: str

    provider: str

    title: str

    content: str

    source_reference: str | None = None