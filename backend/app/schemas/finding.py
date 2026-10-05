from pydantic import BaseModel


class Finding(BaseModel):
    title: str
    summary: str
    severity: str
    evidence_ids: list[int]
    
# {
#   "title": "Database connection pool exhaustion",
#   "summary": "Checkout requests are failing because the database connection pool is nearly exhausted.",
#   "severity": "HIGH",
#   "evidence_ids": [1, 2, 3]
# }