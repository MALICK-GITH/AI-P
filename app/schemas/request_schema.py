from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    league: str = Field(..., min_length=2, max_length=120)
    home_team: str = Field(..., alias="homeTeam", min_length=1, max_length=120)
    away_team: str = Field(..., alias="awayTeam", min_length=1, max_length=120)
    home_odds: float = Field(..., gt=1.0, le=1000.0)
    draw_odds: float = Field(..., gt=1.0, le=1000.0)
    away_odds: float = Field(..., gt=1.0, le=1000.0)

    match_datetime: datetime | None = Field(
        default=None,
        description="Optional kickoff date/time. Defaults to current UTC when omitted.",
    )
    home_form_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    away_form_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    home_attack_avg: float = Field(default=1.5, ge=0.0, le=20.0)
    away_attack_avg: float = Field(default=1.5, ge=0.0, le=20.0)
    home_defense_avg: float = Field(default=1.5, ge=0.0, le=20.0)
    away_defense_avg: float = Field(default=1.5, ge=0.0, le=20.0)
    head_to_head_matches: int = Field(default=0, ge=0, le=1000)
    head_to_head_home_winrate: float = Field(default=0.5, ge=0.0, le=1.0)

