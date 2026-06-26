"""``telos`` CLI — run the goal-understanding benchmark against an agent.

Examples
--------
    # Score Claude as the agent-under-test (judged by the other families):
    python -m telos.bench --adapter generic --family claude

    # Score a running OmegaClaw instance:
    OMEGACLAW_ENDPOINT=http://localhost:8080/chat python -m telos.bench --adapter omegaclaw

    # Just list the scenarios:
    python -m telos.bench --list
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

from telos import harness, judge
from telos.providers import available_families

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")


def _make_adapter(args):
    if args.adapter == "generic":
        from telos.adapters.generic_llm import GenericLLMAdapter
        return GenericLLMAdapter(family=args.family, model=args.model or None), args.family
    if args.adapter == "omegaclaw":
        from telos.adapters.omegaclaw import OmegaClawAdapter
        return OmegaClawAdapter(), None
    raise SystemExit(f"unknown adapter {args.adapter!r}")


def _print_report(report: dict) -> None:
    print(f"\n=== Telos Goal-Understanding Benchmark — {report['adapter']} ===")
    print(f"scenarios: {report['n_scenarios']}   OVERALL: {report['overall']:.3f}"
          f"   refusal_accuracy: {report['refusal_accuracy']}")
    print("\nby dimension:")
    for d, v in report["by_dimension"].items():
        print(f"  {d:22s} {v:.3f}")
    print("\nby category:")
    for c, v in report["by_category"].items():
        print(f"  {c:34s} n={v['n']}  {v['overall']:.3f}")
    failed = [s for s in report["scenarios"] if s.get("error")]
    if failed:
        print(f"\n{len(failed)} scenario(s) failed to produce a reading:")
        for s in failed:
            print(f"  [{s['id']}] {s['error'][:120]}")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Telos goal-understanding benchmark")
    ap.add_argument("--adapter", default="generic", choices=["generic", "omegaclaw"])
    ap.add_argument("--family", default="claude", help="model family for the generic adapter")
    ap.add_argument("--model", default="", help="explicit model id (optional)")
    ap.add_argument("--ids", default="", help="comma-separated scenario ids to run (default: all)")
    ap.add_argument("--judge-families", default="", help="override judge panel (default: all available)")
    ap.add_argument("--no-exclude-self", action="store_true",
                    help="allow the agent's own family to judge it (default: excluded)")
    ap.add_argument("--out", default="", help="path to write the JSON report (default: results/<adapter>.json)")
    ap.add_argument("--list", action="store_true", help="list scenarios and exit")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    scenarios = harness.load_scenarios(ids=[i.strip() for i in args.ids.split(",") if i.strip()] or None)
    if args.list:
        for s in scenarios:
            print(f"{s['id']:8s} {s['category']:34s} {s.get('title','')}")
        print(f"\n{len(scenarios)} scenarios across "
              f"{len(set(s['category'] for s in scenarios))} categories")
        return 0

    if not scenarios:
        print("no scenarios found", file=sys.stderr)
        return 2

    print(f"available model families: {available_families()}")
    adapter, own_family = _make_adapter(args)
    print(f"running adapter '{adapter.name}' over {len(scenarios)} scenarios...")
    run_result = harness.run(adapter, scenarios, verbose=args.verbose)

    exclude = None if args.no_exclude_self else own_family
    jf = [f.strip() for f in args.judge_families.split(",") if f.strip()] or None
    report = judge.score_run(run_result, exclude_family=exclude, judge_families=jf)

    out = args.out or os.path.join(RESULTS_DIR, f"{args.adapter}-{args.family}.json"
                                   if args.adapter == "generic" else f"{args.adapter}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    _print_report(report)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
