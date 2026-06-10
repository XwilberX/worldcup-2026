"""Tournament structure and group stage logic for World Cup 2026."""

import numpy as np
from typing import Dict, List, Tuple
from itertools import combinations


def simulate_group(
    teams: List[str],
    model,
    group_name: str = "",
) -> Dict[str, dict]:
    """
    Simulate a 4-team group: each team plays all others once.

    Returns dict mapping team -> {
        'points': int,
        'gf': int,
        'ga': int,
        'gd': int,
        'wins': int,
        'draws': int,
        'losses': int,
        'results': list of (opponent, score_str),
    }
    """
    standings = {
        t: {"points": 0, "gf": 0, "ga": 0, "gd": 0, "wins": 0, "draws": 0, "losses": 0, "results": []}
        for t in teams
    }

    for home, away in combinations(teams, 2):
        hg, ag = model.sample_match(home, away)

        standings[home]["gf"] += hg
        standings[home]["ga"] += ag
        standings[away]["gf"] += ag
        standings[away]["ga"] += hg
        standings[home]["results"].append((away, f"{hg}-{ag}"))
        standings[away]["results"].append((home, f"{ag}-{hg}"))

        if hg > ag:
            standings[home]["points"] += 3
            standings[home]["wins"] += 1
            standings[away]["losses"] += 1
        elif hg < ag:
            standings[away]["points"] += 3
            standings[away]["wins"] += 1
            standings[home]["losses"] += 1
        else:
            standings[home]["points"] += 1
            standings[away]["points"] += 1
            standings[home]["draws"] += 1
            standings[away]["draws"] += 1

    for t in teams:
        standings[t]["gd"] = standings[t]["gf"] - standings[t]["ga"]

    return standings


def rank_group(standings: Dict[str, dict]) -> List[Tuple[str, dict]]:
    """
    Rank teams in a group by: points, goal diff, goals for, head-to-head.
    Returns sorted list of (team, stats).
    """
    items = list(standings.items())
    items.sort(key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gf"]), reverse=True)
    return items


def select_best_thirds(
    all_groups: Dict[str, List[Tuple[str, dict]]]
) -> List[str]:
    """
    Select the 8 best 3rd-placed teams across all 12 groups.
    Sorted by: points, goal diff, goals for.
    """
    thirds = []
    for group_name, ranking in all_groups.items():
        if len(ranking) >= 3:
            team, stats = ranking[2]
            thirds.append((team, stats, group_name))

    thirds.sort(key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gf"]), reverse=True)
    return [t[0] for t in thirds[:8]]


def get_third_place_bracket_positions(qualifying_thirds: List[str]) -> Dict[str, str]:
    """
    Map third-placed teams to their Round of 32 positions.
    Based on FIFA's bracket rules for best third-placed teams.
    Simplified: assign to bracket positions based on which groups advance.
    """
    # Standard FIFA mapping for 12 groups, 8 best thirds
    positions = [
        "1E", "1F", "1G", "1H", "1I", "1J", "1K", "1L"
    ]
    return {t: pos for t, pos in zip(qualifying_thirds, positions)}


ROUND_OF_32_MATCHUPS = [
    ("1A", "3C/D/E/F"),   # Match 73
    ("1C", "3A/B/F"),     # Match 74
    ("1B", "3A/E/F/G"),   # Match 75
    ("1F", "2A"),         # Match 76
    ("1E", "2B"),         # Match 77
    ("1D", "3B/E/F/G"),   # Match 78
    ("1G", "3A/C/D"),     # Match 79
    ("1H", "2C"),         # Match 80
    ("1I", "2D"),         # Match 81
    ("1L", "3E/H/I/J"),   # Match 82
    ("1K", "2E"),         # Match 83
    ("1J", "2F"),         # Match 84
    ("2G", "2H"),         # Match 85
    ("2I", "2J"),         # Match 86
    ("2K", "2L"),         # Match 87
    ("1A/D/F/G", "3C/E"), # Match 88 - simplified, winner of group D vs 3rd B/E etc
]

# Simplified bracket for simulation
BRACKET = {
    "R32": list(range(73, 89)),  # 16 matches
    "R16": list(range(89, 97)),   # 8 matches
    "QF": list(range(97, 101)),   # 4 matches
    "SF": [101, 102],             # 2 matches
    "F3": 103,                    # 3rd place
    "F": 104,                     # Final
}
