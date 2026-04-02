import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src.data.generate_data import INTERACTIONS_PATH, generate_data

DATA_DIR = Path("data/raw")
MODELS_DIR = Path("models")
MODEL_PATH = MODELS_DIR / "recommender.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"


def prepare_dataset() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not INTERACTIONS_PATH.exists():
        generate_data()
    return pd.read_csv(INTERACTIONS_PATH)


def train() -> None:
    df = prepare_dataset()
    user_item = (
        df.groupby(["user_id", "item_id"])["rating"]
        .mean()
        .unstack(fill_value=0.0)
        .sort_index()
    )
    item_popularity = (
        df.groupby("item_id")["rating"].mean().sort_values(ascending=False)
    )

    similarity = cosine_similarity(user_item.values)
    np.fill_diagonal(similarity, 0.0)
    similarity_df = pd.DataFrame(
        similarity, index=user_item.index, columns=user_item.index
    )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    artifact = {
        "user_item": user_item,
        "similarity": similarity_df,
        "popular_items": item_popularity.index.tolist(),
    }
    joblib.dump(artifact, MODEL_PATH)
    METRICS_PATH.write_text(
        json.dumps(
            {
                "users": int(user_item.shape[0]),
                "items": int(user_item.shape[1]),
                "interactions": int(len(df)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Model saved to {MODEL_PATH}")
    print(f"Metrics saved to {METRICS_PATH}")


if __name__ == "__main__":
    train()
