"""Group stage simulation: round-robin matches, standings, and qualification"""

from __future__ import annotations

from itertools import combinations
from typing import Any

from . import elo
from .teams import Team


def play_match(team_a: Team, team_b: Team, rng) -> tuple[int, int]:
    """Simulate a single group-stage match and return the scoreline"""
    return elo.simulate_scoreline(team_a.effective_elo, team_b.effective_elo, rng)

def simulate_group(teams: list[Team], rng) -> list[dict[str, Any]]:
    """Simulate a full round-robin group of 4 teams (6 matched)
    
    Returns standings as a list of stat dicts, ordered 1st-4th, using
    points, then goal difference, then goals scored as tiebreakers, with
    a random tiebreak as the final fallback. Head-to-head and fair-play
    tiebreakers from the official rules are intentionally not modelled as
    they are rarely decisive across thousands of simulations and adding
    them would add complexity for negligible accuracy gain
    """
    stats = {
        t.name: {"team": t, "pts": 0, "gf": 0, "ga": 0, "gd": 0} for t in teams
    }

    for team_a, team_b in combinations(teams, 2):
        goals_a, goals_b = play_match(team_a, team_b, rng)

        stats[team_a.name]["gf"] += goals_a
        stats[team_a.name]["ga"] += goals_b
        stats[team_b.name]["gf"] += goals_b
        stats[team_b.name]["ga"] += goals_a

        if goals_a > goals_b:
            stats[team_a.name]["pts"] += 3
        elif goals_b > goals_a:
            stats[team_b.name]["pts"] += 3
        else:
            stats[team_a.name]["pts"] += 1
            stats[team_b.name]["pts"] += 1
    
    for s in stats.values():
        s["gd"] = s["gf"] - s["ga"]

    return sorted(
        stats.values(),
        key=lambda s: (s["pts"], s["gd"], s["gf"], rng.random()),
        reverse=True,
    )

def simulate_all_groups(
        teams_by_group: dict[str, list[Team]], rng
) -> dict[str, list[dict[str, Any]]]:
    """Simulate all 12 groups. Returns standings"""
    return {group: simulate_group(teams, rng) for group, teams in teams_by_group.items()}


def select_qualifiers(
        group_results: dict[str, list[dict[str, Any]]], rng
) -> tuple[dict[str, Team], dict[str, Team], list[tuple[str, Team]]]:
    """Determine the 24 automatic qualifiers and the 8 best third-place teams
    
    Returns:
        winners for each group's 1st place
        runners_up for each group's 2nd place
        best_thirds for the 8 best 3rd-placed 
            teams across all 12 groups, ranked by points/GD/GF
    """
    winners: dict[str, Team] = {}
    runners_up: dict[str, Team] = {}
    thirds: list[tuple[str, dict[str, Any]]] = []

    for group, standings in group_results.items():
        winners[group] = standings[0]["team"]
        runners_up[group] = standings[1]["team"]
        thirds.append((group, standings[2]))

    thirds_sorted = sorted(
        thirds,
        key=lambda gs: (gs[1]["pts"], gs[1]["gd"], gs[1]["gf"], rng.random()),
        reverse=True,
    )
    best_thirds = [(group, stat["team"]) for group, stat in thirds_sorted[:8]]

    return winners, runners_up, best_thirds