from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    top_k: int = Field(default=5, ge=1, le=20)


class RecommendResponse(BaseModel):
    user_id: int
    recommendations: list[int]
