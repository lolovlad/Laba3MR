from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path("data/raw")
INTERACTIONS_PATH = DATA_DIR / "interactions.csv"
ITEMS_PATH = DATA_DIR / "items.csv"


def generate_data(
    num_users: int = 80,
    num_items: int = 60,
    interactions_per_user: int = 18,
    seed: int = 40,
) -> None:
    rng = np.random.default_rng(seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    items = pd.DataFrame(
        {
            "item_id": np.arange(1, num_items + 1),
            "category": rng.choice(["books", "movies", "music"], size=num_items),
        }
    )
    items.to_csv(ITEMS_PATH, index=False)

    records: list[dict[str, int | float]] = []
    for user_id in range(1, num_users + 1):
        preferred_category = rng.choice(["books", "movies", "music"])
        preferred_items = items[items["category"] == preferred_category][
            "item_id"
        ].tolist()
        other_items = items[items["category"] != preferred_category]["item_id"].tolist()

        sampled_pref = rng.choice(
            preferred_items,
            size=max(1, int(interactions_per_user * 0.7)),
            replace=True,
        )
        sampled_other = rng.choice(
            other_items,
            size=max(1, interactions_per_user - len(sampled_pref)),
            replace=True,
        )

        for item_id in np.concatenate([sampled_pref, sampled_other]):
            base = 4.0 if item_id in preferred_items else 2.8
            rating = float(np.clip(rng.normal(base, 0.7), 1.0, 5.0))
            records.append(
                {"user_id": user_id, "item_id": int(item_id), "rating": rating}
            )

    pd.DataFrame(records).to_csv(INTERACTIONS_PATH, index=False)
    print(f"Saved {INTERACTIONS_PATH} and {ITEMS_PATH}")


if __name__ == "__main__":
    generate_data()
