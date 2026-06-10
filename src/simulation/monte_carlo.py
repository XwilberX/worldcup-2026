"""Monte Carlo simulation for the 2026 World Cup tournament."""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import random

from src.simulation.tournament import simulate_group, rank_group, select_best_thirds


def simulate_single_tournament(
    groups: Dict[str, List[str]],
    model,
    seed: int = None,
) -> Dict[str, dict]:
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    all_teams = []
    for g in groups.values():
        all_teams.extend(g)

    results = {t: {"champion": False, "runner_up": False, "third": False,
                   "semifinalist": False, "quarterfinalist": False,
                   "round_of_16": False, "round_of_32": False, "group_stage": False}
               for t in all_teams}

    # --- Group stage ---
    all_group_rankings = {}
    group_of_team = {}
    for group_name, teams in groups.items():
        standings = simulate_group(teams, model, group_name)
        ranking = rank_group(standings)
        all_group_rankings[group_name] = ranking
        for rank, (team, _) in enumerate(ranking):
            group_of_team[team] = (group_name, rank)

    # Advancing teams
    advancing = []
    for _, ranking in all_group_rankings.items():
        advancing.append(ranking[0][0])
        advancing.append(ranking[1][0])

    best_thirds = select_best_thirds(all_group_rankings)
    advancing.extend(best_thirds)

    for t in advancing:
        results[t]["round_of_32"] = True
    for t in all_teams:
        if t not in advancing:
            results[t]["group_stage"] = True

    # --- Build R32 bracket ---
    group_winners = [ranking[0][0] for _, ranking in all_group_rankings.items()]
    other_teams = [ranking[1][0] for _, ranking in all_group_rankings.items()] + best_thirds
    random.shuffle(other_teams)

    # Pair winners vs others avoiding same-group
    r32_pairs = []
    used_others = set()
    for w in group_winners:
        w_group = group_of_team[w][0]
        for o in other_teams:
            if o not in used_others and group_of_team[o][0] != w_group:
                r32_pairs.append((w, o))
                used_others.add(o)
                break

    # Remaining teams paired randomly
    remaining = [o for o in other_teams if o not in used_others]
    random.shuffle(remaining)
    while len(remaining) >= 2:
        r32_pairs.append((remaining.pop(), remaining.pop()))

    # --- Simulate knockout tree ---
    current_teams = []
    for a, b in r32_pairs:
        winner = simulate_knockout_match(a, b, model)
        current_teams.append(winner)
        results[a]["round_of_16"] = True
        results[b]["round_of_16"] = True

    # R16: current_teams should be 16
    random.shuffle(current_teams)
    qf_participants = list(current_teams)
    next_round = []
    for i in range(0, len(current_teams), 2):
        if i + 1 >= len(current_teams):
            break
        winner = simulate_knockout_match(current_teams[i], current_teams[i + 1], model)
        next_round.append(winner)

    for t in qf_participants:
        results[t]["quarterfinalist"] = True

    # QF: next_round should be 8
    current_teams = next_round
    random.shuffle(current_teams)
    sf_participants = list(current_teams)
    next_round = []
    for i in range(0, len(current_teams), 2):
        if i + 1 >= len(current_teams):
            break
        winner = simulate_knockout_match(current_teams[i], current_teams[i + 1], model)
        next_round.append(winner)

    for t in sf_participants:
        results[t]["semifinalist"] = True

    # SF: next_round should be 4
    if len(next_round) >= 4:
        sf1_win = simulate_knockout_match(next_round[0], next_round[1], model)
        sf2_win = simulate_knockout_match(next_round[2], next_round[3], model)
        sf_losers = [t for t in next_round if t not in (sf1_win, sf2_win)]

        # Third place
        if len(sf_losers) >= 2:
            third = simulate_knockout_match(sf_losers[0], sf_losers[1], model)
            results[third]["third"] = True

        # Final
        champion = simulate_knockout_match(sf1_win, sf2_win, model)
        runner_up = sf2_win if champion == sf1_win else sf1_win
        results[champion]["champion"] = True
        results[runner_up]["runner_up"] = True

    return results


def simulate_knockout_match(team_a: str, team_b: str, model) -> str:
    pred = model.predict_match(team_a, team_b)
    r = np.random.random()
    if r < pred["prob_home_win"]:
        return team_a
    elif r < pred["prob_home_win"] + pred["prob_draw"]:
        return team_a if np.random.random() < 0.5 else team_b
    else:
        return team_b


def monte_carlo_simulation(
    groups: Dict[str, List[str]],
    model,
    n_simulations: int = 10000,
    n_workers: int = 4,
    show_progress: bool = True,
) -> pd.DataFrame:
    all_teams = []
    for g in groups.values():
        all_teams.extend(g)

    counts = {t: {"champion": 0, "runner_up": 0, "third": 0,
                   "semifinalist": 0, "quarterfinalist": 0,
                   "round_of_16": 0, "round_of_32": 0, "group_stage": 0}
              for t in all_teams}

    for i in range(n_simulations):
        if show_progress and (i + 1) % 1000 == 0:
            print(f"  Simulated {i + 1}/{n_simulations} tournaments...")

        result = simulate_single_tournament(groups, model, seed=i)
        for team, stages in result.items():
            for stage, reached in stages.items():
                if reached:
                    counts[team][stage] += 1

    rows = []
    for team, stage_counts in counts.items():
        row = {"team": team}
        for stage in ["champion", "runner_up", "third", "semifinalist",
                       "quarterfinalist", "round_of_16", "round_of_32", "group_stage"]:
            row[stage] = stage_counts[stage] / n_simulations
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values("champion", ascending=False).reset_index(drop=True)
    return df
