from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path("models/recommender.joblib")


def load_model(path: Path = MODEL_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found at '{path}'. Run training script first."
        )
    return joblib.load(path)


def recommend_items(artifact: dict, user_id: int, top_k: int = 5) -> list[int]:
    user_item: pd.DataFrame = artifact["user_item"]
    similarity: pd.DataFrame = artifact["similarity"]
    popular_items: list[int] = artifact["popular_items"]

    if user_id not in user_item.index:
        return popular_items[:top_k]

    sims = similarity.loc[user_id]
    weighted_scores = sims @ user_item
    seen_items = user_item.columns[user_item.loc[user_id] > 0].tolist()
    ranked = weighted_scores.sort_values(ascending=False)
    ranked = ranked.drop(labels=seen_items, errors="ignore")
    recs = [int(item_id) for item_id in ranked.head(top_k).index.tolist()]

    if len(recs) < top_k:
        for item_id in popular_items:
            if item_id not in recs and item_id not in seen_items:
                recs.append(int(item_id))
            if len(recs) == top_k:
                break
    return recs
