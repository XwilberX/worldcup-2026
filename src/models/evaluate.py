"""Backtesting and evaluation metrics for football prediction models."""

import numpy as np
import pandas as pd
from typing import Dict, List
from scipy.stats import poisson


def log_loss_score(actual: tuple, probs: np.ndarray) -> float:
    """Log-loss for a single match: -log(P(actual_score))."""
    hg, ag = actual
    if hg < probs.shape[0] and ag < probs.shape[1]:
        return -np.log(max(probs[hg, ag], 1e-15))
    return -np.log(1e-15)


def ranked_probability_score(
    model,
    df: pd.DataFrame,
) -> float:
    """
    RPS for football scores. Lower is better.
    Ranges from 0 (perfect) to 1 (worst).
    """
    total_rps = 0.0
    n = len(df)

    for _, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]
        actual_hg = int(row["home_score"])
        actual_ag = int(row["away_score"])
        max_g = max(6, actual_hg, actual_ag)

        probs = model.predict_score_probs(home, away, max_goals=max_g)

        # Cumulative distribution
        cum_pred = np.zeros((max_g + 2, max_g + 2))
        for i in range(max_g + 1):
            for j in range(max_g + 1):
                cum_pred[i, j] = probs[: i + 1, : j + 1].sum()

        cum_actual = np.zeros((max_g + 2, max_g + 2))
        cum_actual[actual_hg:, actual_ag:] = 1.0

        rps = np.sum((cum_pred - cum_actual) ** 2) / (max_g ** 2)
        total_rps += rps

    return total_rps / n


def backtest_temporal(
    df: pd.DataFrame,
    model_class,
    train_years: int = 3,
    test_window: str = "1Y",
    verbose: bool = True,
) -> Dict[str, float]:
    """
    Temporal backtesting: train on past N years, predict next window.
    """
    from src.models.dixon_coles import DixonColes

    df = df.sort_values("date").copy()
    results = []

    train_start = df["date"].min()
    test_dates = pd.date_range(
        start=df["date"].min() + pd.DateOffset(years=train_years),
        end=df["date"].max() - pd.DateOffset(months=6),
        freq="6ME",
    )

    for cutoff in test_dates:
        train = df[df["date"] < cutoff]
        test = df[(df["date"] >= cutoff) & (df["date"] < cutoff + pd.DateOffset(months=6))]

        if len(train) < 500 or len(test) < 50:
            continue

        model = DixonColes()
        model.fit(train, verbose=False)

        log_losses = []
        for _, row in test.iterrows():
            try:
                probs = model.predict_score_probs(row["home_team"], row["away_team"])
                ll = log_loss_score(
                    (int(row["home_score"]), int(row["away_score"])), probs
                )
                log_losses.append(ll)
            except Exception:
                pass

        if log_losses:
            results.append({
                "cutoff": cutoff,
                "log_loss": np.mean(log_losses),
                "n_train": len(train),
                "n_test": len(test),
            })

    if verbose and results:
        avg_ll = np.mean([r["log_loss"] for r in results])
        print(f"Backtest Results:")
        print(f"  Time periods: {len(results)}")
        print(f"  Average Log-Loss: {avg_ll:.4f}")

    return results
