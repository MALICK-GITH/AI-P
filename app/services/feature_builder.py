from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Sequence, Tuple

import pandas as pd

from app.schemas.request_schema import PredictionRequest


FEATURE_COLUMNS: list[str] = [
    "team_home_encoded",
    "team_away_encoded",
    "league_encoded",
    "league_group_encoded",
    "home_form_rate",
    "away_form_rate",
    "home_attack_avg",
    "away_attack_avg",
    "home_defense_avg",
    "away_defense_avg",
    "head_to_head_matches",
    "head_to_head_home_winrate",
    "hour",
    "day_of_week",
]

LEAGUE_GROUP_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("penalty", "Penalty"),
    ("3x3", "3x3"),
    ("4x4", "4x4"),
    ("5x5", "5x5"),
)


@dataclass
class SafeLabelEncoder:
    classes_: list[str] = field(default_factory=list)
    class_to_index_: dict[str, int] = field(default_factory=dict)

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


@dataclass(frozen=True)
class FeatureVector:
    team_home_encoded: int
    team_away_encoded: int
    league_encoded: int
    league_group_encoded: int
    home_form_rate: float
    away_form_rate: float
    home_attack_avg: float
    away_attack_avg: float
    home_defense_avg: float
    away_defense_avg: float
    head_to_head_matches: int
    head_to_head_home_winrate: float
    hour: int
    day_of_week: int

    def to_dict(self) -> dict[str, object]:
        return {
            "team_home_encoded": self.team_home_encoded,
            "team_away_encoded": self.team_away_encoded,
            "league_encoded": self.league_encoded,
            "league_group_encoded": self.league_group_encoded,
            "home_form_rate": self.home_form_rate,
            "away_form_rate": self.away_form_rate,
            "home_attack_avg": self.home_attack_avg,
            "away_attack_avg": self.away_attack_avg,
            "home_defense_avg": self.home_defense_avg,
            "away_defense_avg": self.away_defense_avg,
            "head_to_head_matches": self.head_to_head_matches,
            "head_to_head_home_winrate": self.head_to_head_home_winrate,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
        }

    def to_frame(self, feature_columns: Sequence[str] | None = None) -> pd.DataFrame:
        frame = pd.DataFrame([self.to_dict()])
        if feature_columns is not None:
            return frame.loc[:, list(feature_columns)]
        return frame


def normalize_league_name(value: str) -> str:
    raw = (value or "").strip()
    lowered = raw.lower()
    for needle, normalized in LEAGUE_GROUP_KEYWORDS:
        if needle in lowered:
            return normalized
    return raw


def _safe_lookup(encoder: object, value: str) -> int:
    class_to_index = getattr(encoder, "class_to_index_", None)
    if isinstance(class_to_index, dict):
        return int(class_to_index.get(value, -1))

    classes = getattr(encoder, "classes_", None)
    if isinstance(classes, list) and value in classes:
        return int(classes.index(value))

    return -1


