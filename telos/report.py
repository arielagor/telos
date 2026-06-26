"""Build a Markdown leaderboard from the per-adapter result JSON files in results/."""

from __future__ import annotations

import glob
import json
import os

from telos.judge import DIMENSIONS

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
SHORT = {
    "goal_inference": "goal_inf",
    "scope_accuracy": "scope",
    "conflict_detection": "conflict",
    "collective_alignment": "collective",
    "beneficial_refusal": "refusal",
}


def load_reports() -> list[dict]:
    reports = []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        if os.path.basename(path).startswith(("_", "LEADER")):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                r = json.load(f)
            if "overall" in r and "by_dimension" in r:
                reports.append(r)
        except (json.JSONDecodeError, OSError):
            continue
    return reports


def build_markdown(reports: list[dict]) -> str:
    reports = sorted(reports, key=lambda r: r["overall"], reverse=True)
    head = ["agent", "overall", *[SHORT[d] for d in DIMENSIONS], "refusal_acc", "n"]
    lines = ["| " + " | ".join(head) + " |",
             "|" + "|".join(["---"] * len(head)) + "|"]
    for r in reports:
        row = [
            r["adapter"],
            f"**{r['overall']:.3f}**",
            *[f"{r['by_dimension'].get(d, 0.0):.3f}" for d in DIMENSIONS],
            ("-" if r.get("refusal_accuracy") is None else f"{r['refusal_accuracy']:.2f}"),
            str(r["n_scenarios"]),
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> int:
    reports = load_reports()
    if not reports:
        print("no result files found in results/")
        return 1
    md = build_markdown(reports)
    out = os.path.join(RESULTS_DIR, "LEADERBOARD.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("# Telos Goal-Understanding Benchmark — Leaderboard\n\n")
        f.write(md + "\n")
    print(md)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
