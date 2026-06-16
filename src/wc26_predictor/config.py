"""Static configuration and tournament data for the WC26 bracket predictor"""

GROUPS = {
    "A": ["Mexico", "South Korea", "South Africa", "Czechia"],
    "B": ["Switzerland", "Canada", "Bosnia and Herzegovina", "Qatar"],
    "C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "D": ["United States", "Turkey", "Australia", "Paraguay"],
    "E": ["Germany", "Ecuador", "Ivory Coast", "Curacao"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Iran", "Egypt", "New Zealand"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Austria", "Algeria", "Jordan"],
    "K": ["Portugal", "Colombia", "Uzbekistan", "DR Congo"],
    "L": ["England", "Croatia", "Panama", "Ghana"],
}

# Host nations get a small bump to reflect home turf advantage
HOST_NATIONS = {"United States", "Mexico", "Canada"}
HOST_ADVANTAGE_ELO = 60.0

# Match outcome model parameters
# Draw probability is modelled as peaking when two teams are evenly matched
# (diff == 0) and decaying as the ranking gap widens. These constants are tuned
# to give roughly realitic international draw rates (-24-28%) for closely 
# matched teams, dropping towad -10% for big mismatches
DRAW_BASE_PROB = 0.26
DRAW_ELO_SCALE = 600.0

# Baseline expected goals for two perfectly evenly matched teams.
# Elo difference scales this up/down per side via a logistic-style curve.
BASE_GOAL_RATE = 1.35

# Simulation defaults
DEFAULT_SIMULATIONS = 10000
DEFAULT_SEED = 42