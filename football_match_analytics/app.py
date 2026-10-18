
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Football Match Analytics",
    page_icon="⚽",
    layout="wide",
)

DATA_FILE = Path(__file__).parent / "E0.csv"


@st.cache_data
def load_data():
    matches = pd.read_csv(DATA_FILE)

    required = ["HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    missing = [column for column in required if column not in matches.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    matches["FTHG"] = pd.to_numeric(matches["FTHG"], errors="coerce")
    matches["FTAG"] = pd.to_numeric(matches["FTAG"], errors="coerce")

    matches = matches.dropna(
        subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    ).copy()

    matches = matches[
        (matches["FTHG"] >= 0)
        & (matches["FTAG"] >= 0)
        & (matches["FTHG"] % 1 == 0)
        & (matches["FTAG"] % 1 == 0)
    ].copy()

    matches["FTHG"] = matches["FTHG"].astype(int)
    matches["FTAG"] = matches["FTAG"].astype(int)

    if "Date" in matches.columns:
        matches["Date"] = pd.to_datetime(
            matches["Date"], dayfirst=True, errors="coerce"
        )

    return matches


def build_table(matches):
    stats = {}

    for _, match in matches.iterrows():
        home = match["HomeTeam"]
        away = match["AwayTeam"]
        hg = int(match["FTHG"])
        ag = int(match["FTAG"])

        for team in (home, away):
            if team not in stats:
                stats[team] = {
                    "MP": 0, "W": 0, "D": 0, "L": 0,
                    "GF": 0, "GA": 0, "Pts": 0,
                }

        stats[home]["MP"] += 1
        stats[away]["MP"] += 1

        stats[home]["GF"] += hg
        stats[home]["GA"] += ag
        stats[away]["GF"] += ag
        stats[away]["GA"] += hg

        if hg > ag:
            stats[home]["W"] += 1
            stats[home]["Pts"] += 3
            stats[away]["L"] += 1
        elif hg < ag:
            stats[away]["W"] += 1
            stats[away]["Pts"] += 3
            stats[home]["L"] += 1
        else:
            stats[home]["D"] += 1
            stats[away]["D"] += 1
            stats[home]["Pts"] += 1
            stats[away]["Pts"] += 1

    table = pd.DataFrame.from_dict(stats, orient="index")
    table.index.name = "Team"
    table["GD"] = table["GF"] - table["GA"]

    table = table.sort_values(
        ["Pts", "GD", "GF"],
        ascending=[False, False, False],
    ).reset_index()

    table.insert(0, "Pos", range(1, len(table) + 1))
    return table


def build_form(matches):
    if "Date" not in matches.columns:
        return {}

    dated = matches.dropna(subset=["Date"]).sort_values("Date")
    results = {}

    for _, match in dated.iterrows():
        home, away = match["HomeTeam"], match["AwayTeam"]
        hg, ag = int(match["FTHG"]), int(match["FTAG"])

        if hg > ag:
            home_result, away_result = "W", "L"
        elif hg < ag:
            home_result, away_result = "L", "W"
        else:
            home_result, away_result = "D", "D"

        results.setdefault(home, []).append(home_result)
        results.setdefault(away, []).append(away_result)

    return {
        team: "".join(values[-5:])
        for team, values in results.items()
    }


st.title("⚽ Football Match Analytics")
st.caption("English Premier League match data · CSV-powered analysis")

if not DATA_FILE.exists():
    st.error("E0.csv was not found. Place it in the same folder as app.py.")
    st.stop()

try:
    matches = load_data()
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

if matches.empty:
    st.error("No valid match results were found in the CSV.")
    st.stop()

table = build_table(matches)
form = build_form(matches)
table["Last 5"] = table["Team"].map(form).fillna("Unavailable")

st.sidebar.header("Dashboard")
teams = sorted(table["Team"].tolist())
selected_team = st.sidebar.selectbox("Select a team", teams)

first_date = matches["Date"].min() if "Date" in matches.columns else None
last_date = matches["Date"].max() if "Date" in matches.columns else None

col1, col2, col3, col4 = st.columns(4)
col1.metric("Teams", len(table))
col2.metric("Matches analysed", len(matches))
col3.metric("Top team", table.iloc[0]["Team"])
col4.metric("Top points", int(table.iloc[0]["Pts"]))

if first_date is not None and pd.notna(first_date):
    st.caption(f"Dataset dates: {first_date.date()} to {last_date.date()}")

st.subheader("League Table")
st.dataframe(table, hide_index=True, use_container_width=True)

st.download_button(
    "Download league table CSV",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name="league_table.csv",
    mime="text/csv",
)

st.divider()
st.subheader(f"Team Profile: {selected_team}")

team_row = table.loc[table["Team"] == selected_team].iloc[0]

a, b, c, d = st.columns(4)
a.metric("League position", int(team_row["Pos"]))
b.metric("Points", int(team_row["Pts"]))
c.metric("Goal difference", int(team_row["GD"]))
d.metric("Last five", team_row["Last 5"])

st.write("### Goals scored vs conceded")
goal_chart = pd.DataFrame({
    "Goals": ["Scored", "Conceded"],
    "Total": [int(team_row["GF"]), int(team_row["GA"])],
})
st.bar_chart(goal_chart.set_index("Goals"))

st.write("### Compare two teams")
left, right = st.columns(2)

with left:
    team_a = st.selectbox("First team", teams, index=teams.index(selected_team))

with right:
    team_b_options = [team for team in teams if team != team_a]
    team_b = st.selectbox("Second team", team_b_options)

if st.button("Compare teams", type="primary"):
    comparison = table[table["Team"].isin([team_a, team_b])].set_index("Team")
    st.dataframe(
        comparison[["Pos", "MP", "W", "D", "L", "GF", "GA", "GD", "Pts", "Last 5"]],
        use_container_width=True,
    )

    head_to_head = matches[
        (
            (matches["HomeTeam"] == team_a)
            & (matches["AwayTeam"] == team_b)
        )
        |
        (
            (matches["HomeTeam"] == team_b)
            & (matches["AwayTeam"] == team_a)
        )
    ]

    st.write("### Head-to-head matches")
    if head_to_head.empty:
        st.info("No matches between these teams were found in this dataset.")
    else:
        columns = [
            col for col in ["Date", "HomeTeam", "FTHG", "FTAG", "AwayTeam"]
            if col in head_to_head.columns
        ]
        st.dataframe(
            head_to_head[columns].sort_values(
                "Date" if "Date" in columns else "HomeTeam"
            ),
            hide_index=True,
            use_container_width=True,
        )

st.caption(
    "Analysis is calculated from the supplied dataset. "
    "Recent form is ordered from oldest to newest among each team's last five recorded matches."
)
