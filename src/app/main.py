from fastapi import FastAPI

from src.app.schemas import RecommendRequest, RecommendResponse
from src.ml.predict import MODEL_PATH, load_model, recommend_items
from src.data.generate_data import INTERACTIONS_PATH, generate_data
from src.ml.train import train

app = FastAPI(title="Laba3 Recommender API", version="0.1.0")
artifact = None


@app.on_event("startup")
def startup_event() -> None:
    global artifact
    if not INTERACTIONS_PATH.exists():
        generate_data()
    if not MODEL_PATH.exists():
        train()
    artifact = load_model()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest) -> RecommendResponse:
    global artifact
    if artifact is None:
        if not INTERACTIONS_PATH.exists():
            generate_data()
        if not MODEL_PATH.exists():
            train()
        artifact = load_model()
    recommendations = recommend_items(artifact, payload.user_id, payload.top_k)
    return RecommendResponse(user_id=payload.user_id, recommendations=recommendations)
