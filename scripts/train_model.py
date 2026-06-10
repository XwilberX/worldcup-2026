"""Train the Dixon-Coles model and save predictions."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pickle
from src.data.loader import load_results, load_wc2026_schedule, WC2026_GROUPS
from src.models.elo import compute_elo_history, get_elo_ratings
from src.models.dixon_coles import DixonColes
from src.models.evaluate import backtest_temporal
from src.simulation.monte_carlo import monte_carlo_simulation


def main():
    print("=" * 60)
    print("World Cup 2026 Prediction Pipeline")
    print("=" * 60)

    # 1. Load data
    print("\n[1/6] Loading historical match data...")
    df = load_results(start_date="2010-01-01")
    print(f"  Loaded {len(df):,} matches from {df['date'].min().date()} to {df['date'].max().date()}")

    # 2. Compute Elo ratings
    print("\n[2/6] Computing Elo ratings...")
    elo = compute_elo_history(df)
    print(f"  Computed Elo for {len(elo)} teams")
    top_elo = sorted(elo.items(), key=lambda x: x[1], reverse=True)[:10]
    for team, rating in top_elo:
        print(f"    {team}: {rating:.0f}")

    # 3. Train Dixon-Coles model
    print("\n[3/6] Training Dixon-Coles model...")
    df_recent = load_results(start_date="2014-01-01")
    model = DixonColes()
    model.fit(df_recent, decay_half_life_days=365 * 3, min_matches=20, verbose=True)

    # 4. Backtest
    print("\n[4/6] Running backtests...")
    _ = backtest_temporal(df_recent, DixonColes, train_years=4)

    # 5. Load 2026 tournament structure
    print("\n[5/6] Loading 2026 World Cup groups...")
    groups = WC2026_GROUPS
    print(f"  Loaded {len(groups)} official FIFA groups:")
    for gname, teams in sorted(groups.items()):
        print(f"    Group {gname}: {', '.join(teams)}")

    # 6. Run Monte Carlo simulation
    print("\n[6/6] Running Monte Carlo simulation (10,000 iterations)...")
    results = monte_carlo_simulation(groups, model, n_simulations=10000, show_progress=True)

    print("\n" + "=" * 60)
    print("TOP 20 CHAMPIONSHIP PROBABILITIES")
    print("=" * 60)
    top20 = results.head(20)
    for _, row in top20.iterrows():
        bar = "█" * int(row["champion"] * 200)
        print(f"  {row['team']:<25} {row['champion']:.1%}  {bar}")

    # Save results
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    results.to_csv(os.path.join(output_dir, "simulation_results.csv"), index=False)

    with open(os.path.join(output_dir, "model.pkl"), "wb") as f:
        pickle.dump(model, f)

    with open(os.path.join(output_dir, "groups.pkl"), "wb") as f:
        pickle.dump(groups, f)

    print(f"\nResults saved to {output_dir}/")
    print("Done!")


if __name__ == "__main__":
    main()
