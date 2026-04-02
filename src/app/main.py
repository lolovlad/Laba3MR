from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.schemas import RecommendRequest, RecommendResponse
from src.ml.predict import MODEL_PATH, load_model, recommend_items
from src.data.generate_data import INTERACTIONS_PATH, generate_data
from src.ml.train import train

artifact = None


def _warmup_artifact() -> None:
    global artifact
    if not INTERACTIONS_PATH.exists():
        generate_data()
    if not MODEL_PATH.exists():
        train()
    artifact = load_model()


@asynccontextmanager
async def lifespan(_: FastAPI):
    _warmup_artifact()
    yield


app = FastAPI(title="Laba3 Recommender API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest) -> RecommendResponse:
    if artifact is None:
        _warmup_artifact()
    recommendations = recommend_items(artifact, payload.user_id, payload.top_k)
    return RecommendResponse(user_id=payload.user_id, recommendations=recommendations)
