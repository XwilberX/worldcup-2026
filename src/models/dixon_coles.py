"""Dixon-Coles model for football match score prediction.

Based on: Dixon, M.J. and Coles, S.G. (1997)
"Modelling Association Football Scores and Inefficiencies in the Football Betting Market"
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson
from typing import Dict, Tuple
import itertools


class DixonColes:
    """
    Dixon-Coles Poisson regression model for football scores.

    Each team i has parameters:
    - attack_i: attacking strength
    - defense_i: defensive weakness (higher = worse defense)

    lambda_home = home_advantage * attack_home * defense_away
    lambda_away = attack_away * defense_home

    With Dixon-Coles correction for low-scores (0-0, 1-0, 0-1, 1-1).
    """

    def __init__(self, rho: float = 0.0, home_advantage: float = 1.0):
        self.rho = rho
        self.home_advantage = home_advantage
        self.attack: Dict[str, float] = {}
        self.defense: Dict[str, float] = {}
        self.teams: list = []

    def fit(
        self,
        df: pd.DataFrame,
        decay_half_life_days: float = 365 * 3,
        min_matches: int = 10,
        verbose: bool = True,
    ):
        """
        Fit the model to match data using Maximum Likelihood Estimation.
        Uses exponential time decay for match weights.

        Identifiability constraints:
        - First team's attack = 0 (baseline)
        - Mean defense = 0
        """
        # Filter teams with enough matches
        match_counts = {}
        for _, row in df.iterrows():
            match_counts[row["home_team"]] = match_counts.get(row["home_team"], 0) + 1
            match_counts[row["away_team"]] = match_counts.get(row["away_team"], 0) + 1

        valid_teams = {t for t, c in match_counts.items() if c >= min_matches}
        df = df[df["home_team"].isin(valid_teams) & df["away_team"].isin(valid_teams)].copy()

        self.teams = sorted(valid_teams)
        n_teams = len(self.teams)
        team_to_idx = {t: i for i, t in enumerate(self.teams)}

        if verbose:
            print(f"Fitting Dixon-Coles on {len(df)} matches, {n_teams} teams")

        # Compute time weights
        max_date = df["date"].max()
        df["days_ago"] = (max_date - df["date"]).dt.days
        df["weight"] = np.exp(-np.log(2) * df["days_ago"] / decay_half_life_days)

        goals_home = df["home_score"].values.astype(float)
        goals_away = df["away_score"].values.astype(float)
        weights = df["weight"].values

        hi_idx = np.array([team_to_idx[t] for t in df["home_team"]])
        ai_idx = np.array([team_to_idx[t] for t in df["away_team"]])

        # Parameters: home_adv + attack[1:] + defense + rho
        # attack[0] is fixed to 0
        n_params = 1 + (n_teams - 1) + n_teams + 1
        # Index layout:
        # 0: home_adv
        # 1 to n_teams: attack[1:] (attack[0]=0)
        # n_teams to 2*n_teams-1: defense
        # 2*n_teams-1: rho

        def inflate_attack(attack_compact):
            full = np.zeros(n_teams)
            full[1:] = attack_compact
            return full

        def neg_log_likelihood(params):
            home_adv = params[0]
            attack = inflate_attack(params[1:n_teams])
            defense = np.array(params[n_teams:2*n_teams])
            rho = params[-1]

            log_lambda_home = home_adv + attack[hi_idx] - defense[ai_idx]
            log_lambda_away = attack[ai_idx] - defense[hi_idx]

            lambda_home = np.exp(np.clip(log_lambda_home, -10, 5))
            lambda_away = np.exp(np.clip(log_lambda_away, -10, 5))

            ll = goals_home * np.log(np.maximum(lambda_home, 1e-10)) - lambda_home
            ll += goals_away * np.log(np.maximum(lambda_away, 1e-10)) - lambda_away

            tau = np.ones(len(df))
            mask_00 = (goals_home == 0) & (goals_away == 0)
            tau[mask_00] = 1.0 - lambda_home[mask_00] * lambda_away[mask_00] * rho
            mask_10 = (goals_home == 1) & (goals_away == 0)
            tau[mask_10] = 1.0 + lambda_home[mask_10] * rho
            mask_01 = (goals_home == 0) & (goals_away == 1)
            tau[mask_01] = 1.0 + lambda_away[mask_01] * rho
            mask_11 = (goals_home == 1) & (goals_away == 1)
            tau[mask_11] = 1.0 - rho

            tau = np.maximum(tau, 1e-10)
            ll += np.log(tau)

            # Penalties for constraints
            defense_penalty = 500.0 * np.mean(defense) ** 2

            return -np.sum(weights * ll) + defense_penalty

        init = np.zeros(n_params)
        init[0] = 0.3   # home advantage (log scale)
        init[-1] = -0.05 # rho

        result = minimize(
            neg_log_likelihood,
            init,
            method="L-BFGS-B",
            options={"maxiter": 20000, "disp": False},
        )

        self.home_advantage = np.exp(result.x[0])
        attack_full = inflate_attack(result.x[1:n_teams])
        self.attack = {t: attack_full[i] for i, t in enumerate(self.teams)}
        self.defense = {t: result.x[n_teams + i] for i, t in enumerate(self.teams)}
        self.rho = result.x[-1]

        if verbose:
            print(f"  Home advantage: {self.home_advantage:.3f}")
            print(f"  Rho: {self.rho:.4f}")
            print(f"  Converged: {result.success}")
            top_a = sorted(self.attack.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  Top attacks: {', '.join(f'{t}({v:.2f})' for t,v in top_a)}")

        return self

    def predict_score_probs(
        self, home_team: str, away_team: str, max_goals: int = 6
    ) -> np.ndarray:
        """Return matrix of score probabilities P(score_home=x, score_away=y)."""
        a_home = self.attack.get(home_team, 0.0)
        d_home = self.defense.get(home_team, 0.0)
        a_away = self.attack.get(away_team, 0.0)
        d_away = self.defense.get(away_team, 0.0)

        log_lambda_home = np.log(self.home_advantage) + a_home - d_away
        log_lambda_away = a_away - d_home

        lambda_home = np.exp(np.clip(log_lambda_home, -10, 5))
        lambda_away = np.exp(np.clip(log_lambda_away, -10, 5))

        # Poisson probabilities
        range_g = np.arange(max_goals + 1)
        prob_home = poisson.pmf(range_g, lambda_home)
        prob_away = poisson.pmf(range_g, lambda_away)

        probs = np.outer(prob_home, prob_away)

        # Apply Dixon-Coles correction
        rho = self.rho
        # 0-0
        probs[0, 0] *= 1.0 - lambda_home * lambda_away * rho
        # 1-0
        if max_goals >= 1:
            probs[1, 0] *= 1.0 + lambda_home * rho
        # 0-1
        if max_goals >= 1:
            probs[0, 1] *= 1.0 + lambda_away * rho
        # 1-1
        if max_goals >= 1:
            probs[1, 1] *= 1.0 - rho

        probs = np.maximum(probs, 0.0)
        probs /= probs.sum()
        return probs

    def predict_match(self, home_team: str, away_team: str) -> dict:
        """Predict match outcome probabilities and most likely scores."""
        probs = self.predict_score_probs(home_team, away_team, max_goals=8)

        win = draw = loss = 0.0
        for i in range(probs.shape[0]):
            for j in range(probs.shape[1]):
                if i > j:
                    win += probs[i, j]
                elif i == j:
                    draw += probs[i, j]
                else:
                    loss += probs[i, j]

        return {
            "home_team": home_team,
            "away_team": away_team,
            "prob_home_win": float(win),
            "prob_draw": float(draw),
            "prob_away_win": float(loss),
            "most_likely_score": self.most_likely_score(probs),
        }

    def most_likely_score(self, probs: np.ndarray) -> str:
        """Return the most likely score as string 'X-Y'."""
        idx = np.unravel_index(np.argmax(probs), probs.shape)
        return f"{idx[0]}-{idx[1]}"

    def sample_match(self, home_team: str, away_team: str) -> Tuple[int, int]:
        """Sample a match outcome from the predicted distribution."""
        probs = self.predict_score_probs(home_team, away_team, max_goals=10)
        flat = probs.flatten()
        idx = np.random.choice(len(flat), p=flat)
        i, j = np.unravel_index(idx, probs.shape)
        return int(i), int(j)
