# cve_weakness_class

Part of **decision-layer-bench**, which measures whether a small typed decision
model can stand in for an LLM classification call inside a pipeline.

Given the published description of one software vulnerability, name the weakness
class it belongs to — one of 30 CWE identifiers.

```
In link_load_gnss_image of link_device.c, there is a possible out-of-bounds
write due to a missing bounds check. This could lead to local escalation of
privilege with System execution privileges needed.
```

→ `ANSWER: CWE-787`

## What it measures

A decision layer answers a classification question directly, in place of an LLM
call. The pitch is that it is nearly as accurate, far cheaper, and sure enough
of itself that you can threshold on its confidence and escalate the rest. This
task puts one realistic decision under that claim.

- **Can it hit a real label space?** 30 classes with overlapping meanings,
  supplied as names only — no worked examples. A model in this class cannot pick
  the taxonomy up in context, so it has to arrive already knowing what "Use
  After Free" means.
- **Is it cheaper per unit of correct work?** Not total spend — cost per correct
  answer, and latency per case. An arm that is cheap and wrong is not cheap.
  Latency is measured for every arm; dollars only where something was billed.
- **When it misses, how does it miss?** CWE is a hierarchy, so a miss is either
  an abstraction-level slip — a parent or child of the recorded class — or an
  unrelated class. Two arms on the same score can differ sharply here, and the
  run report splits them.

Accuracy is not the column that separates the strongest arms, and this benchmark
does not pretend otherwise. Efficiency and error structure are.

## The set

1,500 cases, 50 for each of the 30 classes, no two carrying the same
description text. Each case is one CVE published
between 2026-07-01 and 2026-09-15, with the weakness class recorded for it in
the National Vulnerability Database by the organisation that assigned the CVE.

Balanced rather than natural: in the wild `CWE-284` alone is 9.4% of CVEs, and
a model that leant on the base rate would collect points for nothing. Every
class carries equal weight here, which makes the task harder than production
and makes per-class results readable.

Descriptions that cite a CWE identifier are excluded from the pool — otherwise
a regular expression would answer those without reading anything. So are
descriptions citing any CVE identifier: NVD is a public lookup, and a CVE id in
the text is an answer key one request away.

That filter does not close the channel completely, and the benchmark does not
claim it does. These descriptions are NVD's own text, published verbatim, so a
solution with a search engine can look up the string itself. Nothing in the
case set prevents that — it is the cost of using real records rather than
paraphrases. Read a score with that in mind, or run offline.

## Scoring

Exact match against the recorded CWE. Chance is 0.033.

CWE is a hierarchy: `CWE-862` (Missing Authorization) sits under `CWE-284`
(Improper Access Control), and an analyst can reasonably record either. Naming
a parent or a child of the recorded class scores zero, the same as any other
miss — partial credit would bake one abstraction level into the metric. Instead
the run report publishes what share of each arm's errors were parent-or-child
rather than unrelated, so an abstraction-level slip and a misread flaw show up
as different failures.

The run report also carries latency, cost per correct answer where the run was
priced, per-class accuracy, and the most frequent confusions.

## Baselines

Trivial predictors, run through this task's own judge over all 1,500 cases
(offline probes 2026-09-20; the board arm 2026-09-21):

| | accuracy |
|---|---|
| **lexical match to class name, per case** — the `word overlap · no model` arm | **0.478** |
| lexical match to class name, fitted over the whole set | 0.541 |
| uniform random over the 30 options | 0.033 |
| always the most frequent class in the wild | 0.033 |
| output with no identifier from the option list | 0.000 |

Two lexical rows, because the same strategy is worth different amounts under
different constraints, and only one of them is a bar a submission can be held
to. The 0.541 probe fits TF-IDF across all 1,500 descriptions at once, so it
carries corpus statistics no solution can reach — an arm sees one case and
cannot fit IDF over the other 1,499. The arm on the board scores the same idea
per case, with no corpus statistics, and reaches 0.478.

**0.478 is the floor a submission has to clear**, because it is the one
measured under the constraints every arm actually runs under. 0.541 stays
published beside it as the ceiling of the same strategy when it is handed the
whole set — an upper bound on what reading no meaning can buy, not a bar any
single-case solution could be held to.

The lexical rows are the ones that matter at all. 392 of the 1,500 descriptions
contain the recorded class's own name somewhere in the prose — "out-of-bounds
write", "SQL injection" — and a string matcher collects those for free. That
is deliberate: it is how these descriptions are written, and cropping around it
would make the task an artefact.

Accuracy is not expected to separate the strongest arms. Probing across model
tiers while designing this, the spread from a 1B open model to the best arm was
about 52 points, but the top three landed within two points of each other —
closer than 1,500 cases can resolve. What separates arms at that level is
efficiency and error structure, and the board bears that out: the top three sit
inside six thousandths of each other on accuracy and between 1.96 and 3.65
seconds per case.

Efficiency is reported two ways, and only one of them is populated for every
arm. **Latency is measured for all of them.** **Dollar cost is reported only
where the run was actually billed**, or where the arm reported its own spend —
several arms here run against a free hosted demo that takes no API key, and
their cost cells are left empty rather than filled with a figure nobody
measured. Read the empty cells as unpriced, not as free.

## Running it

Each case directory holds `description.txt`. `inputs/task.md` carries the
instructions and the full option list. Print one line:

```
ANSWER: CWE-787
```

The identifier must be one of the 30 options. Parsing is forgiving about the
marker — the last valid identifier in your output is taken — but the answer
itself must match exactly.

## Acknowledgements

Vulnerability records come from the **National Vulnerability Database**,
maintained by NIST, which places its data in the public domain.

Weakness classes come from **CWE™**, maintained by MITRE and released for free
public use. CWE is a trademark of The MITRE Corporation. Catalogue version
v4.20.

Neither NIST nor MITRE endorses this benchmark.
