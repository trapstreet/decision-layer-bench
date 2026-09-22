# decision-layer-bench

**This benchmark tests the decision layer** — TypeSafe calls the models System
One; around ten open replicas now exist, and a growing number of products are
built on top of them. They are small typed models that answer a classification
question directly: you hand one the options, it returns one of them plus a
confidence, in place of an LLM call inside a pipeline.

A deployed decision layer is four things: what state gets assembled, what
question gets asked, where the threshold sits, and the model underneath. This
benchmark measures both ends of that.

The pitch for the category is threefold: nearly as accurate as the LLM you
removed, far cheaper, and sure enough of itself that you can threshold on its
confidence and escalate the rest to a bigger model. This benchmark takes that
pitch apart into things that can be measured, and measures them on real
decisions.

**Model boards** put the replicas against each other and against the LLM calls
they are meant to replace — the LLMs are reference rows there, not the subject.

**Product boards** hold the model fixed and vary everything else. Thirteen
tool-call permission gates ship on the same model; what separates them is the
other three parts. There the model is the reference row and the shipped product
is the subject — the model board's shape, inverted.

## What the model boards measure

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

## What the product boards measure

**Whether the shipped thing does what the model can.** Same three columns are
beside the point here: a permission gate that refuses everything is cheap and
certain and useless. What matters is the pair — what it stops, and what it
interrupts — reported per class, because a constant strategy is perfect on one
row and hopeless on the others and a single number hides that.

**And where the gap lives.** Products on one model land in very different
places, so the difference is not the model. On `tool_call_scope` the model,
asked about scope directly, separates in-scope from out-of-scope well above
anything a shortcut reaches — while both shipped gates measured so far are
constants, one allowing everything and one refusing almost everything. That is
a finding about question sets and thresholds, and it is a fix rather than a
verdict.

## Tasks

| task | the decision | options | n |
|---|---|---|---|
| [`cve_weakness_class`](tasks/cve_weakness_class) | a published vulnerability description → the weakness class behind it | 30 | 1,500 |
| [`tool_call_scope`](tasks/tool_call_scope) | a session and a pending command → allow it, hand it back, or stop it | 3 | 84 |

The suite grows by adding decisions of a different shape, not by adding more of
the same material. `tool_call_scope` is a different shape twice over: there is
no option list to hand over, and the answer is a relation between two sets read
out of a listing rather than a label attached to a description. It is also the
first task a shipped product can sit as well as a model.

## Running one

Each task directory holds `inputs/task.md` with the instructions — and the
option list, where there is one — and one directory per case. Answers are not in this repository. Scores go
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

On `tool_call_scope` the floor is a pair rather than a number, and reading it on
the wrong scale is its own trap: a rule that stops any command touching a row
the user does not own looks weak as an accuracy and reads as a competent gate as
a catch rate at zero false refusals. The case set now includes in-scope calls
where the user authorises a colleague's resource out loud, which is what that
rule gets wrong, and nothing trivial catches anything at a false refusal of zero
any more.

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
`tool_call_scope` adapts its scope axis from AmPermBench (CC BY-NC-SA) as
method only, and builds its own cases; no data of theirs is redistributed.
The vulnerability records in `cve_weakness_class` come from NIST's National
Vulnerability Database, which places its data in the public domain, and the
weakness classes from MITRE's CWE™, released for free public use. Each task's
README carries its own acknowledgements; neither NIST nor MITRE endorses this
benchmark.
