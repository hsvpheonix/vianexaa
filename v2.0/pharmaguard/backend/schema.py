from pydantic import BaseModel

class DrugResponse(BaseModel):
    drug: str
    gene: str | None
    phenotype: str | None
    recommendation: str
    explanation: str | None