def _build_team_history_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()

    df["league_group"] = df["league"].map(normalize_league_name)
    df["total_goals"] = df["score_home"] + df["score_away"]
    df["goal_diff"] = df["score_home"] - df["score_away"]
    df["winner"] = df["goal_diff"].apply(
        lambda goal_diff: "home" if goal_diff > 0 else "away" if goal_diff < 0 else "draw"
    )
    df["over_under_2_5"] = (df["total_goals"] > 2).astype(int)
    df["total_goals_parity"] = (df["total_goals"] % 2).astype(int)
    df["hour"] = df["finished_at"].dt.hour.fillna(0).astype(int)
    df["day_of_week"] = df["finished_at"].dt.dayofweek.fillna(0).astype(int)

    team_stats: Dict[str, Dict[str, int]] = {}
    head_to_head_stats: Dict[Tuple[str, str], Dict[str, int]] = {}

    home_form: list[float] = []
    away_form: list[float] = []
    home_attack: list[float] = []
    away_attack: list[float] = []
    home_defense: list[float] = []
    away_defense: list[float] = []
    head_to_head: list[int] = []
    head_to_head_home_winrate: list[float] = []

    for _, row in df.iterrows():
        home_team = row["team_home"]
        away_team = row["team_away"]
        matchup_key = tuple(sorted([home_team, away_team]))

        home_snapshot = team_stats.get(
            home_team,
            {"matches": 0, "wins": 0, "goals_for": 0, "goals_against": 0},
        )
        away_snapshot = team_stats.get(
            away_team,
            {"matches": 0, "wins": 0, "goals_for": 0, "goals_against": 0},
        )
        h2h_snapshot = head_to_head_stats.get(
            matchup_key,
            {"matches": 0, "home_wins": 0, "away_wins": 0, "draws": 0},
        )

        home_form.append(home_snapshot["wins"] / home_snapshot["matches"] if home_snapshot["matches"] else 0.5)
        away_form.append(away_snapshot["wins"] / away_snapshot["matches"] if away_snapshot["matches"] else 0.5)
        home_attack.append(
            home_snapshot["goals_for"] / home_snapshot["matches"] if home_snapshot["matches"] else 1.5
        )
        away_attack.append(
            away_snapshot["goals_for"] / away_snapshot["matches"] if away_snapshot["matches"] else 1.5
        )
        home_defense.append(
            home_snapshot["goals_against"] / home_snapshot["matches"] if home_snapshot["matches"] else 1.5
        )
        away_defense.append(
            away_snapshot["goals_against"] / away_snapshot["matches"] if away_snapshot["matches"] else 1.5
        )
        head_to_head.append(h2h_snapshot["matches"])
        head_to_head_home_winrate.append(
            h2h_snapshot["home_wins"] / h2h_snapshot["matches"] if h2h_snapshot["matches"] else 0.5
        )

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
    return df


def prepare_training_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    df["finished_at"] = pd.to_datetime(df["finished_at"], errors="coerce", utc=True)
    return df.sort_values("finished_at").reset_index(drop=True)


def build_training_features(
    dataframe: pd.DataFrame,
    encoder_source_df: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, SafeLabelEncoder]]:
    df = _build_team_history_features(dataframe)

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

    encoders = {
        "team_home": team_home_encoder,
        "team_away": team_away_encoder,
        "league": league_encoder,
        "league_group": league_group_encoder,
    }
    return df, encoders


class FeatureBuilder:
    def __init__(self, feature_columns: Sequence[str], label_encoders: Mapping[str, object]) -> None:
        self._feature_columns = tuple(feature_columns)
        self._label_encoders = dict(label_encoders)

    @property
    def feature_columns(self) -> tuple[str, ...]:
        return self._feature_columns

    @classmethod
    def from_registry(cls, registry: object, model_name: str = "over_under_2.5.joblib") -> "FeatureBuilder":
        artifact = registry.get(model_name) if hasattr(registry, "get") else registry.get_model(model_name)
        return cls(feature_columns=artifact.feature_columns, label_encoders=artifact.label_encoders)

    def build_vector(self, request: PredictionRequest) -> FeatureVector:
        league_group = normalize_league_name(request.league)
        current_dt = request.match_datetime or datetime.now(timezone.utc)

        team_home = request.home_team.strip()
        team_away = request.away_team.strip()
        league = request.league.strip()

        team_home_encoded = _safe_lookup(self._label_encoders.get("team_home"), team_home)
        team_away_encoded = _safe_lookup(self._label_encoders.get("team_away"), team_away)
        league_encoded = _safe_lookup(self._label_encoders.get("league"), league)
        league_group_encoded = _safe_lookup(self._label_encoders.get("league_group"), league_group)

        return FeatureVector(
            team_home_encoded=team_home_encoded,
            team_away_encoded=team_away_encoded,
            league_encoded=league_encoded,
            league_group_encoded=league_group_encoded,
            home_form_rate=request.home_form_rate,
            away_form_rate=request.away_form_rate,
            home_attack_avg=request.home_attack_avg,
            away_attack_avg=request.away_attack_avg,
            home_defense_avg=request.home_defense_avg,
            away_defense_avg=request.away_defense_avg,
            head_to_head_matches=request.head_to_head_matches,
            head_to_head_home_winrate=request.head_to_head_home_winrate,
            hour=current_dt.hour,
            day_of_week=current_dt.weekday(),
        )

    def build_frame(self, request: PredictionRequest) -> pd.DataFrame:
        return self.build_vector(request).to_frame(self._feature_columns)

    def build_frame_from_vector(self, vector: FeatureVector) -> pd.DataFrame:
        return vector.to_frame(self._feature_columns)
