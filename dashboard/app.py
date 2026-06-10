"""Dashboard Mundial 2026 — FIFA Edition"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pickle
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="Mundial 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "model.pkl")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "simulation_results.csv")
SCHEDULE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "results.csv")

FIFA_BLUE = "#0a0e27"
FIFA_GOLD = "#c8a951"
FIFA_WHITE = "#f5f5f7"
FIFA_DARK = "#131738"
FIFA_ACCENT = "#2d5eb7"
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    * {{ font-family: 'Inter', sans-serif; }}

    .stApp {{
        background: linear-gradient(180deg, {FIFA_DARK} 0%, {FIFA_BLUE} 100%);
    }}

    /* Global text overrides for dark theme */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
    .stText, div[data-testid="stText"], .st-bd, .st-bv, .st-bw {{
        color: {FIFA_WHITE} !important;
    }}

    .stCaption, .stCaption p, small, .small-text {{
        color: #8899bb !important;
    }}

    h1, h2, h3, h4, h5, h6, .st-emotion-cache h1, .st-emotion-cache h2, .st-emotion-cache h3 {{
        color: {FIFA_WHITE} !important;
    }}

    label, .st-emotion-cache label, .st-cg {{ color: {FIFA_WHITE} !important; }}

    /* Streamlit widgets in dark */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input,
    .stSlider div {{
        background: rgba(255,255,255,0.08) !important;
        color: {FIFA_WHITE} !important;
        border-color: #2a3050 !important;
    }}

    .stDataFrame, .stTable, .stTable td, .stTable th {{
        color: {FIFA_WHITE} !important;
        background: transparent !important;
    }}

    /* Expander text */
    .streamlit-expanderContent p, .st-emotion-cache p {{
        color: {FIFA_WHITE};
    }}

    /* Custom elements */
    .main-header {{
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: {FIFA_WHITE};
        margin: 0;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .main-header .gold {{ color: {FIFA_GOLD}; }}

    .sub-header {{
        color: #8899bb;
        font-size: 1.1rem;
        margin-top: 0;
    }}

    .group-card {{
        background: linear-gradient(145deg, #1a1f3a 0%, #161b33 100%);
        border: 1px solid #2a3050;
        border-radius: 16px;
        padding: 20px;
        transition: all 0.2s;
        cursor: pointer;
        color: {FIFA_WHITE};
    }}
    .group-card:hover {{
        border-color: {FIFA_GOLD};
        transform: translateY(-2px);
    }}
    .group-card.selected {{
        border-color: {FIFA_GOLD};
        box-shadow: 0 0 30px rgba(200, 169, 81, 0.15);
    }}

    .group-letter {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {FIFA_GOLD};
    }}

    .team-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #2a3050;
    }}
    .team-name {{
        font-weight: 600;
        color: {FIFA_WHITE};
        font-size: 0.95rem;
    }}
    .team-odds {{
        color: {FIFA_GOLD};
        font-size: 0.85rem;
        font-weight: 600;
    }}

    .match-row {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 16px;
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        margin: 4px 0;
    }}
    .match-team {{
        color: {FIFA_WHITE};
        font-weight: 600;
        flex: 1;
    }}
    .match-score {{
        color: {FIFA_GOLD};
        font-weight: 700;
        font-size: 1.1rem;
        min-width: 30px;
        text-align: center;
    }}
    .match-pct {{
        color: #8899bb;
        font-size: 0.8rem;
        min-width: 40px;
        text-align: center;
    }}

    .champion-card {{
        background: linear-gradient(145deg, #1a1f3a 0%, #0f1330 100%);
        border: 2px solid {FIFA_GOLD};
        border-radius: 20px;
        padding: 24px;
        text-align: center;
    }}
    .champion-card .crown {{ font-size: 3rem; }}
    .champion-card .team {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {FIFA_WHITE};
    }}
    .champion-card .pct {{
        font-size: 3.5rem;
        font-weight: 800;
        color: {FIFA_GOLD};
    }}

    .kpi-box {{
        background: rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 16px;
        text-align: center;
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {FIFA_WHITE};
    }}
    .kpi-label {{
        font-size: 0.8rem;
        color: #8899bb;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        color: #8899bb;
        font-weight: 600;
        padding: 12px 28px;
        border: 1px solid #2a3050;
    }}
    .stTabs [aria-selected="true"] {{
        background: {FIFA_GOLD} !important;
        color: {FIFA_DARK} !important;
        border-color: {FIFA_GOLD} !important;
    }}

    .flag {{ font-size: 1.2rem; }}

    hr {{ border-color: #2a3050; }}

    div[data-testid="stSidebar"] {{
        background: {FIFA_DARK};
        color: {FIFA_WHITE};
    }}

    /* Footer */
    footer {{ visibility: hidden; }}

    /* Fix plotly tooltip */
    .js-plotly-plot .plotly .hoverlayer .hovertext path,
    .js-plotly-plot .plotly .hoverlayer .hovertext text {{
        fill: {FIFA_WHITE} !important;
    }}
</style>
""", unsafe_allow_html=True)

