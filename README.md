# decision-layer-bench

**This benchmark tests Jev and the models built like it** — TypeSafe calls them
System One models; around ten open replicas now exist. They are small typed
models that answer a classification question directly: you hand one the options,
it returns one of them plus a confidence, in place of an LLM call inside a
pipeline.

It measures them against each other, and against the LLM calls they are meant to
replace — the LLMs are reference rows here, not the subject.

The pitch for the category is threefold: nearly as accurate as the LLM you
removed, far cheaper, and sure enough of itself that you can threshold on its
confidence and escalate the rest to a bigger model. This benchmark takes that
pitch apart into things that can be measured, and measures them on real
decisions.

## What it measures

**Accuracy on a real label space.** Not a binary safety flag — thirty classes
with overlapping meanings, supplied as names only. No worked examples, which is
also all the interface offers: a decision layer takes options and criteria, not
demonstrations. The model has to arrive already knowing what the labels mean.

**Cost per correct answer.** Not total spend. An arm that is cheap and wrong is
not cheap, and the whole argument for the category is an efficiency argument, so
efficiency is the column.

**Error structure.** Two arms on the same score can fail differently — a slip to
a neighbouring abstraction level is a different production problem from a
misread. The run report splits them.

Accuracy is not expected to separate the strongest arms, and nothing here
pretends otherwise. On the design probe the top three landed inside two points
of each other while the full range across model tiers spanned about fifty. Cost
and error structure are what separate arms once accuracy saturates.

## Tasks

| task | the decision | options | n |
|---|---|---|---|
| [`cve_weakness_class`](tasks/cve_weakness_class) | a published vulnerability description → the weakness class behind it | 30 | 1,500 |

One task today. The suite grows by adding decisions of a different shape, not by
adding more of the same material.

## Running one

Each task directory holds `inputs/task.md` with the instructions and the option
list, and one directory per case. Answers are not in this repository. Scores go
on the board at [trapstreet.run](https://trapstreet.run), which runs each task's
own judge, so every arm is scored by the same code on the same items.

## How this is built

Two things are worth knowing before you trust a number from here.

**The floor is published, not engineered away.** Every task ships the score that
trivial strategies reach — string matching, constant answers, random — measured
through the real judge on the real case set. On `cve_weakness_class` a lexical
matcher scores 0.541, because CVE descriptions often name their own weakness
class in prose. That is what the material is. It is published as the bar to
clear rather than filtered out to make the numbers look better.

**Leaks are found by probing, and the list is never finished.** The first build
of `cve_weakness_class` shipped 16 cases whose text cited the answer's CWE
identifier. The second shipped 13 citing a CVE identifier, which NVD resolves to
the answer in one public request. The third had 57 cases sharing description
text with another case, which are not independent draws. Each was caught by a
probe added after the previous one had already passed. Where a channel cannot be
closed, it is disclosed instead: `cve_weakness_class` publishes NVD's
descriptions verbatim, so a solver with a search engine can find the source
record, and no filter changes that.

## Contributing

Submissions are welcome, and a replica author's own model is the most useful
thing that could appear on these boards. Running a task and putting the result
up takes about ten minutes and is scored by the task's judge, not by ours
separately.

## Licensing

MIT for the task construction, judges and graders — see [LICENSE](./LICENSE).
The vulnerability records in `cve_weakness_class` come from NIST's National
Vulnerability Database, which places its data in the public domain, and the
weakness classes from MITRE's CWE™, released for free public use. Each task's
README carries its own acknowledgements; neither NIST nor MITRE endorses this
benchmark.
