from pydantic import BaseModel, Field


class CreateBranchRequest(BaseModel):
    owner: str = Field(min_length=1, max_length=100)
    repo: str = Field(min_length=1, max_length=100)
    base_branch: str = Field(min_length=1, max_length=255)


class CreatedBranchResponse(BaseModel):
    branch_name: str
    sha: str
    url: str