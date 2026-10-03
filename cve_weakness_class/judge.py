"""Per-case judge for cve_weakness_class.

Deterministic: exact match of the chosen CWE identifier against the one the
assigning security organisation recorded in NVD. No LLM, no network -- the
grading worker has neither.

Two things worth knowing about the scoring:

1. **Parsing is permissive, scoring is not.** `ANSWER: CWE-79` is the documented
   form, but a solution that prints the identifier without the marker still gets
   read: the last valid identifier in stdout wins. An anchored regex once cost a
   run 23 answers on another task, and a parse failure is not the capability
   being measured. What is *not* forgiving is the answer itself -- it must be
   one of the 30 declared options and it must match.

2. **Hierarchy is reported, never scored.** CWE is a DAG: CWE-79 is a child of
   CWE-74, and an analyst can legitimately record either. 21-35% of every arm's
   errors are a parent or child of the gold. Giving partial credit would bake
   one abstraction level into the metric, so a near-miss scores 0.0 and is
   surfaced as `parent_child: true` for the grader to aggregate. The board then
   shows who errs by abstraction and who errs by misreading the flaw.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

CWE = re.compile(r"CWE-\d+", re.IGNORECASE)
ANSWER_LINE = re.compile(r"ANSWER\s*[:\-]?\s*(CWE-\d+)", re.IGNORECASE)
# Confidence is RECORDED, never scored: a wrong answer held confidently and a
# wrong answer held loosely are the same zero. The difference belongs in a
# column of the report, not on the thumb of the scale.
# Match any number and range-check in code. A regex that matched only 0-1
# clipped "1.7" to its leading "1" and recorded total confidence for a value
# that was never valid -- silently inflating the calibration column.
CONF_LINE = re.compile(r"CONFIDENCE\s*[:=\-]?\s*(\d*\.?\d+)", re.IGNORECASE)
# An arm whose provider tp cannot meter reports its own spend on this line.
# The grader sums it as self-reported cost, apart from metered figures. The
# judge is the only thing that reads a case's stdout, so if it does not carry
# the number into metrics the grader has nothing to sum -- which is how the
# first Jev run reached the board with an empty cost column.
COST_LINE = re.compile(r"UNMETERED_COST_USD\s*[:=]?\s*(\d*\.?\d+)", re.IGNORECASE)
OPTIONS = set(json.loads((Path(__file__).resolve().parent / "options.json").read_text()))


def parse(stdout: str) -> str | None:
    """Prefer the documented ANSWER marker; else the last valid identifier."""
    hits = [m.group(1).upper() for m in ANSWER_LINE.finditer(stdout)]
    for h in reversed(hits):
        if h in OPTIONS:
            return h
    for h in reversed([m.group(0).upper() for m in CWE.finditer(stdout)]):
        if h in OPTIONS:
            return h
    return None


def parse_unmetered_cost(stdout: str) -> float | None:
    """Last self-reported spend for this case, in USD, or None."""
    for v in reversed([m.group(1) for m in COST_LINE.finditer(stdout)]):
        try:
            f = float(v)
        except ValueError:
            continue
        if f >= 0.0:
            return f
    return None


def parse_confidence(stdout: str) -> float | None:
    """Last well-formed CONFIDENCE value in [0, 1], or None."""
    for v in reversed([m.group(1) for m in CONF_LINE.finditer(stdout)]):
        try:
            f = float(v)
        except ValueError:
            continue
        if 0.0 <= f <= 1.0:
            return f
    return None


def related(a: str, b: str, tree: dict) -> bool:
    """True when one of a, b is an ancestor of the other in the CWE DAG."""
    def anc(c: str) -> set[str]:
        seen: set[str] = set()
        stack = list(tree.get(c, {}).get("parents", []))
        while stack:
            p = stack.pop()
            if p in seen:
                continue
            seen.add(p)
            stack += tree.get(p, {}).get("parents", [])
        return seen
    return b in anc(a) or a in anc(b)


def score_case(stdout: str, expected: dict, tree: dict) -> dict:
    gold = expected["cwe"]
    base = {"category": gold, "gold": gold}
    got = parse(stdout)
    if got is None:
        return {**base, "score": 0.0, "answered": False,
                "reason": "no CWE identifier from the option list in output"}
    hit = got == gold
    out = {**base, "score": 1.0 if hit else 0.0, "answered": True,
           "predicted": got,
           "parent_child": (not hit) and related(got, gold, tree),
           "reason": "correct" if hit else f"chose {got}, gold {gold}"}
    conf = parse_confidence(stdout)
    if conf is not None:
        out["confidence"] = conf
    cost = parse_unmetered_cost(stdout)
    if cost is not None:
        out["unmetered_cost_usd"] = cost
    return out


def main() -> None:
    m = json.loads(os.environ["TRAPTASK_MANIFEST"])
    expected = json.loads((Path(m["expected_dir"]) / "answer.json").read_text())
    tree = json.loads((Path(__file__).resolve().parent / "tools" / "cwe_tree.json").read_text())
    try:
        exit_code = json.loads(Path(m["run"]["meta"]).read_text()).get("exit_code")
    except Exception:
        exit_code = None
    try:
        stdout = Path(m["run"]["stdout"]).read_text(errors="replace")
    except Exception:
        stdout = ""

    if exit_code not in (0, None):
        print(json.dumps({"score": 0.0, "answered": False, "category": expected["cwe"],
                          "reason": f"solution exited {exit_code}"}))
        return
    if not stdout.strip():
        print(json.dumps({"score": 0.0, "answered": False, "category": expected["cwe"],
                          "reason": "solution produced no output"}))
        return
    print(json.dumps(score_case(stdout, expected, tree)))


if __name__ == "__main__":
    main()
