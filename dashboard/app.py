"""Dashboard Mundial 2026 — FIFA Edition"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

BLUE = "#1a237e"
GOLD = "#b8942d"
WHITE = "#ffffff"
BG = "#f5f6fa"
CARD = "#ffffff"
TEXT = "#1a1a2e"
MUTED = "#5a6070"
BORDER = "#e2e5f0"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: {BG}; }}

    h1,h2,h3,h4,h5,h6 {{ color: {BLUE} !important; font-weight: 700; }}
    label {{ color: {TEXT} !important; font-weight: 600; }}
    .stCaption, small {{ color: {MUTED} !important; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; background: transparent; }}
    .stTabs [data-baseweb="tab"] {{
        background: {WHITE}; border-radius: 12px; color: {MUTED};
        font-weight: 600; padding: 12px 28px; border: 1px solid {BORDER};
    }}
    .stTabs [aria-selected="true"] {{
        background: {BLUE} !important; color: white !important; border-color: {BLUE} !important;
    }}

    .main-header {{ font-size: 2.8rem; font-weight: 800; color: {BLUE}; margin: 0; }}
    .main-header .gold {{ color: {GOLD}; }}
    .sub-header {{ color: {MUTED}; font-size: 1.05rem; margin-top: 0; }}

    .champion-card {{
        background: linear-gradient(145deg, {BLUE} 0%, #283593 100%);
        border: 3px solid {GOLD}; border-radius: 20px; padding: 24px; text-align: center;
    }}
    .champion-card, .champion-card * {{ color: {WHITE} !important; }}
    .champion-card .pct {{ font-size: 2.8rem; font-weight: 800; color: {GOLD} !important; }}

    .kpi-box {{
        background: {WHITE}; border-radius: 14px; padding: 16px; text-align: center;
        border: 1px solid {BORDER}; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    .kpi-value {{ font-size: 2rem; font-weight: 800; color: {BLUE}; }}
    .kpi-label {{ font-size: 0.75rem; color: {MUTED}; text-transform: uppercase; letter-spacing: 1px; }}

    .group-card {{
        background: {WHITE}; border: 2px solid {BORDER}; border-radius: 14px;
        padding: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }}
    .group-card.selected {{ border-color: {GOLD}; box-shadow: 0 0 20px rgba(184,148,45,0.12); }}
    .group-letter {{ font-size: 2rem; font-weight: 800; color: {GOLD}; }}

    .team-row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 7px 0; border-bottom: 1px solid {BORDER};
    }}
    .team-name {{ font-weight: 600; color: {TEXT}; font-size: 0.9rem; }}
    .team-odds {{ color: {GOLD}; font-size: 0.82rem; font-weight: 600; }}

    hr {{ border-color: {BORDER}; }}
    footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

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
    from src.data.loader import load_wc2026_schedule
    return load_wc2026_schedule(SCHEDULE_PATH)

def td(normalized: str) -> str:
    from src.data.loader import team_display_name
    return team_display_name(normalized)

def flag(team_normalized: str) -> str:
    return TEAM_FLAGS.get(team_normalized, "")

def build_match_preds(groups, model, schedule):
    preds = {}
    for _, m in schedule.iterrows():
        h, a = m["home_team"], m["away_team"]
        try:
            p = model.predict_match(h, a)
            preds[(h, a)] = p
        except Exception:
            preds[(h, a)] = None
    return preds

try:
    model = load_model()
    results = load_results()
    groups = load_groups()
    schedule = load_schedule()
    match_preds = build_match_preds(groups, model, schedule)
except FileNotFoundError:
    st.error("Modelo no entrenado. Ejecuta: `uv run python scripts/train_model.py`")
    st.stop()

# ============ HEADER ============
col_h, col_l = st.columns([4, 1])
with col_h:
    st.markdown(
        '<p class="main-header">⚽ <span class="gold">FIFA WORLD CUP</span> 2026</p>'
        '<p class="sub-header">Predicciones · 11 Jun – 19 Jul · Canadá 🇨🇦 México 🇲🇽 USA 🇺🇸</p>',
        unsafe_allow_html=True,
    )

top1 = results.iloc[0]
with col_l:
    st.markdown(f"""
    <div class="champion-card">
        <div style="font-size:2.5rem;">🏆</div>
        <div style="font-size:2rem;">{flag(top1['team'])}</div>
        <div style="font-size:1.2rem; font-weight:700;">{td(top1['team'])}</div>
        <div class="pct">{top1['champion']:.1%}</div>
        <div style="font-size:0.8rem; opacity:0.8;">Favorito al título</div>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for c, v, l in [(c1, "48", "Selecciones"), (c2, "12", "Grupos"), (c3, "104", "Partidos"), (c4, "16", "Sedes")]:
    with c:
        st.markdown(f'<div class="kpi-box"><div class="kpi-value">{v}</div><div class="kpi-label">{l}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============ TABS ============
tab1, tab2, tab3 = st.tabs(["🏟️ GRUPOS", "🏆 ELIMINATORIA", "📊 RANKING"])

# ======= TAB 1: GRUPOS =======
with tab1:
    group_keys = list(groups.keys())

    if "selected_group" not in st.session_state:
        st.session_state.selected_group = "A"

    cols = st.columns(6)
    for i, gk in enumerate(group_keys):
        ci = i % 6
        with cols[ci]:
            teams = groups[gk]
            cls = "group-card selected" if st.session_state.selected_group == gk else "group-card"
            html = f'<div class="{cls}" style="margin-bottom:10px;">'
            html += f'<div class="group-letter">Grupo {gk}</div>'
            for t in teams:
                row = results[results["team"] == t]
                pct = row.iloc[0]["champion"] if len(row) > 0 else 0
                html += f'<div class="team-row"><span class="team-name">{flag(t)} {td(t)}</span><span class="team-odds">{pct:.1%}</span></div>'
            html += '</div>'
            st.markdown(html, unsafe_allow_html=True)
            if st.button(f"Grupo {gk}", key=f"sel_{gk}", width="stretch"):
                st.session_state.selected_group = gk

    st.markdown("<br>", unsafe_allow_html=True)

    gk = st.session_state.selected_group
    teams = groups[gk]
    st.markdown(f"## Grupo {gk}")
    st.markdown(f'<div style="height:3px; width:50px; background:{GOLD}; border-radius:2px; margin-bottom:16px;"></div>', unsafe_allow_html=True)

    # Team cards
    gcols = st.columns(4)
    team_data = results[results["team"].isin(teams)].sort_values("champion", ascending=False)
    for i, (_, r) in enumerate(team_data.iterrows()):
        t = r["team"]
        with gcols[i]:
            border = GOLD if i == 0 else BORDER
            st.markdown(f"""
            <div style="background:{WHITE}; border-radius:12px; padding:18px; text-align:center; border:2px solid {border}; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size:2rem;">{flag(t)}</div>
                <div style="font-size:1rem; font-weight:700; color:{TEXT}; margin:6px 0;">{td(t)}</div>
                <div style="display:flex; justify-content:center; gap:14px; font-size:0.82rem;">
                    <span style="color:{GOLD}; font-weight:600;">🏆 {r['champion']:.1%}</span>
                    <span style="color:{MUTED};">⬆ {r['round_of_32']:.0%}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### Partidos")

    for h, a in combinations(teams, 2):
        p = match_preds.get((h, a))
        if not p:
            continue
        hw, d, aw = p["prob_home_win"], p["prob_draw"], p["prob_away_win"]
        score = p["most_likely_score"]

        bh, bd, ba = int(hw * 200), int(d * 200), int(aw * 200)
        ch = "#2e7d32" if hw >= 0.5 else ("#e65100" if hw >= 0.35 else "#c62828")
        cd = "#f9a825"
        ca = "#2e7d32" if aw >= 0.5 else ("#e65100" if aw >= 0.35 else "#c62828")

        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; background:{WHITE}; border:1px solid {BORDER}; border-radius:10px; padding:12px 18px; margin-bottom:6px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
            <div style="flex:1; text-align:right;">
                <span style="color:{TEXT}; font-weight:600;">{flag(h)} {td(h)}</span>
            </div>
            <div style="min-width:40px; text-align:center;">
                <span style="color:{GOLD}; font-weight:700; font-size:1.1rem;">{score}</span>
            </div>
            <div style="flex:1;">
                <span style="color:{TEXT}; font-weight:600;">{flag(a)} {td(a)}</span>
            </div>
            <div style="width:200px; display:flex; gap:2px; height:18px; border-radius:5px; overflow:hidden;">
                <div style="width:{bh}px; background:{ch};"></div>
                <div style="width:{bd}px; background:{cd};"></div>
                <div style="width:{ba}px; background:{ca};"></div>
            </div>
            <div style="min-width:110px; display:flex; gap:10px; font-size:0.78rem; font-weight:600;">
                <span style="color:{ch};">{hw:.0%}</span>
                <span style="color:{cd};">{d:.0%}</span>
                <span style="color:{ca};">{aw:.0%}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # All groups chart
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
                marker_color=GOLD if champ > 0.1 else "#3f51b5",
                hoverinfo="text",
            ))
    fig.update_layout(
        barmode="stack", height=500,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        xaxis=dict(title="% Clasifica", tickformat=".0%", gridcolor=BORDER),
        yaxis=dict(title="", gridcolor=BORDER),
        showlegend=False, bargap=0.01,
    )
    st.plotly_chart(fig, width="stretch")
    st.caption("Barra = % de avanzar a Octavos · Color oro = alta probabilidad de campeón")

# ======= TAB 2: ELIMINATORIA =======
with tab2:
    st.markdown("## Camino a la Final")

    rounds = [
        ("Dieciseisavos (32 equipos)", "round_of_32", "🎫"),
        ("Octavos (16)", "round_of_16", "🏟️"),
        ("Cuartos (8)", "quarterfinalist", "🔥"),
        ("Semifinales (4)", "semifinalist", "⭐"),
        ("Final (2)", "runner_up", "🥈"),
        ("Campeón", "champion", "🏆"),
    ]

    for rname, col_key, icon in rounds:
        top_n = {"round_of_32": 32, "round_of_16": 16, "quarterfinalist": 8,
                 "semifinalist": 4, "runner_up": 2, "champion": 1}[col_key]
        top_teams = results.sort_values(col_key, ascending=False).head(top_n)

        st.markdown(f"### {icon} {rname}")
        grid_cols = st.columns(min(top_n, 8) if top_n <= 16 else 8)
        for i, (_, r) in enumerate(top_teams.iterrows()):
            ci = i % 8
            with grid_cols[ci]:
                t = r["team"]
                pct = r[col_key]
                bw = int(pct * 100)
                st.markdown(f"""
                <div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:8px; padding:8px; text-align:center; margin-bottom:6px;">
                    <div style="font-size:1.2rem;">{flag(t)}</div>
                    <div style="color:{TEXT}; font-weight:600; font-size:0.8rem;">{td(t)}</div>
                    <div style="margin-top:3px; height:3px; background:{BORDER}; border-radius:1px;">
                        <div style="height:3px; width:{bw}%; background:{GOLD}; border-radius:1px;"></div>
                    </div>
                    <div style="color:{GOLD}; font-weight:700; font-size:0.8rem; margin-top:3px;">{pct:.1%}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Top 8 — Probabilidad de Avance")

    top8 = results.head(8)
    fig = go.Figure()
    for _, row in top8.iterrows():
        fig.add_trace(go.Scatter(
            x=["Dieciseisavos", "Octavos", "Cuartos", "Semifinal", "Final", "Campeón"],
            y=[row["round_of_32"], row["round_of_16"], row["quarterfinalist"],
               row["semifinalist"], row["runner_up"] + row["champion"], row["champion"]],
            mode="lines+markers",
            name=f"{flag(row['team'])} {td(row['team'])}",
            line=dict(width=3), marker=dict(size=8),
        ))
    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        yaxis=dict(tickformat=".0%", gridcolor=BORDER, title="Probabilidad"),
        xaxis=dict(gridcolor=BORDER),
        hovermode="x unified",
    )
    st.plotly_chart(fig, width="stretch")

# ======= TAB 3: RANKING =======
with tab3:
    st.markdown("## Probabilidad de Campeón")
    st.markdown(f'<div style="height:3px; width:50px; background:{GOLD}; border-radius:2px; margin-bottom:20px;"></div>', unsafe_allow_html=True)

    top_n = st.slider("Mostrar", 5, 48, 20, key="rank_topn")
    top = results.head(top_n).copy()

    color_list = [GOLD, "#cca844", "#bfa050", "#b09860", "#a09070"] + ["#5a6070"] * (top_n - 5)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=[f"{flag(r['team'])} {td(r['team'])}" for _, r in top.iterrows()][::-1],
        x=[r["champion"] * 100 for _, r in top.iterrows()][::-1],
        orientation="h",
        marker_color=color_list[::-1],
        text=[f"{r['champion']:.1%}" for _, r in top.iterrows()][::-1],
        textposition="outside",
        textfont=dict(color=TEXT, size=13),
        hovertemplate="%{y}<br>Campeón: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        height=max(380, top_n * 28 + 100),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
        xaxis=dict(title="% Campeón", ticksuffix="%", gridcolor=BORDER),
        yaxis=dict(title="", tickfont=dict(size=13)),
        margin=dict(l=20, r=80, t=20, b=20),
        bargap=0.25,
    )
    st.plotly_chart(fig, width="stretch")

    with st.expander("Ver tabla completa"):
        full = results.copy()
        full["display"] = full["team"].apply(lambda x: f"{flag(x)} {td(x)}")
        dc = ["display", "champion", "runner_up", "third", "semifinalist",
              "quarterfinalist", "round_of_16", "round_of_32"]
        df_tab = full[dc].copy()
        for c in dc[1:]:
            df_tab[c] = df_tab[c].apply(lambda x: f"{x:.1%}")
        st.dataframe(
            df_tab.rename(columns={
                "display": "Selección", "champion": "🏆 Campeón", "runner_up": "🥈 Subcampeón",
                "third": "🥉 3er Lugar", "semifinalist": "Semis", "quarterfinalist": "Cuartos",
                "round_of_16": "Octavos", "round_of_32": "Clasifica",
            }),
            width="stretch", hide_index=True, height=800,
        )

# ============ FOOTER ============
st.markdown("---")
fc1, fc2, fc3 = st.columns(3)
with fc1:
    st.caption("**Modelo Dixon-Coles (1997)** · Regresión Poisson · 10K simulaciones Monte Carlo")
with fc2:
    st.caption("**~50,000 partidos** · 1872–2026 · martj42/international_results")
with fc3:
    st.caption("Predicciones probabilísticas. Las sorpresas son parte del fútbol.")
