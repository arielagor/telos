"""Offline tests for the council's JSON extraction + adapter normalisation.

No network calls — these exercise the parsing/robustness layer the live council depends on.
"""

from telos.adapters.generic_llm import _normalize
from telos.council import extract_json


def test_extract_plain_object():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_fenced_json():
    text = "Sure!\n```json\n{\"goal_inference\": 0.8, \"x\": 1}\n```\nhope that helps"
    assert extract_json(text) == {"goal_inference": 0.8, "x": 1}


def test_extract_prose_wrapped():
    text = 'Here is my verdict: {"score": 0.5, "rationale": "ok"} — done.'
    assert extract_json(text) == {"score": 0.5, "rationale": "ok"}


def test_extract_array():
    assert extract_json("answer: [1, 2, 3]") == [1, 2, 3]


def test_extract_nested_braces_balanced():
    text = '{"outer": {"inner": [1, {"k": "v}"}]}, "done": true}'
    obj = extract_json(text)
    assert obj["done"] is True and obj["outer"]["inner"][1]["k"] == "v}"


def test_extract_invalid_returns_none():
    assert extract_json("no json here at all") is None
    assert extract_json("") is None


def test_normalize_coerces_messy_reading():
    raw = {
        "goals": [
            {"description": "ship", "scope": "Collective", "owner": "team", "implicit": "yes"},
            {"description": "win", "scope": "individual"},
            "garbage",
        ],
        "conflicts": [["a", "b"], {"a": "x", "b": "y", "explanation": "z"}],
        "refused": 1,
    }
    out = _normalize(raw)
    assert out["goals"][0]["scope"] == "collective"
    assert out["goals"][0]["implicit"] is True
    assert out["goals"][1]["owner"] == "unknown"
    assert len(out["goals"]) == 2  # "garbage" dropped
    assert out["conflicts"][0] == {"a": "a", "b": "b", "explanation": ""}
    assert out["refused"] is True
