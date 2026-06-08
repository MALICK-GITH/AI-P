"""
Baseline training script from a CSV of finished matches.

Produces several models compatible with the project architecture:
- match_winner
- over_under_2.5
- total_goals_parity
- team_home_goals
- team_away_goals
- match_total_goals
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, balanced_accuracy_score, mean_absolute_error

from app.services.feature_builder import (
    FEATURE_COLUMNS,
    build_training_features as shared_build_training_features,
    prepare_training_dataframe as shared_prepare_training_dataframe,
)


@dataclass
class SafeLabelEncoder:
    classes_: List[str] = field(default_factory=list)
    class_to_index_: Dict[str, int] = field(default_factory=dict)

    def fit(self, values: Iterable[object]) -> "SafeLabelEncoder":
        seen: Dict[str, None] = {}
        for value in values:
            key = "" if pd.isna(value) else str(value)
            seen.setdefault(key, None)
        self.classes_ = list(seen.keys())
        self.class_to_index_ = {label: index for index, label in enumerate(self.classes_)}
        return self

    def transform(self, values: Iterable[object]) -> pd.Series:
        normalized = pd.Series(list(values), dtype="object").map(
            lambda value: "" if pd.isna(value) else str(value)
        )
        return normalized.map(self.class_to_index_).fillna(-1).astype(int)


@dataclass
class TrainingArtifacts:
    match_winner_accuracy: float
    match_winner_balanced_accuracy: float
    over_under_accuracy: float
    over_under_balanced_accuracy: float
    parity_accuracy: float
    parity_balanced_accuracy: float
    home_goals_mae: float
    away_goals_mae: float
    total_goals_mae: float
    total_rows: int
    train_rows: int
    test_rows: int
    output_dir: Path
    report_path: Path


def normalize_league_name(value: str) -> str:
    value = (value or "").strip()
    lowered = value.lower()
    if "penalty" in lowered:
        return "Penalty"
    if "3x3" in lowered:
        return "3x3"
    if "4x4" in lowered:
        return "4x4"
    if "5x5" in lowered:
        return "5x5"
    return value


def safe_time_split_index(total_rows: int, train_ratio: float, min_test_rows: int = 1) -> int:
    if not 0 < train_ratio < 1:
        raise ValueError("--train-ratio must be a float strictly between 0 and 1.")
    if total_rows < 2:
        raise ValueError("The dataset must contain at least 2 rows after cleaning.")

    split_idx = int(total_rows * train_ratio)
    split_idx = max(1, split_idx)
    split_idx = min(total_rows - min_test_rows, split_idx)

    if split_idx < 1 or split_idx >= total_rows:
        raise ValueError("Unable to create a valid train/test split with the current dataset size.")

    return split_idx


def prepare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    df["finished_at"] = pd.to_datetime(df["finished_at"], errors="coerce", utc=True)
    df = df.sort_values("finished_at").reset_index(drop=True)
    return df


def build_features(
    dataframe: pd.DataFrame,
    encoder_source_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, Dict[str, SafeLabelEncoder]]:
    df = dataframe.copy()

    df["league_group"] = df["league"].map(normalize_league_name)
    df["total_goals"] = df["score_home"] + df["score_away"]
    df["goal_diff"] = df["score_home"] - df["score_away"]
    df["winner"] = df["goal_diff"].apply(lambda goal_diff: "home" if goal_diff > 0 else "away" if goal_diff < 0 else "draw")
    df["over_under_2_5"] = (df["total_goals"] > 2).astype(int)
    df["total_goals_parity"] = (df["total_goals"] % 2).astype(int)
    df["hour"] = df["finished_at"].dt.hour.fillna(0).astype(int)
    df["day_of_week"] = df["finished_at"].dt.dayofweek.fillna(0).astype(int)

    encoder_source_df = encoder_source_df if encoder_source_df is not None else df
    encoder_league_group_source = encoder_source_df["league"].map(normalize_league_name)

    team_home_encoder = SafeLabelEncoder().fit(encoder_source_df["team_home"])
    team_away_encoder = SafeLabelEncoder().fit(encoder_source_df["team_away"])
    league_encoder = SafeLabelEncoder().fit(encoder_source_df["league"])
    league_group_encoder = SafeLabelEncoder().fit(encoder_league_group_source)

    df["team_home_encoded"] = team_home_encoder.transform(df["team_home"])
    df["team_away_encoded"] = team_away_encoder.transform(df["team_away"])
    df["league_encoded"] = league_encoder.transform(df["league"])
    df["league_group_encoded"] = league_group_encoder.transform(df["league_group"])

    team_stats: Dict[str, Dict[str, int]] = {}
    head_to_head_stats: Dict[Tuple[str, str], Dict[str, int]] = {}

    home_form = []
    away_form = []
    home_attack = []
    away_attack = []
    home_defense = []
    away_defense = []
    head_to_head = []
    head_to_head_home_winrate = []

    for _, row in df.iterrows():
        home_team = row["team_home"]
        away_team = row["team_away"]
        matchup_key = tuple(sorted([home_team, away_team]))

        home_snapshot = team_stats.get(home_team, {"matches": 0, "wins": 0, "goals_for": 0, "goals_against": 0})
        away_snapshot = team_stats.get(away_team, {"matches": 0, "wins": 0, "goals_for": 0, "goals_against": 0})
        h2h_snapshot = head_to_head_stats.get(matchup_key, {"matches": 0, "home_wins": 0, "away_wins": 0, "draws": 0})

        home_form.append(home_snapshot["wins"] / home_snapshot["matches"] if home_snapshot["matches"] else 0.5)
        away_form.append(away_snapshot["wins"] / away_snapshot["matches"] if away_snapshot["matches"] else 0.5)
        home_attack.append(home_snapshot["goals_for"] / home_snapshot["matches"] if home_snapshot["matches"] else 1.5)
        away_attack.append(away_snapshot["goals_for"] / away_snapshot["matches"] if away_snapshot["matches"] else 1.5)
        home_defense.append(home_snapshot["goals_against"] / home_snapshot["matches"] if home_snapshot["matches"] else 1.5)
        away_defense.append(away_snapshot["goals_against"] / away_snapshot["matches"] if away_snapshot["matches"] else 1.5)
        head_to_head.append(h2h_snapshot["matches"])
        head_to_head_home_winrate.append(h2h_snapshot["home_wins"] / h2h_snapshot["matches"] if h2h_snapshot["matches"] else 0.5)

        winner = row["winner"]
        score_home = int(row["score_home"])
        score_away = int(row["score_away"])

        if winner == "home":
            home_snapshot["wins"] += 1
            h2h_snapshot["home_wins"] += 1
        elif winner == "away":
            away_snapshot["wins"] += 1
            h2h_snapshot["away_wins"] += 1
        else:
            h2h_snapshot["draws"] += 1

        home_snapshot["matches"] += 1
        away_snapshot["matches"] += 1
        home_snapshot["goals_for"] += score_home
        home_snapshot["goals_against"] += score_away
        away_snapshot["goals_for"] += score_away
        away_snapshot["goals_against"] += score_home
        h2h_snapshot["matches"] += 1

        team_stats[home_team] = home_snapshot
        team_stats[away_team] = away_snapshot
        head_to_head_stats[matchup_key] = h2h_snapshot

    df["home_form_rate"] = home_form
    df["away_form_rate"] = away_form
    df["home_attack_avg"] = home_attack
    df["away_attack_avg"] = away_attack
    df["home_defense_avg"] = home_defense
    df["away_defense_avg"] = away_defense
    df["head_to_head_matches"] = head_to_head
    df["head_to_head_home_winrate"] = head_to_head_home_winrate

    encoders = {
        "team_home": team_home_encoder,
        "team_away": team_away_encoder,
        "league": league_encoder,
        "league_group": league_group_encoder,
    }

    return df, encoders


def train_models(csv_path: Path, output_dir: Path, train_ratio: float = 0.8) -> TrainingArtifacts:
    df = pd.read_csv(csv_path)
    df["score_home"] = pd.to_numeric(df["score_home"], errors="coerce")
    df["score_away"] = pd.to_numeric(df["score_away"], errors="coerce")
    df = df.dropna(subset=["team_home", "team_away", "league", "score_home", "score_away"]).copy()
    df["score_home"] = df["score_home"].astype(int)
    df["score_away"] = df["score_away"].astype(int)
    df = shared_prepare_training_dataframe(df)

    split_idx = safe_time_split_index(len(df), train_ratio=train_ratio)
    encoder_source_df = df.iloc[:split_idx].copy()
    featured_df, encoders = shared_build_training_features(df, encoder_source_df=encoder_source_df)

    feature_columns = FEATURE_COLUMNS

    output_dir.mkdir(parents=True, exist_ok=True)

    winner_model = RandomForestClassifier(n_estimators=300, max_depth=14, min_samples_leaf=3, random_state=42, n_jobs=-1)
    over_under_model = RandomForestClassifier(n_estimators=250, max_depth=12, min_samples_leaf=4, random_state=42, n_jobs=-1)
    parity_model = RandomForestClassifier(n_estimators=250, max_depth=12, min_samples_leaf=4, random_state=42, n_jobs=-1)
    home_goals_model = RandomForestRegressor(n_estimators=300, max_depth=14, min_samples_leaf=3, random_state=42, n_jobs=-1)
    away_goals_model = RandomForestRegressor(n_estimators=300, max_depth=14, min_samples_leaf=3, random_state=42, n_jobs=-1)
    total_goals_model = RandomForestRegressor(n_estimators=300, max_depth=14, min_samples_leaf=3, random_state=42, n_jobs=-1)

    X = featured_df[feature_columns]
    y_winner = featured_df["winner"]
    y_over_under = featured_df["over_under_2_5"]
    y_parity = featured_df["total_goals_parity"]
    y_home_goals = featured_df["score_home"]
    y_away_goals = featured_df["score_away"]
    y_total_goals = featured_df["total_goals"]

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train_winner, y_test_winner = y_winner.iloc[:split_idx], y_winner.iloc[split_idx:]
    y_train_ou, y_test_ou = y_over_under.iloc[:split_idx], y_over_under.iloc[split_idx:]
    y_train_parity, y_test_parity = y_parity.iloc[:split_idx], y_parity.iloc[split_idx:]
    y_train_home, y_test_home = y_home_goals.iloc[:split_idx], y_home_goals.iloc[split_idx:]
    y_train_away, y_test_away = y_away_goals.iloc[:split_idx], y_away_goals.iloc[split_idx:]
    y_train_total, y_test_total = y_total_goals.iloc[:split_idx], y_total_goals.iloc[split_idx:]

    winner_model.fit(X_train, y_train_winner)
    winner_predictions = winner_model.predict(X_test)
    winner_accuracy = accuracy_score(y_test_winner, winner_predictions)
    winner_balanced_accuracy = balanced_accuracy_score(y_test_winner, winner_predictions)

    over_under_model.fit(X_train, y_train_ou)
    over_under_predictions = over_under_model.predict(X_test)
    over_under_accuracy = accuracy_score(y_test_ou, over_under_predictions)
    over_under_balanced_accuracy = balanced_accuracy_score(y_test_ou, over_under_predictions)

    parity_model.fit(X_train, y_train_parity)
    parity_predictions = parity_model.predict(X_test)
    parity_accuracy = accuracy_score(y_test_parity, parity_predictions)
    parity_balanced_accuracy = balanced_accuracy_score(y_test_parity, parity_predictions)

    home_goals_model.fit(X_train, y_train_home)
    home_goals_predictions = home_goals_model.predict(X_test)
    home_goals_mae = mean_absolute_error(y_test_home, home_goals_predictions)

    away_goals_model.fit(X_train, y_train_away)
    away_goals_predictions = away_goals_model.predict(X_test)
    away_goals_mae = mean_absolute_error(y_test_away, away_goals_predictions)

    total_goals_model.fit(X_train, y_train_total)
    total_goals_predictions = total_goals_model.predict(X_test)
    total_goals_mae = mean_absolute_error(y_test_total, total_goals_predictions)

    trained_at = datetime.utcnow().isoformat()

    payloads = {
        "match_winner.joblib": {
            "model": winner_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "accuracy": float(winner_accuracy),
            "balanced_accuracy": float(winner_balanced_accuracy),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "match_winner",
        },
        "over_under_2.5.joblib": {
            "model": over_under_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "accuracy": float(over_under_accuracy),
            "balanced_accuracy": float(over_under_balanced_accuracy),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "over_under_2.5",
        },
        "total_goals_parity.joblib": {
            "model": parity_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "accuracy": float(parity_accuracy),
            "balanced_accuracy": float(parity_balanced_accuracy),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "total_goals_parity",
        },
        "team_home_goals.joblib": {
            "model": home_goals_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "mae": float(home_goals_mae),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "team_home_goals",
        },
        "team_away_goals.joblib": {
            "model": away_goals_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "mae": float(away_goals_mae),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "team_away_goals",
        },
        "match_total_goals.joblib": {
            "model": total_goals_model,
            "label_encoders": encoders,
            "feature_columns": feature_columns,
            "mae": float(total_goals_mae),
            "trained_at": trained_at,
            "model_type": "random_forest_csv_baseline",
            "target": "match_total_goals",
        },
    }

    for filename, payload in payloads.items():
        joblib.dump(payload, output_dir / filename)

    report_path = output_dir / "training_report.json"
    report = {
        "csv_path": str(csv_path),
        "trained_at": trained_at,
        "train_ratio": train_ratio,
        "total_rows": len(featured_df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "metrics": {
            "match_winner": {
                "accuracy": float(winner_accuracy),
                "balanced_accuracy": float(winner_balanced_accuracy),
            },
            "over_under_2_5": {
                "accuracy": float(over_under_accuracy),
                "balanced_accuracy": float(over_under_balanced_accuracy),
            },
            "total_goals_parity": {
                "accuracy": float(parity_accuracy),
                "balanced_accuracy": float(parity_balanced_accuracy),
            },
            "team_home_goals": {
                "mae": float(home_goals_mae),
            },
            "team_away_goals": {
                "mae": float(away_goals_mae),
            },
            "match_total_goals": {
                "mae": float(total_goals_mae),
            },
        },
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    return TrainingArtifacts(
        match_winner_accuracy=float(winner_accuracy),
        match_winner_balanced_accuracy=float(winner_balanced_accuracy),
        over_under_accuracy=float(over_under_accuracy),
        over_under_balanced_accuracy=float(over_under_balanced_accuracy),
        parity_accuracy=float(parity_accuracy),
        parity_balanced_accuracy=float(parity_balanced_accuracy),
        home_goals_mae=float(home_goals_mae),
        away_goals_mae=float(away_goals_mae),
        total_goals_mae=float(total_goals_mae),
        total_rows=len(featured_df),
        train_rows=len(X_train),
        test_rows=len(X_test),
        output_dir=output_dir,
        report_path=report_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline models from a finished matches CSV.")
    parser.add_argument("--csv", required=True, help="Path to the finished matches CSV")
    parser.add_argument("--output-dir", default="app/models", help="Output directory for .joblib models")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Fraction of oldest rows used for training")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifacts = train_models(Path(args.csv), Path(args.output_dir), train_ratio=args.train_ratio)
    print("Training complete")
    print(f"Rows used: {artifacts.total_rows}")
    print(f"Train rows: {artifacts.train_rows}")
    print(f"Test rows: {artifacts.test_rows}")
    print(f"match_winner accuracy: {artifacts.match_winner_accuracy:.4f}")
    print(f"match_winner balanced accuracy: {artifacts.match_winner_balanced_accuracy:.4f}")
    print(f"over_under_2.5 accuracy: {artifacts.over_under_accuracy:.4f}")
    print(f"over_under_2.5 balanced accuracy: {artifacts.over_under_balanced_accuracy:.4f}")
    print(f"total_goals_parity accuracy: {artifacts.parity_accuracy:.4f}")
    print(f"total_goals_parity balanced accuracy: {artifacts.parity_balanced_accuracy:.4f}")
    print(f"team_home_goals MAE: {artifacts.home_goals_mae:.4f}")
    print(f"team_away_goals MAE: {artifacts.away_goals_mae:.4f}")
    print(f"match_total_goals MAE: {artifacts.total_goals_mae:.4f}")
    print(f"Models saved in: {artifacts.output_dir}")
    print(f"Training report: {artifacts.report_path}")


if __name__ == "__main__":
    main()
