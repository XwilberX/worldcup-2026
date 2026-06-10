"""Load and preprocess international football results."""

import pandas as pd
from pathlib import Path
import re

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
RESULTS_PATH = RAW_DIR / "results.csv"

TEAM_NAME_MAP = {
    "Curaçao": "Curacao",
    "Czech Republic": "CzechRepublic",
    "South Korea": "KoreaRepublic",
    "North Korea": "KoreaDPR",
    "United States": "UnitedStates",
    "Saudi Arabia": "SaudiArabia",
    "Costa Rica": "CostaRica",
    "South Africa": "SouthAfrica",
    "New Zealand": "NewZealand",
    "El Salvador": "ElSalvador",
    "Ivory Coast": "IvoryCoast",
    "DR Congo": "DRCongo",
    "Cape Verde": "CapeVerde",
    "Bosnia and Herzegovina": "BosniaHerzegovina",
    "Northern Ireland": "NorthernIreland",
    "Trinidad and Tobago": "TrinidadTobago",
    "United Arab Emirates": "UAE",
    "Papua New Guinea": "PapuaNewGuinea",
    "Sierra Leone": "SierraLeone",
    "Burkina Faso": "BurkinaFaso",
    "Equatorial Guinea": "EquatorialGuinea",
    "Guinea-Bissau": "GuineaBissau",
    "East Germany": "Germany",
    "West Germany": "Germany",
    "Soviet Union": "Russia",
    "Czechoslovakia": "CzechRepublic",
    "Yugoslavia": "Serbia",
}

TEAM_DISPLAY_NAMES = {v: k for k, v in TEAM_NAME_MAP.items() if k not in (
    "East Germany", "West Germany", "Soviet Union", "Czechoslovakia", "Yugoslavia"
)}

def team_display_name(normalized: str) -> str:
    return TEAM_DISPLAY_NAMES.get(normalized, normalized)


def normalize_team(name: str) -> str:
    name = str(name).strip()
    return TEAM_NAME_MAP.get(name, name.replace(" ", ""))


def load_results(path: str = None, start_date: str = "2016-01-01") -> pd.DataFrame:
    """
    Load and preprocess the international results dataset.
    - Filters from start_date onwards
    - Normalizes team names
    - Removes rows with missing scores (future matches)
    - Converts dates
    """
    path = path or str(RESULTS_PATH)
    df = pd.read_csv(path)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)

    df = df[(df["date"] >= start_date) & (df["date"] < "2026-06-01")]

    df["home_team"] = df["home_team"].apply(normalize_team)
    df["away_team"] = df["away_team"].apply(normalize_team)

    # Remove rows where home_score and away_score are strings like 'NA'
    df = df.sort_values("date").reset_index(drop=True)

    return df


def load_wc2026_schedule(path: str = None) -> pd.DataFrame:
    """
    Load the 2026 World Cup group stage schedule from the dataset.
    Returns a DataFrame with the group stage matchups.
    """
    path = path or str(RESULTS_PATH)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    wc26 = df[(df["date"] >= "2026-06-11") & (df["date"] <= "2026-07-19")].copy()
    wc26["home_team"] = wc26["home_team"].apply(normalize_team)
    wc26["away_team"] = wc26["away_team"].apply(normalize_team)

    return wc26


# Official FIFA World Cup 2026 groups (from draw)
# Normalized team names matching the dataset
WC2026_GROUPS = {
    "A": ["Mexico", "SouthAfrica", "KoreaRepublic", "CzechRepublic"],
    "B": ["Canada", "BosniaHerzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["UnitedStates", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "IvoryCoast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "NewZealand"],
    "H": ["Spain", "CapeVerde", "SaudiArabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DRCongo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}