CONFED_FLAGS = {
    "CONMEBOL": "🇧🇷🇦🇷", "UEFA": "🇪🇺", "CONCACAF": "🇲🇽🇺🇸",
    "CAF": "🇸🇳🇲🇦", "AFC": "🇯🇵🇰🇷", "OFC": "🇳🇿",
}

TEAM_FLAGS = {
    "Mexico": "🇲🇽", "SouthAfrica": "🇿🇦", "KoreaRepublic": "🇰🇷", "CzechRepublic": "🇨🇿",
    "Canada": "🇨🇦", "BosniaHerzegovina": "🇧🇦", "Qatar": "🇶🇦", "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "UnitedStates": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turkey": "🇹🇷",
    "Germany": "🇩🇪", "Curacao": "🇨🇼", "IvoryCoast": "🇨🇮", "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Iran": "🇮🇷", "NewZealand": "🇳🇿",
    "Spain": "🇪🇸", "CapeVerde": "🇨🇻", "SaudiArabia": "🇸🇦", "Uruguay": "🇺🇾",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Iraq": "🇮🇶", "Norway": "🇳🇴",
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Austria": "🇦🇹", "Jordan": "🇯🇴",
    "Portugal": "🇵🇹", "DRCongo": "🇨🇩", "Uzbekistan": "🇺🇿", "Colombia": "🇨🇴",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croatia": "🇭🇷", "Ghana": "🇬🇭", "Panama": "🇵🇦",
}

@st.cache_resource
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

@st.cache_data
def load_results():
    return pd.read_csv(RESULTS_PATH)

@st.cache_data
def load_groups():
    from src.data.loader import WC2026_GROUPS
    return WC2026_GROUPS

@st.cache_data
def load_schedule():
    from src.data.loader import load_wc2026_schedule, normalize_team
    return load_wc2026_schedule(SCHEDULE_PATH)

def td(normalized: str) -> str:
    from src.data.loader import team_display_name
    return team_display_name(normalized)

def flag(team_normalized: str) -> str:
    return TEAM_FLAGS.get(team_normalized, "")

def build_match_predictions(groups, model, schedule):
    """Build all 72 group match predictions indexed by (home, away)."""
    preds = {}
    for _, match in schedule.iterrows():
        h, a = match["home_team"], match["away_team"]
        try:
            p = model.predict_match(h, a)
            preds[(h, a)] = p
        except Exception:
            preds[(h, a)] = None
    return preds

# --- Load data ---
try:
    model = load_model()
    results = load_results()
    groups = load_groups()
    schedule = load_schedule()
    match_preds = build_match_predictions(groups, model, schedule)
except FileNotFoundError:
    st.error("Modelo no entrenado. Ejecuta: `uv run python scripts/train_model.py`")
    st.stop()

# ============================================================
# HEADER
# ============================================================
col_h, col_l = st.columns([4, 1])
with col_h:
    st.markdown(
        '<p class="main-header">⚽ <span class="gold">FIFA WORLD CUP</span> 2026</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sub-header">Predicciones · Canadá 🇨🇦 &nbsp; México 🇲🇽 &nbsp; USA 🇺🇸 &nbsp;· 11 Jun – 19 Jul</p>',
        unsafe_allow_html=True,
    )

