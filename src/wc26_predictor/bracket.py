"""Round of 32 bracket resolution and single-elimination knockout simulation"""

from __future__ import annotations

import json
from pathlib import Path

from . import elo
from .teams import Team


def load_bracket_template(path: Path) -> list[str]:
    """Load the round-of-32 slot template
    
    The template is a flat list of 32 slot codes in match order

    Slot codes are either:
        - "1A" / "2A" etc. -> the 1st or 2nd placed team from groups A-L
        - "3rd_1" .. "3rd_8" -> the nth best 3rd-placed team overall,
          ranked by points/GD/GF
    """
    with open(path) as f:
        return json.load(f)["round_of_32_slots"]
    

def resolve_slots(
    template: list[str],
    winners: dict[str, Team],
    runners_up: dict[str, Team],
    best_thirds: list[tuple[str, Team]],
) -> list[Team]:
    """Map the slot template to actual Team objects for this simulation run"""
    third_lookup = {f"3rd_{i + 1}": team for i, (_, team) in enumerate(best_thirds)}

    resolved: list[Team] = []
    for slot in template:
        if slot.startswith("3rd_"):
            resolved.append(third_lookup[slot])
        else:
            position, group = slot[0], slot[1]
            if position == "1":
                resolved.append(winners[group])
            elif position == "2":
                resolved.append(runners_up[group])
            else:
                raise ValueError(f"Urecognised bracket slot code: {slot!r}")
            
    if len(resolved) != 32:
        raise ValueError(
            f"Bracket template must resolve to exactly 32 teams, got {len(resolved)}"
        )
    return resolved


def play_knockout_match(team_a: Team, team_b: Team, rng) -> Team:
    """Simulate a knockout match. Draws after 90 minutes go to penalties"""
    goals_a, goals_b = elo.simulate_scoreline(
        team_a.effective_elo, team_b.effective_elo, rng
    )
    if goals_a != goals_b:
        return team_a if goals_a > goals_b else team_b
    
    p_a = elo.knockout_win_probability(team_a.effective_elo, team_b.effective_elo)
    return team_a if rng.random() < p_a else team_b


def simulate_knockouts(slot_teams: list[Team], rng) -> dict[str, list[Team]]:
    """Simulate the full 32-team single elimination bracket"""
    rounds: dict[str, list[Team]] = {"round_of_32": list(slot_teams)}

    progression = ["round_of_16", "quarter_finals", "semi_finals", "final"]
    current = slot_teams
    for stage_name in progression:
        winners = [
            play_knockout_match(current[i], current[i + 1], rng)
            for i in range(0, len(current), 2)
        ]
        rounds[stage_name] = winners
        current = winners

    # `current` now holds the two finalists. Simulate the final itself
    # rather than defaulting to whichever finalist is first in the list
    rounds["champion"] = play_knockout_match(current[0], current[1], rng)
    return rounds