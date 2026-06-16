"""Elo-based match outcome model

This module converts Elo ratings into match outcome probabilities and
simulated scorelines. It deliberately favours simplicity and transparency
over statistical sophistication, the goal being a defensible, explainable
baseline that can later be swapped out for a trained model without touching the 
simulation engine
"""

from __future__ import annotations

import math

from . import config

def expected_score(elo_a: float, elo_b: float) -> float:
    """Standard Elo expected-score formula
    
    Returns team A's "win equity" in the 0-1 range, where 0.5 means an 
    even match. This combines win and draw outcomes into a single continuous
    measure (a draw counts as 0.5 of a win for each side)
    """
    return 1.0 / (1.0 + 10 ** (-(elo_a - elo_b) / 400.0))

def draw_probability(elo_a: float, elo_b: float) -> float:
    """Probability of a draw, peaking for evenly matched teams"""
    diff = elo_a - elo_b
    return config.DRAW_BASE_PROB * math.exp(
        -(diff ** 2) / (2 * config.DRAW_ELO_SCALE ** 2)
    )

def match_outcome_probabilities(elo_a: float, elo_b: float) -> tuple[float, float, float]:
    """Return (P(A wins), P(draw), P(B wins)) for a single match
    
    The win-equity from 'expected_score' is first reduced by the draw
    probability, then split between the two teams proportionally to 
    their relateive strength
    """
    we = expected_score(elo_a, elo_b)
    p_draw = draw_probability(elo_a, elo_b)
    remaining = 1.0 - p_draw
    p_a = remaining * we
    p_b = remaining * (1.0 - we)
    return p_a, p_draw, p_b

def simulate_scoreline(elo_a: float, elo_b: float, rng) -> tuple[int, int]:
    """Simulate a final score using independent Poisson goal counts
    
    Each side's expected goal rate is scaled away from the baseline rate
    according to the Elo difference. This is a simplification (real
    scorelines aren't independent Poisson processes), but it produces
    sensible goal differences for group-stage tiebreakers and a realistic
    spread of results without requiring historical goals data
    """
    diff = elo_a - elo_b
    lam_a = config.BASE_GOAL_RATE * (10 ** (diff / 800.0))
    lam_b = config.BASE_GOAL_RATE * (10 ** (-diff / 800.0))
    goals_a = rng.poisson(lam_a)
    goals_b = rng.poisson(lam_b)
    return int(goals_a), int(goals_b)

def knockout_win_probability(elo_a: float, elo_b: float) -> float:
    """Probability team A advances from a knockout tie that ends level
    
    Used to resolve penalty shootouts: a near coin-flip, lightly
    influenced by the Elo gap
    """
    return expected_score(elo_a, elo_b)