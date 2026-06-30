import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIDM Resident Portal",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {background:#1e2130;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1rem;}
  .flag-red    {color:#ff4b4b;font-weight:700;}
  .flag-amber  {color:#ffa500;font-weight:700;}
  .flag-green  {color:#21c354;font-weight:700;}
  .leaderboard-rank {font-size:1.4rem;font-weight:800;}
</style>
""", unsafe_allow_html=True)

# ── Google Sheets connection ──────────────────────────────────────────────────
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

@st.cache_resource(show_spinner=False)
def get_worksheet():
    if "gcp_service_account" not in st.secrets or "sheet" not in st.secrets:
        return None
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(st.secrets["sheet"]["sheet_id"])
    return sh.sheet1

def get_mock_data():
    data = [
        {"Resident Name": "Alice Smith", "Total Score": 85, "Flag Status": "GREEN", "Timestamp": "2023-10-01 10:00:00", "Module 1": 80, "Module 2": 90, "Module 3": 85},
        {"Resident Name": "Bob Jones", "Total Score": 45, "Flag Status": "RED", "Timestamp": "2023-10-01 10:05:00", "Module 1": 40, "Module 2": 50, "Module 3": 45},
        {"Resident Name": "Charlie Brown", "Total Score": 65, "Flag Status": "AMBER", "Timestamp": "2023-10-01 10:10:00", "Module 1": 60, "Module 2": 70, "Module 3": 65},
        {"Resident Name": "David Wilson", "Total Score": 92, "Flag Status": "GREEN", "Timestamp": "2023-10-01 10:15:00", "Module 1": 95, "Module 2": 89, "Module 3": 92},
        {"Resident Name": "Eve Adams", "Total Score": 58, "Flag Status": "AMBER", "Timestamp": "2023-10-01 10:20:00", "Module 1": 55, "Module 2": 60, "Module 3": 59},
    ]
    return pd.DataFrame(data)

@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    if os.environ.get("MOCK_MODE") == "true" or "gcp_service_account" not in st.secrets:
        return get_mock_data()

    ws = get_worksheet()
    if ws is None:
        return get_mock_data()

    records = ws.get_all_records()
    df = pd.DataFrame(records)
    return df

def main():
    # ── Sidebar ───────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/tooth.png", width=60)
        st.title("AIDM Portal")
        st.caption("Resident Performance Dashboard")
        st.divider()
        page = st.radio(
            "Navigate",
            ["🏠 Overview", "📊 Leaderboard", "🎯 My Profile", "🚩 Flagged Residents"],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    # ── Load data ─────────────────────────────────────────────────────────────────
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        st.stop()

    if df.empty:
        st.warning("No data found in the sheet yet.")
        st.stop()

    # Normalise column names
    df.columns = [c.strip() for c in df.columns]

    # Expected columns (adjust to match your sheet headers exactly)
    RESIDENT_COL  = "Resident Name"
    SCORE_COL     = "Total Score"
    FLAG_COL      = "Flag Status"
    DATE_COL      = "Timestamp"
    MODULE_COLS   = [c for c in df.columns if c not in [RESIDENT_COL, SCORE_COL, FLAG_COL, DATE_COL]]

    # ── Page: Overview ────────────────────────────────────────────────────────────
    if page == "🏠 Overview":
        st.title("🦷 AIDM Resident Performance Overview")
        st.caption(f"Data refreshed · {datetime.now().strftime('%d %b %Y, %H:%M')}")

        col1, col2, col3, col4 = st.columns(4)
        total   = len(df[RESIDENT_COL].unique()) if RESIDENT_COL in df.columns else len(df)
        flagged = len(df[df[FLAG_COL].str.upper().str.contains("RED|AMBER", na=False)]) if FLAG_COL in df.columns else 0
        avg_score = round(df[SCORE_COL].mean(), 1) if SCORE_COL in df.columns else "N/A"
        top_score = df[SCORE_COL].max() if SCORE_COL in df.columns else "N/A"

        col1.metric("Total Residents", total)
        col2.metric("Flagged", flagged, delta=None)
        col3.metric("Avg Score", avg_score)
        col4.metric("Top Score", top_score)

        if SCORE_COL in df.columns and RESIDENT_COL in df.columns:
            fig = px.bar(
                df.sort_values(SCORE_COL, ascending=False),
                x=RESIDENT_COL, y=SCORE_COL,
                color=FLAG_COL if FLAG_COL in df.columns else None,
                color_discrete_map={"RED": "#ff4b4b", "AMBER": "#ffa500", "GREEN": "#21c354"},
                title="Score Distribution by Resident",
            )
            fig.update_layout(xaxis_tickangle=-45, height=420)
            st.plotly_chart(fig, width="stretch")

    # ── Page: Leaderboard ─────────────────────────────────────────────────────────
    elif page == "📊 Leaderboard":
        st.title("📊 Leaderboard")
        if SCORE_COL in df.columns:
            lb = df.sort_values(SCORE_COL, ascending=False).reset_index(drop=True)
            lb.index += 1
            lb.index.name = "Rank"
            st.dataframe(lb, width="stretch")
        else:
            st.dataframe(df, width="stretch")

    # ── Page: My Profile ──────────────────────────────────────────────────────────
    elif page == "🎯 My Profile":
        st.title("🎯 My Profile")
        if RESIDENT_COL in df.columns:
            residents = sorted(df[RESIDENT_COL].dropna().unique().tolist())
            selected  = st.selectbox("Select Resident", residents)
            row = df[df[RESIDENT_COL] == selected].iloc[-1]  # latest record

            st.subheader(f"Performance: {selected}")
            c1, c2 = st.columns(2)
            if SCORE_COL in df.columns:
                c1.metric("Total Score", row[SCORE_COL])
            if FLAG_COL in df.columns:
                flag = str(row[FLAG_COL]).upper()
                colour = "flag-red" if flag == "RED" else "flag-amber" if flag == "AMBER" else "flag-green"
                c2.markdown(f'<span class="{colour}">Status: {flag}</span>', unsafe_allow_html=True)

            if MODULE_COLS:
                values = []
                for mc in MODULE_COLS:
                    try:
                        values.append(float(row[mc]))
                    except Exception:
                        values.append(0)
                fig = go.Figure(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=MODULE_COLS + [MODULE_COLS[0]],
                    fill="toself",
                    line_color="#00d4ff",
                ))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Module Radar")
                st.plotly_chart(fig, width="stretch")
        else:
            st.info("Resident Name column not found in sheet.")

    # ── Page: Flagged Residents ────────────────────────────────────────────────────
    elif page == "🚩 Flagged Residents":
        st.title("🚩 Flagged Residents")
        if FLAG_COL in df.columns:
            red   = df[df[FLAG_COL].str.upper() == "RED"]
            amber = df[df[FLAG_COL].str.upper() == "AMBER"]

            st.subheader(f"🔴 RED ({len(red)})")
            if not red.empty:
                st.dataframe(red, width="stretch")
            else:
                st.success("No RED-flagged residents.")

            st.subheader(f"🟠 AMBER ({len(amber)})")
            if not amber.empty:
                st.dataframe(amber, width="stretch")
            else:
                st.success("No AMBER-flagged residents.")
        else:
            st.info("Flag Status column not found in sheet.")

if __name__ == "__main__":
    main()
