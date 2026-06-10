"""Elo rating system for international football teams."""

import pandas as pd
import numpy as np
from typing import Dict


def compute_elo_history(
    df: pd.DataFrame,
    initial_elo: float = 1500.0,
    k: float = 30.0,
    home_advantage: float = 100.0,
    goal_diff_factor: float = 1.0,
) -> Dict[str, float]:
    """
    Compute Elo ratings for all teams over time.
    Returns a dict with final Elo for each team.

    Uses a modified Elo with:
    - Goal difference multiplier (larger wins = bigger rating changes)
    - Home advantage
    - Higher K for World Cup matches
    """
    elo = {}
    df = df.sort_values("date").copy()

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        hg = row["home_score"]
        ag = row["away_score"]
        is_neutral = row.get("neutral", False)
        tournament = row.get("tournament", "")

        if home not in elo:
            elo[home] = initial_elo
        if away not in elo:
            elo[away] = initial_elo

        r_home = elo[home]
        r_away = elo[away]

        # Adjust for home advantage
        if is_neutral and str(is_neutral).upper() != "TRUE":
            r_home += home_advantage
        elif not is_neutral or str(is_neutral).upper() == "FALSE":
            r_home += home_advantage

        # Expected score
        expected_home = 1.0 / (1.0 + 10 ** ((r_away - r_home) / 400.0))

        # Actual score
        if hg > ag:
            actual_home = 1.0
        elif hg < ag:
            actual_home = 0.0
        else:
            actual_home = 0.5

        # Goal difference multiplier
        goal_diff = abs(hg - ag)
        if goal_diff <= 1:
            g = 1.0
        elif goal_diff == 2:
            g = 1.5
        else:
            g = (11.0 + goal_diff) / 8.0

        # K-factor: higher for competitive matches
        k_match = k
        if "World Cup" in str(tournament) and "qualif" not in str(tournament).lower():
            k_match = k * 1.5
        elif "Copa América" in str(tournament) or "African Cup" in str(tournament):
            k_match = k * 1.2

        # Update Elo
        change = k_match * g * (actual_home - expected_home)
        elo[home] += change
        elo[away] -= change

    return elo


def get_elo_ratings(teams: list, elo: dict) -> dict:
    """Get Elo ratings for specific teams, defaulting to 1500 if not found."""
    return {t: elo.get(t, 1500.0) for t in teams}


def elo_win_probability(elo_a: float, elo_b: float, home_adv: float = 0.0) -> float:
    """Probability team A beats team B given Elo ratings."""
    return 1.0 / (1.0 + 10 ** ((elo_b - (elo_a + home_adv)) / 400.0))
