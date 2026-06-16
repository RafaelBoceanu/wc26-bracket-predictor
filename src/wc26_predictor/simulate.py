"""Run the full tournament N times and aggregate 
how often each team reaches eact stage"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from . import bracket, group_stage
from .teams import Team

STAGES = [
    "group_stage",
    "round_of_32",
    "round_of_16",
    "quarter_finals",
    "semi_finals",
    "final",
    "champion",
]


def run_simulations(
    teams_by_name: dict[str, Team],
    teams_by_group: dict[str, list[Team]],
    bracket_template: list[str],
    n_simulations: int,
    seed: int = 42,
) -> dict[str, dict[str, float]]:
    """Run the tournament `n_simulations` times and return per-team
    probabilities of reaching each stage
    
    Every team is guaranteed to reach the group stage with probability of 1.0,
    which is the starting point for all 48 teams, not an outcome of the
    simulation
    """
    rng = np.random.default_rng(seed)
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for name in teams_by_name:
        counts[name]["group_stage"] = n_simulations

    for _ in range(n_simulations):
        group_results = group_stage.simulate_all_groups(teams_by_group, rng)
        winners, runners_up, best_thirds = group_stage.select_qualifiers(
            group_results, rng
        )
        slot_teams = bracket.resolve_slots(
            bracket_template, winners, runners_up, best_thirds
        )
        knockout_results = bracket.simulate_knockouts(slot_teams, rng)

        for stage_name, value in knockout_results.items():
            if stage_name == "champion":
                counts[value.name]["champion"] += 1
            else:
                for team in value:
                    counts[team.name][stage_name] += 1

    return {
        name: {
            stage: stage_counts.get(stage, 0) / n_simulations for stage in STAGES
        }
        for name, stage_counts in counts.items()
    }