# Champion card
top1 = results.iloc[0]
with col_l:
    st.markdown(f"""
    <div class="champion-card">
        <div class="crown">🏆</div>
        <div style="font-size: 2.5rem;">{flag(top1['team'])}</div>
        <div class="team">{td(top1['team'])}</div>
        <div class="pct">{top1['champion']:.1%}</div>
        <div style="color: #8899bb; font-size: 0.85rem;">Favorito al título</div>
    </div>
    """, unsafe_allow_html=True)

# KPI row
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-value">48</div><div class="kpi-label">Selecciones</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-value">12</div><div class="kpi-label">Grupos</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-value">104</div><div class="kpi-label">Partidos</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-box"><div class="kpi-value">16</div><div class="kpi-label">Sedes</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs(["🏟️ GRUPOS", "🏆 ELIMINATORIA", "📊 RANKING"])

# ==================== TAB 1: GRUPOS ====================
with tab1:
    # Group cards grid
    group_keys = list(groups.keys())

    # Selected group from session state
    if "selected_group" not in st.session_state:
        st.session_state.selected_group = "A"

    # Grid of 12 groups
    cols = st.columns(6)
    for i, gk in enumerate(group_keys):
        ci = i % 6
        with cols[ci]:
            teams = groups[gk]
            top_team = results[results["team"].isin(teams)].sort_values("champion", ascending=False)
            best = top_team.iloc[0] if len(top_team) > 0 else None

            card_class = "group-card selected" if st.session_state.selected_group == gk else "group-card"
            card_html = f'<div class="{card_class}" style="margin-bottom:12px;">'
            card_html += f'<div class="group-letter">GRUPO {gk}</div>'
            for t in teams:
                row = results[results["team"] == t]
                pct = row.iloc[0]["champion"] if len(row) > 0 else 0
                card_html += f'<div class="team-row"><span class="team-name">{flag(t)} {td(t)}</span><span class="team-odds">{pct:.1%}</span></div>'
            card_html += '</div>'

            if st.markdown(card_html, unsafe_allow_html=True):
                pass
            if st.button(f"Ver Grupo {gk}", key=f"sel_{gk}", width="stretch"):
                st.session_state.selected_group = gk

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Selected Group Detail ---
    gk = st.session_state.selected_group
    teams = groups[gk]

    st.markdown(f"## Grupo {gk}")
    st.markdown(f'<div style="height:2px; width:60px; background:{FIFA_GOLD}; border-radius:2px; margin-bottom:20px;"></div>', unsafe_allow_html=True)

    # Team power cards
    gcols = st.columns(4)
    team_data = results[results["team"].isin(teams)].sort_values("champion", ascending=False)
    for i, (_, r) in enumerate(team_data.iterrows()):
        t = r["team"]
        with gcols[i]:
            pos = ["🥇","🥈","🥉","4️⃣"][i]
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); border-radius: 14px; padding: 20px; text-align: center; border: 1px solid {'#c8a951' if i == 0 else '#2a3050'};">
                <div style="font-size: 2rem;">{flag(t)}</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #f5f5f7; margin: 8px 0;">{td(t)}</div>
                <div style="display: flex; justify-content: center; gap: 16px; font-size: 0.85rem;">
                    <span style="color: #c8a951;">🏆 {r['champion']:.1%}</span>
                    <span style="color: #8899bb;">⬆ {r['round_of_32']:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Matches
    st.markdown(f"### Partidos del Grupo {gk}")
    match_list = []
    for h, a in combinations(teams, 2):
        p = match_preds.get((h, a))
        if p:
            match_list.append((h, a, p))

    for h, a, p in match_list:
        hw, d, aw = p["prob_home_win"], p["prob_draw"], p["prob_away_win"]
        score = p["most_likely_score"]

        # Color bar
        bar_hw = int(hw * 200)
        bar_d = int(d * 200)
        bar_aw = int(aw * 200)

        color_h = "#4caf50" if hw >= 0.5 else ("#ff9800" if hw >= 0.35 else "#f44336")
        color_d = "#ffc107"
        color_a = "#4caf50" if aw >= 0.5 else ("#ff9800" if aw >= 0.35 else "#f44336")

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:16px; background:rgba(255,255,255,0.02); border-radius:12px; padding:14px 20px; margin-bottom:8px;">
            <div style="flex:1; text-align:right;">
                <span style="color:#f5f5f7; font-weight:600; font-size:1rem;">{flag(h)} {td(h)}</span>
            </div>
            <div style="min-width:90px; text-align:center;">
                <span style="color:#c8a951; font-weight:700; font-size:1.2rem;">{score}</span>
            </div>
            <div style="flex:1;">
                <span style="color:#f5f5f7; font-weight:600; font-size:1rem;">{flag(a)} {td(a)}</span>
            </div>
            <div style="width:200px; display:flex; gap:2px; height:20px; border-radius:6px; overflow:hidden;">
                <div style="width:{bar_hw}px; background:{color_h};"></div>
                <div style="width:{bar_d}px; background:{color_d};"></div>
                <div style="width:{bar_aw}px; background:{color_a};"></div>
            </div>
            <div style="min-width:120px; display:flex; gap:12px; font-size:0.8rem;">
                <span style="color:{color_h};">{hw:.0%}</span>
                <span style="color:{color_d};">{d:.0%}</span>
                <span style="color:{color_a};">{aw:.0%}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # All groups overview
    st.markdown("---")
    st.markdown("### Todos los Grupos")

    fig = go.Figure()
    for gk in group_keys:
        for t in groups[gk]:
            row = results[results["team"] == t]
            champ = row.iloc[0]["champion"] if len(row) > 0 else 0
            adv = row.iloc[0]["round_of_32"] if len(row) > 0 else 0
            fig.add_trace(go.Bar(
                name=f"{gk}: {td(t)}",
                y=[f"Grupo {gk}"],
                x=[adv],
                orientation="h",
                text=f"{flag(t)} {td(t)} {champ:.1%}",
                textposition="inside",
                marker=dict(
                    color=champ,
                    colorscale=[[0, "#1a237e"], [0.5, "#3f51b5"], [1, "#ffd700"]],
                    showscale=True,
                    colorbar=dict(title="🏆", tickformat=".0%"),
                ),
                hoverinfo="text",
            ))

    fig.update_layout(
        barmode="stack",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899bb"),
        xaxis=dict(title="% Clasifica", tickformat=".0%", gridcolor="#2a3050"),
        yaxis=dict(title="", gridcolor="#2a3050"),
        showlegend=False,
        bargap=0.01,
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Barra = % de avanzar a Octavos · Color = % de ser campeón · Texto = probabilidad de título")

# ==================== TAB 2: ELIMINATORIA ====================
with tab2:
    st.markdown("## Camino a la Final")

    # Show KO stage predictions per round
    rounds = [
        ("Dieciseisavos (32)", "round_of_32", "🎫"),
        ("Octavos (16)", "round_of_16", "🏟️"),
        ("Cuartos (8)", "quarterfinalist", "🔥"),
        ("Semis (4)", "semifinalist", "⭐"),
        ("Final (2)", "runner_up", "🥈"),
        ("Campeón (1)", "champion", "🏆"),
    ]

    for round_name, col_key, icon in rounds:
        top_n = 32 if "32" in round_name else (16 if "16" in round_name else (8 if "8" in round_name else (4 if "4" in round_name else (2 if "2" in round_name else 1))))
        top_teams = results.sort_values(col_key, ascending=False).head(top_n)

        st.markdown(f"### {icon} {round_name}")

        cols = st.columns(min(top_n, 8) if top_n <= 16 else 8)
        for i, (_, r) in enumerate(top_teams.iterrows()):
            ci = i % 8
            with cols[ci]:
                t = r["team"]
                pct = r[col_key]
                bar_w = int(pct * 100)
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03); border-radius:10px; padding:10px; text-align:center; margin-bottom:8px;">
                    <div style="font-size:1.3rem;">{flag(t)}</div>
                    <div style="color:#f5f5f7; font-weight:600; font-size:0.85rem;">{td(t)}</div>
                    <div style="margin-top:4px; height:4px; background:#2a3050; border-radius:2px;">
                        <div style="height:4px; width:{bar_w}%; background:{FIFA_GOLD}; border-radius:2px;"></div>
                    </div>
                    <div style="color:#c8a951; font-weight:700; font-size:0.85rem; margin-top:4px;">{pct:.1%}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Bracket chart
    st.markdown("---")
    st.markdown("### Probabilidad de Avanzar — Top 8")

    top8 = results.head(8)
    fig = go.Figure()
    for _, row in top8.iterrows():
        fig.add_trace(go.Scatter(
            x=["Dieciseisavos", "Octavos", "Cuartos", "Semis", "Final", "Campeón"],
            y=[
                row["round_of_32"],
                row["round_of_16"],
                row["quarterfinalist"],
                row["semifinalist"],
                row["runner_up"] + row["champion"],
                row["champion"],
            ],
            mode="lines+markers",
            name=f"{flag(row['team'])} {td(row['team'])}",
            line=dict(width=3),
            marker=dict(size=10),
        ))

    fig.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899bb"),
        yaxis=dict(tickformat=".0%", gridcolor="#2a3050", title="Probabilidad"),
        xaxis=dict(gridcolor="#2a3050"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")

# ==================== TAB 3: RANKING ====================
with tab3:
    st.markdown("## Ranking de Campeón")
    st.markdown('<div style="height:2px; width:60px; background:#c8a951; border-radius:2px; margin-bottom:20px;"></div>', unsafe_allow_html=True)

    top_n = st.slider("Mostrar", 5, 48, 20, key="rank_topn")

    top = results.head(top_n).copy()

    fig = go.Figure()
    colors = [FIFA_GOLD, "#e6c460", "#d4b860", "#c0a860", "#aa9850"] + ["#8899bb"] * (top_n - 5)

    fig.add_trace(go.Bar(
        y=[f"{flag(r['team'])} {td(r['team'])}" for _, r in top.iterrows()][::-1],
        x=[r["champion"] * 100 for _, r in top.iterrows()][::-1],
        orientation="h",
        marker_color=colors[::-1],
        text=[f"{r['champion']:.1%}" for _, r in top.iterrows()][::-1],
        textposition="outside",
        textfont=dict(color="#f5f5f7", size=14),
        hovertemplate="%{y}<br>Campeón: %{x:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        height=max(400, top_n * 30 + 100),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8899bb"),
        xaxis=dict(title="% Campeón", ticksuffix="%", gridcolor="#2a3050"),
        yaxis=dict(title="", tickfont=dict(size=14)),
        margin=dict(l=20, r=80, t=20, b=20),
        bargap=0.25,
    )
    st.plotly_chart(fig, width="stretch")

    # Full table (collapsible)
    with st.expander("Ver tabla completa de probabilidades"):
        full = results.copy()
        full["display"] = full["team"].apply(lambda x: f"{flag(x)} {td(x)}")
        disp_cols = ["display", "champion", "runner_up", "third", "semifinalist",
                      "quarterfinalist", "round_of_16", "round_of_32"]
        df_tab = full[disp_cols].copy()
        for c in disp_cols[1:]:
            df_tab[c] = df_tab[c].apply(lambda x: f"{x:.1%}")

        st.dataframe(
            df_tab.rename(columns={
                "display": "Selección", "champion": "🏆 Campeón", "runner_up": "🥈 Subcampeón",
                "third": "🥉 3er Lugar", "semifinalist": "Semis", "quarterfinalist": "Cuartos",
                "round_of_16": "Octavos", "round_of_32": "Clasifica",
            }),
            width="stretch", hide_index=True, height=800,
        )

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Metodología**")
    st.caption("Modelo Dixon-Coles (1997) · Regresión Poisson · Corrección de bajos marcadores · 10,000 simulaciones Monte Carlo")
with c2:
    st.markdown("**Datos**")
    st.caption("~50,000 partidos internacionales (1872–2026) · martj42/international_results")
with c3:
    st.markdown("**Sobre esto**")
    st.caption("Las predicciones son probabilísticas. Las sorpresas son parte del fútbol. Los resultados reales pueden variar.")
