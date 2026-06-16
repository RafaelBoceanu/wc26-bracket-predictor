#!/usr/bin/env python3
"""CLI entry point for the World Cup 2026 knockout bracket predictor

Usage:
    python scripts/run_simulation.py
    python scripts/run_simulation.py --simulations 50000 --seed 7
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from wc26_predictor import bracket, config, results, simulate, teams # noqa: E402

def main() -> None:
    parser = argparse.ArgumentParser(description="WC26 Knockout Bracket Predictor")
    parser.add_argument(
        "--ratings", type=Path, default=PROJECT_ROOT / "data" / "bracket_r32.json"
    )
    parser.add_argument("--simulations", type=int, default=config.DEFAULT_SIMULATIONS)
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    parser.add_argument(
        "--out-csv", type=Path, default=PROJECT_ROOT / "output" / "predictions.csv"
    )
    parser.add_argument(
        "--out-json", type=Path, default=PROJECT_ROOT / "output" / "predictions.json"
    )
    args = parser.parse_args()

    teams_by_name = teams.load_teams(args.ratings)
    teams_by_group = teams.group_teams(teams_by_name)
    bracket_template = bracket.load_bracket_template(args.bracket)

    sim_results = simulate.run_simulations(
        teams_by_name,
        teams_by_group,
        bracket_template,
        args.simulations,
        seed=args.seed,
    )

    rows = results.to_sorted_rows(sim_results, teams_by_name)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    results.write_csv(rows, args.out_csv)
    results.write_json(rows, args.out_json)

    print(f"Ran {args.simulations:,} simulations (seed={args.seed}).\n")
    header = f"{'Team':<22}{'Group':<7}{'Champion':>10}{'Semis':>10}{'QF':>10}"
    print(header)
    print("-" * len(header))
    for row in rows[:15]:
        print(
            f"{row['team']:<22}{row['group']:<7}"
            f"{row['champion'] * 100:>9.2f}%"
            f"{row['final'] * 100:>9.2f}%"
            f"{row['semi_finals'] * 100:>9.2f}%"
            f"{row['quarter_finals'] * 100:>9.2f}%"
        )
    print(f"\nFull results written to:\n    {args.out_csv}\n   {args.out_json}")


    if __name__ == "__main__":
        main()