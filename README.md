# World Cup 2026 — Probabilistic Match Predictions

Predictive analytics platform for the FIFA World Cup 2026, forecasting all 104 tournament matches using the Dixon-Coles statistical model and Monte Carlo simulation.

## Methodology

The prediction engine combines two established approaches:

**Dixon-Coles Model (1997)** — A bivariate Poisson regression model that estimates attack and defense strength parameters for each national team. The model applies a low-score correction factor to improve accuracy for common football results (0-0, 1-0, 0-1, 1-1). Matches are time-weighted, giving more importance to recent results.

**Monte Carlo Simulation** — 10,000 complete tournament simulations are run, each simulating the full group stage, Round of 32, Round of 16, quarterfinals, semifinals, third-place match, and final. Knockout draws in regulation time are resolved via penalty shootouts (50/50 probability split).

## Data

- **Source:** [martj42/international_results](https://github.com/martj42/international_results) — approximately 50,000 international matches from 1872 to 2026
- **Tournament structure:** 48 teams, 12 groups of 4, top 2 plus 8 best third-placed teams advance to Round of 32
- **Groups:** Official FIFA draw

## Dashboard

The interactive dashboard provides:

- Group stage predictions with score probabilities for all 72 group matches
- Knockout bracket visualization with advancement probabilities by round
- Championship probability rankings for all 48 participating teams
- Downloadable CSV with complete match predictions

## Project Structure

```
worldcup-2026/
├── dashboard/app.py              # Streamlit dashboard
├── src/
│   ├── data/loader.py            # Data loading and preprocessing
│   ├── models/
│   │   ├── elo.py                # Elo rating system
│   │   ├── dixon_coles.py        # Dixon-Coles Poisson model
│   │   └── evaluate.py           # Backtesting metrics
│   └── simulation/
│       ├── tournament.py         # Tournament structure and group logic
│       └── monte_carlo.py        # Monte Carlo tournament simulator
├── scripts/
│   ├── download_data.py          # Dataset download script
│   └── train_model.py            # Full training pipeline
├── data/
│   ├── raw/                      # Raw match data (downloaded separately)
│   └── processed/                # Trained model and simulation results
└── pyproject.toml                # Dependencies (managed with uv)
```

## Quick Start

**Prerequisites:** Python 3.10+ and [uv](https://docs.astral.sh/uv/)

```bash
# Clone repository
git clone https://github.com/XwilberX/worldcup-2026.git
cd worldcup-2026

# Install dependencies
uv sync

# Download match data
uv run python scripts/download_data.py

# Train model and run simulation
uv run python scripts/train_model.py

# Launch dashboard
uv run streamlit run dashboard/app.py
```

## Top Predictions

Based on 10,000 Monte Carlo simulations (as of June 10, 2026):

| Rank | Team | Championship |
|------|------|-------------|
| 1 | Argentina | 21.4% |
| 2 | Brazil | 17.8% |
| 3 | Spain | 9.3% |
| 4 | Colombia | 8.9% |
| 5 | France | 6.3% |
| 6 | England | 4.5% |
| 7 | Uruguay | 4.4% |
| 8 | Portugal | 3.9% |
| 9 | Ecuador | 3.3% |
| 10 | Netherlands | 2.5% |

## Limitations

These predictions are probabilistic. The model does not account for player injuries, suspensions, managerial changes, or weather conditions. Historical performance does not guarantee future results. All predictions should be interpreted as statistical estimates, not certainties.
