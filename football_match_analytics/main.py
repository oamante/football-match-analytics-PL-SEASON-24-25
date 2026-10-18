
from pathlib import Path
import pandas as pd

# Dataset and output file paths
DATA_FILE = Path(__file__).parent / "E0.csv"
OUTPUT_FILE = Path(__file__).parent / "league_table.csv"


def load_matches(file_path):
    """Load and validate the match dataset."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}\n"
            "Place E0.csv beside main.py."
        )

    matches = pd.read_csv(file_path)

    required_columns = [
        "HomeTeam", "AwayTeam", "FTHG", "FTAG"
    ]

    missing = [
        column for column in required_columns
        if column not in matches.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    # Remove rows without team names or valid scores.
    matches["FTHG"] = pd.to_numeric(
        matches["FTHG"], errors="coerce"
    )
    matches["FTAG"] = pd.to_numeric(
        matches["FTAG"], errors="coerce"
    )

    matches = matches.dropna(
        subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    ).copy()

    # Keep completed football scores as whole numbers.
    matches = matches[
        (matches["FTHG"] >= 0)
        & (matches["FTAG"] >= 0)
        & (matches["FTHG"] % 1 == 0)
        & (matches["FTAG"] % 1 == 0)
    ].copy()

    matches["FTHG"] = matches["FTHG"].astype(int)
    matches["FTAG"] = matches["FTAG"].astype(int)

    if matches.empty:
        raise ValueError("No valid match results found.")

    return matches


def calculate_table(matches):
    """Calculate league standings from match results."""

    teams = {}

    for _, match in matches.iterrows():
        home = match["HomeTeam"]
        away = match["AwayTeam"]
        home_goals = int(match["FTHG"])
        away_goals = int(match["FTAG"])

        for team in (home, away):
            if team not in teams:
                teams[team] = {
                    "MP": 0,
                    "W": 0,
                    "D": 0,
                    "L": 0,
                    "GF": 0,
                    "GA": 0,
                    "Pts": 0,
                }

        # Matches played and goals.
        teams[home]["MP"] += 1
        teams[away]["MP"] += 1

        teams[home]["GF"] += home_goals
        teams[home]["GA"] += away_goals

        teams[away]["GF"] += away_goals
        teams[away]["GA"] += home_goals

        # Determine the result.
        if home_goals > away_goals:
            teams[home]["W"] += 1
            teams[home]["Pts"] += 3
            teams[away]["L"] += 1

        elif home_goals < away_goals:
            teams[away]["W"] += 1
            teams[away]["Pts"] += 3
            teams[home]["L"] += 1

        else:
            teams[home]["D"] += 1
            teams[away]["D"] += 1
            teams[home]["Pts"] += 1
            teams[away]["Pts"] += 1

    table = pd.DataFrame.from_dict(teams, orient="index")
    table.index.name = "Team"

    table["GD"] = table["GF"] - table["GA"]

    table = table.sort_values(
        by=["Pts", "GD", "GF"],
        ascending=[False, False, False],
    )

    table.insert(0, "Pos", range(1, len(table) + 1))

    return table.reset_index()


def calculate_recent_form(matches):
    """Calculate each team's last five results, oldest to newest."""

    matches = matches.copy()

    if "Date" not in matches.columns:
        print("Warning: No Date column; recent form unavailable.")
        return {}

    matches["Date"] = pd.to_datetime(
        matches["Date"],
        dayfirst=True,
        errors="coerce",
    )

    matches = matches.dropna(subset=["Date"])
    matches = matches.sort_values("Date", kind="stable")

    form = {}

    for _, match in matches.iterrows():
        home = match["HomeTeam"]
        away = match["AwayTeam"]
        home_goals = int(match["FTHG"])
        away_goals = int(match["FTAG"])

        if home_goals > away_goals:
            home_result, away_result = "W", "L"
        elif home_goals < away_goals:
            home_result, away_result = "L", "W"
        else:
            home_result, away_result = "D", "D"

        form.setdefault(home, []).append(home_result)
        form.setdefault(away, []).append(away_result)

    # Only the five most recent matches for each team.
    return {
        team: "".join(results[-5:])
        for team, results in form.items()
    }


def show_head_to_head(matches, team_a, team_b):
    """Display matches between two teams."""

    games = matches[
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

    print(f"\nHEAD-TO-HEAD: {team_a} vs {team_b}")
    print("-" * 45)

    if games.empty:
        print("No matches found between these teams.")
        return

    columns = [
        column for column in
        ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        if column in games.columns
    ]

    print(games[columns].to_string(index=False))

    print(f"\nMatches found: {len(games)}")


def main():
    """Run the football analytics program."""

    print("=" * 55)
    print("          FOOTBALL MATCH ANALYTICS")
    print("=" * 55)

    try:
        matches = load_matches(DATA_FILE)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"Error: {error}")
        return

    print(f"\nValid matches loaded: {len(matches)}")

    if "Date" in matches.columns:
        dates = pd.to_datetime(
            matches["Date"], dayfirst=True, errors="coerce"
        ).dropna()

        if not dates.empty:
            print(
                f"Date range: {dates.min().date()} "
                f"to {dates.max().date()}"
            )

    print("\nSAMPLE MATCHES")
    print(matches.head().to_string(index=False))

    # Calculate the league table and recent form.
    table = calculate_table(matches)
    recent_form = calculate_recent_form(matches)

    table["Last 5"] = (
        table["Team"].map(recent_form).fillna("Unavailable")
    )

    print("\nFINAL LEAGUE TABLE")
    print("=" * 100)
    print(table.to_string(index=False))

    # Export the results.
    table.to_csv(OUTPUT_FILE, index=False)
    print(f"\nLeague table saved to: {OUTPUT_FILE}")

    # Head-to-head analysis.
    print("\nHEAD-TO-HEAD ANALYSIS")
    print("Enter team names as shown in the league table.")
    print("Press Enter at the first prompt to skip this section.")

    team_lookup = {
        team.casefold(): team
        for team in table["Team"]
    }

    team_a_input = input("\nFirst team: ").strip()

    if not team_a_input:
        print("\nAnalysis complete.")
        return

    team_b_input = input("Second team: ").strip()

    team_a = team_lookup.get(team_a_input.casefold())
    team_b = team_lookup.get(team_b_input.casefold())

    if team_a is None:
        print(f"Team not found: {team_a_input}")
    elif team_b is None:
        print(f"Team not found: {team_b_input}")
    else:
        show_head_to_head(matches, team_a, team_b)

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
