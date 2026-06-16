"""Optional FastAPI layer exposing bracket predictions over HTTP

Run with:
    uvicorn wc26_predictor.api:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import bracket, config, simulate, teams

app = FastAPI(
    title="WC26 Bracket Predictor API",
    description="Knockout-stage probabilities for the 2026 FIFA World Cup",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@app.get("/teams")
def get_teams() -> dict:
    """Return all 48 teams with their group and Elo rating"""
    teams_by_name = teams.load_teams(_DATA_DIR / "teams.json")
    return {
        name: {"group": team.group, "elo": team.elo}
        for name, team in teams_by_name.items()
    }


@app.get("/predictions")
def get_predictions(simulations: int = config.DEFAULT_SIMULATIONS) -> dict:
    """Run the simulation and return per-team stage probabilities
    
    Note: this runs the simulation on every request. For a dashboard,
    cache the result (e.g. with `functools.lru_cache` keyed on
    `simulations`, or a scheduled job that writes to a file/DB) rather
    than recomputing on each page load
    """
    teams_by_name = teams.load_teams(_DATA_DIR / "teams.json")
    teams_by_group = teams.group_teams(teams_by_name)
    bracket_template = bracket.load_bracket_template(_DATA_DIR / "bracket-r32.json")

    sim_results = simulate.run_simulations(
        teams_by_name, teams_by_group, bracket_template, simulations
    )

    return {
        name: {stage: round(prob, 4) for stage, prob in probs.items()}
        for name, probs in sim_results.items()
    }