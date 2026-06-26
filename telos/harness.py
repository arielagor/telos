"""Benchmark harness — run an agent-under-test over the scenario set.

The harness is deliberately dumb: it loads scenarios, asks an adapter for each goal reading,
and records the result (or the failure). All judgement lives in :mod:`telos.judge`.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from glob import glob
from typing import Optional

from telos.adapters.base import AdapterError

SCENARIO_DIR = os.path.join(os.path.dirname(__file__), "scenarios")


@dataclass
class RunItem:
    scenario: dict
    reading: Optional[dict] = None
    error: str = ""

    @property
    def ok(self) -> bool:
        return self.reading is not None


@dataclass
class RunResult:
    adapter_name: str
    items: list[RunItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "adapter": self.adapter_name,
            "items": [
                {"id": it.scenario.get("id"), "category": it.scenario.get("category"),
                 "ok": it.ok, "error": it.error, "reading": it.reading}
                for it in self.items
            ],
        }


def load_scenarios(scenario_dir: str = SCENARIO_DIR, ids: Optional[list[str]] = None) -> list[dict]:
    out = []
    for path in sorted(glob(os.path.join(scenario_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else [data]
        for s in items:
            if ids and s.get("id") not in ids:
                continue
            s.setdefault("_source", os.path.basename(path))
            out.append(s)
    return out


def run(adapter, scenarios: list[dict], verbose: bool = False) -> RunResult:
    res = RunResult(adapter_name=getattr(adapter, "name", adapter.__class__.__name__))
    for s in scenarios:
        try:
            reading = adapter.read_goals(s)
            res.items.append(RunItem(scenario=s, reading=reading))
            if verbose:
                print(f"  [{s.get('id')}] ok ({len(reading.get('goals', []))} goals)")
        except AdapterError as e:
            res.items.append(RunItem(scenario=s, error=str(e)))
            if verbose:
                print(f"  [{s.get('id')}] FAILED: {e}")
        except Exception as e:  # noqa: BLE001 - keep the run going; one bad item shouldn't abort
            res.items.append(RunItem(scenario=s, error=f"{type(e).__name__}: {e}"))
            if verbose:
                print(f"  [{s.get('id')}] ERROR: {e}")
    return res
