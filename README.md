# ⚽ Football Match Analytics

An interactive football analytics dashboard built with **Python, Pandas, and Streamlit**, using English Premier League match data from the 2024–25 season.

The project explores team performance, league standings, recent form, goals scored and conceded, and head-to-head results through a simple web interface.

## Features

- **League Table:** Calculate league positions, matches played, wins, draws, losses, goals for, goals against, goal difference, and points.
- **Recent Form:** Review a team's results from its last five recorded matches.
- **Team Analysis:** Explore a team's performance and goal statistics.
- **Team Comparison:** Compare two Premier League teams.
- **Head-to-Head Analysis:** Examine previous results between selected teams.
- **Interactive Dashboard:** Explore the data using Streamlit.
- **CSV Export:** Download the calculated league table for further analysis.

## Tech Stack

- Python
- Pandas
- Streamlit

## Dataset

The project uses English Premier League match results from the 2024–25 season.

**Data source:** [Football-Data.co.uk](https://www.football-data.co.uk/)

The dataset includes home and away teams, full-time goals, and other match information.

## Project Structure

```text
football_match_analytics/
├── app.py
├── main.py
├── E0.csv
├── league_table.csv
└── README.md
```

- `app.py` — Interactive Streamlit dashboard.
- `main.py` — Python script for match analysis and league table calculations.
- `E0.csv` — Source match dataset.
- `league_table.csv` — Generated league table, when exported by the analysis script.
- `README.md` — Project documentation.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/football-match-analytics.git
cd football-match-analytics
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Install dependencies

```bash
py -m pip install pandas streamlit
```

### 3. Run the dashboard

```bash
py -m streamlit run app.py
```

Streamlit will provide a local URL that you can open in your browser.

### 4. Run the analysis script

```bash
py main.py
```

## Project Goal

The goal of this project is to apply Python programming and data analysis to football, turning raw match results into useful team statistics and interactive comparisons.

It also serves as a practical project for developing skills in data handling, calculations, visualization, and application development.

## Future Improvements

- Add match outcome predictions using machine learning.
- Include additional seasons to compare long-term team performance.
- Add home-versus-away performance analysis.
- Improve visualizations and dashboard design.
- Add player-level statistics where suitable data is available.

## Disclaimer

This project is intended for educational and analytical purposes. Historical match statistics do not guarantee future match outcomes.

---

**Built with Python and a passion for football.**
