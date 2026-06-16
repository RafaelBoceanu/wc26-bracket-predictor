"""Team data model and loading"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import config


@dataclass(frozen=True)
class Team:
    name: str
    group: str
    elo: float

    @property
    def effective_elo(self) -> float:
        """Elo rating including host-nation advantage, where applicable"""
        if self.name in config.HOST_NATIONS:
            return self.elo + config.HOST_ADVANTAGE_ELO
        return self.elo
    

def load_teams(ratings_path: Path) -> dict[str, Team]:
    """Load Elo ratings from a JSON file and build Team objects
    
    The ratings file is just a flat {"Team Name": elo_rating} mapping.
    Group assignments come from `config.GROUPS`. Every team listed in
    `config.GROUPS` must have a corresponding rating, or this raises
    """
    with open(ratings_path) as f:
        ratings = json.load(f)

    teams: dict[str, Team] = {}
    for group, names in config.GROUPS.items():
        for name in names:
            if name not in ratings:
                raise ValueError(
                    f"Missing Elo raing for '{name}' in {ratings_path} "
                    "Every team in config.GROUPS must have an entry"
                )
            teams[name] = Team(name=name, group=group, elo=float(ratings[name]))
    return teams

def group_teams(teams_by_name: dict[str, Team]) -> dict[str, list[Team]]:
    """Re-index teams by group letter"""
    grouped: dict[str, list[Team]] = {}
    for team in teams_by_name.values():
        grouped.setdefault(team.group, []).append(team)
    return grouped