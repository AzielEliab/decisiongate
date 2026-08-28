# DecisionGATE

**A Lightweight Ethical Filtering System**

Aziel Eliab
July 2026
License: Apache-2.0

> Freedom without clarity is chaos. Clarity without force is wisdom.

---

## Abstract

DecisionGATE is a software-only **pre-execution filter**. It is not
predictive, not advisory, and not prescriptive. It does not tell anyone
what to do. It asks whether a proposed action has survived structured
scrutiny.

The core claim is narrow:

**No action should pass unless it survives structured scrutiny.**

A proposal is presented to five sequential gates — Definition, Evidence,
Impact, Integrity, Responsibility. Each gate returns PASS, REVISE, or
BLOCK. REVISE includes specific feedback. BLOCK cannot be remedied
without changing the proposal's nature. The proposal must PASS all five
**in order**. The first failure stops the chain.

This document is the specification implemented by the `decisiongate`
Python package, version 0.1.0. Forks are welcome and always allowed.

This product is standalone. It is not ForgeReceipts. It is not
ZionPattern Solver. It is not merged into those trees.

---

## 1. Purpose

Freedom without a clear statement of what will be done is chaos: people
act on shifting language and discover the cost after the fact. Clarity
imposed as a command is not wisdom either. DecisionGATE holds the
middle: **clarity without force**.

The filter sits *before* execution. It does not forecast outcomes. It
does not rank options. It does not recommend a path. It inspects one
proposal and reports whether that proposal is inspectable and owned.

---

## 2. What this is not

DecisionGATE is not:

- a predictor
- an advisor
- a prescriber
- a scorer or ranker
- a model that learns from outcomes
- a policy engine that executes anything
- ForgeReceipts
- ZionPattern Solver

A fork that adds "you should", confidence, or a recommended alternative
has left this spec.

---

## 3. Philosophy

**Freedom without clarity is chaos.**

A proposal that cannot be stated in concrete language cannot be owned.
Vague and shifting statements hide the action until it is too late to
refuse it.

**Clarity without force is wisdom.**

Naming the action, the evidence, the impacts, the values, and the owner
is not the same as compelling the action. The filter refuses to pass
what it cannot see. It does not push what it can see.

---

## 4. The five gates

Gates run in this order. Later gates are not evaluated once an earlier
gate has failed.

### 4.1 Definition

The statement must be a concrete, unambiguous proposal: an action with
an object, long enough to pin down *what* is being done.

- Empty statement → BLOCK (there is no proposal to scrutinize).
- Fewer than 12 words → REVISE.
- Only hedges (`maybe`, `somehow`, `stuff`, `things`) without a
  verb+object → REVISE.
- Vague or shifting language that cannot be held still → REVISE or BLOCK.

### 4.2 Evidence

Facts, data, or observations must be identified. An ungrounded assertion
does not pass.

- Empty evidence list → REVISE.

### 4.3 Impact

Who or what is affected must be named on **both** sides: positive and
negative. Hidden impacts do not pass.

- Either list empty → REVISE.

### 4.4 Integrity

The proposal must be consistent with stated values, prior commitments,
and constraints.

- Empty values → REVISE.
- Statement clearly contradicts a provided constraint (simple substring
  / negation check, e.g. constraint "do not X" while the statement
  contains X) → BLOCK.
- Other contradictions → REVISE or BLOCK.

### 4.5 Responsibility

A named accountable owner. Diffuse or absent ownership cannot pass.

- Blank `accountable_person` → BLOCK.

---

## 5. States

| State | Meaning |
|-------|---------|
| PASS | This gate's requirement is met. The chain continues. |
| REVISE | Specific feedback is attached. The author can change the *wording or completeness* of the same proposal. Chain stops. |
| BLOCK | Cannot be remedied without changing the proposal's **nature**. Chain stops. `blocked_at` records the gate. |

A proposal that PASSes all five has survived scrutiny. That is not
advice to execute it.

---

## 6. Lineage

The engine returns a `Report`:

- `lineage` — the gates that actually ran, each a `GateResult(name, state, feedback)`
- `final_state` — PASS, or the first failure's state
- `blocked_at` — gate name when `final_state` is BLOCK, otherwise omitted / null

The local UI may let a human **override a gate to REVISE** with a note.
The override is recorded in lineage (`overridden`, `automatic_state`,
`override_note`). The default engine is automatic. Override does not
convert BLOCK into PASS.

---

## 7. Heuristics

v0.1 heuristics are deterministic, documented in `decisiongate/gates.py`,
and covered by tests. There is no ML. Rules stay small. A human can
still force REVISE in the UI.

Word tokens are alphanumeric sequences. Verb+object is a closed verb
list plus simple suffixes (`ing`, `ed`, `ize`, `ise`, `ify`) plus at
least one other non-hedge token. Constraint contradiction is a
substring check after stripping a small set of negation markers
(`do not`, `don't`, `never`, `must not`, `cannot`, `no`, `not`,
`without`).

These rules are the floor of scrutiny, not a moral oracle.

---

## 8. Interface

Library package `decisiongate`:

- `decisiongate.proposal.Proposal` — `statement`, `evidence` (list of
  str), `impacts_positive`, `impacts_negative`, `values`,
  `commitments`, `constraints`, `accountable_person`
- `decisiongate.gates` — five functions returning `GateResult`
- `decisiongate.engine.DecisionGATE.run(proposal) -> Report`

CLI:

```
decisiongate version
decisiongate check --statement "..." --evidence "..." --impact-pos "..." --impact-neg "..." --values "..." --accountable "Name"
decisiongate ui   # 127.0.0.1:8791
```

UI binds 127.0.0.1 only. Self-contained CSS. No CDN. Motto on the page.
Five gates as a vertical stack: PASS green, REVISE amber, BLOCK red.
Final banner. Export JSON lineage.

Runtime is stdlib only.

---

## 9. Isolation

DecisionGATE is one product. Download counting, if deployed, uses an
isolated worker (`decisiongate-download-tracker`, project
`decisiongate`). Counts are not mixed with any other product. The
homepage shows the number on the download button. Nobody reports a
download; the click is the count.

Until a real KV namespace id replaces `REPLACE_ME`, that worker stays
undeployed.

---

## 10. License

Apache-2.0. Copyright 2026 Aziel Eliab.

Forks are welcome and always allowed.
