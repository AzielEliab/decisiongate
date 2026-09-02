# DecisionGATE

A lightweight **ethical pre-execution filter**. Not predictive, advisory, or
prescriptive. No action should pass unless it survives structured scrutiny.

**Author:** Aziel Eliab
**Date:** July 2026
**License:** [Apache-2.0](LICENSE)

> Freedom without clarity is chaos. Clarity without force is wisdom.

See the spec: [docs/whitepaper.md](docs/whitepaper.md).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
decisiongate ui
```


## One-click install

```bash
curl -fsSL https://decisiongate-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `decisiongate ui`.

Or tap **Download** / **One-click install** on the Worker homepage:
https://decisiongate-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

- Homepage: [https://decisiongate-download-tracker.vibelock.workers.dev/](https://decisiongate-download-tracker.vibelock.workers.dev/)
- Direct tarball: [decisiongate-0.1.0.tar.gz](https://decisiongate-download-tracker.vibelock.workers.dev/download?asset=decisiongate-0.1.0.tar.gz)
- One-click install: [https://decisiongate-download-tracker.vibelock.workers.dev/install.sh](https://decisiongate-download-tracker.vibelock.workers.dev/install.sh)
- Skill: [https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill](https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill)
- OpenAPI: [https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json](https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json)
- GitHub: [https://github.com/AzielEliab/decisiongate](https://github.com/AzielEliab/decisiongate)
- Zenodo DOI: [10.5281/zenodo.21435730](https://doi.org/10.5281/zenodo.21435730) · [record](https://zenodo.org/records/21435730)

Isolated counter: Worker `decisiongate-download-tracker`, KV `DECISIONGATE_DOWNLOADS`. `/v1` does not increment downloads.

Open http://127.0.0.1:8791 (loopback only). No CDN, no telemetry.

Counted download: [https://decisiongate-download-tracker.vibelock.workers.dev/](https://decisiongate-download-tracker.vibelock.workers.dev/)

Pre-execution wrap (runs `CMD` only if all five gates PASS):

```bash
decisiongate wrap --statement "..." --evidence "..." --impact-pos "..." --impact-neg "..." --values "..." --accountable "Name" -- -- CMD
```



This tree is a standalone product. It is not ForgeReceipts. It is not
ZionPattern Solver. It is not merged into those trees.

Counted downloads (number on the button, no user reporting):
[https://decisiongate-download-tracker.vibelock.workers.dev/](https://decisiongate-download-tracker.vibelock.workers.dev/)

## iPhone & Android

A local-first Flutter client lives in [`mobile/`](mobile/). Open that
folder in Android Studio or Xcode through Flutter (`flutter create .`
first if `android/` / `ios/` still hold the skeleton READMEs). Five-gate
form, sequential PASS / REVISE / BLOCK, motto on screen.

Counted desktop download: [https://decisiongate-download-tracker.vibelock.workers.dev/](https://decisiongate-download-tracker.vibelock.workers.dev/)

Forks are welcome and always allowed.

---

## What it is

Five sequential gates. A proposal must PASS all five **in order**. The first
failure stops the chain.

| # | Gate | PASS requires | Failure |
|---|------|---------------|---------|
| 1 | Definition | Concrete, unambiguous statement | Vague / shifting → REVISE or BLOCK |
| 2 | Evidence | Facts, data, or observations | Ungrounded assertions → REVISE |
| 3 | Impact | Who/what is affected, positive **and** negative | Hidden impacts → REVISE |
| 4 | Integrity | Consistent with stated values, commitments, constraints | Contradictions → REVISE or BLOCK |
| 5 | Responsibility | Named accountable owner | Diffuse or absent → BLOCK |

Each gate is `PASS`, `REVISE`, or `BLOCK`. REVISE includes specific feedback.
BLOCK cannot be remedied without changing the proposal's nature.

Default engine is automatic (deterministic heuristics, no ML). The local UI
can override a gate to REVISE with a note recorded in lineage.

## Install

Python 3.10+. Stdlib only at runtime.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CLI

```bash
decisiongate version
decisiongate check --statement "..." --evidence "..." --impact-pos "..." --impact-neg "..." --values "..." --accountable "Name"
decisiongate ui   # 127.0.0.1:8791
```

`check --json` prints lineage, `final_state`, and optional `blocked_at`.

## Library

```python
from decisiongate import DecisionGATE, Proposal

report = DecisionGATE().run(Proposal(
    statement="Release DecisionGATE 0.1.0 as a standalone Python package with Apache-2.0 licensing on GitHub this month.",
    evidence=["Whitepaper dated July 2026 names five sequential gates."],
    impacts_positive=["Authors get a named scrutiny path before acting."],
    impacts_negative=["Vague drafts take longer because they must be rewritten."],
    values=["Clarity without force"],
    accountable_person="Aziel Eliab",
))
print(report.final_state)
for gate in report.lineage:
    print(gate.name, gate.state, gate.feedback)
```

## UI

`decisiongate ui` binds **127.0.0.1:8791** only. Form for the proposal fields.
Five gates as a vertical stack lighting PASS (green) / REVISE (amber) / BLOCK
(red) with feedback. Final banner. Export JSON lineage. Self-contained CSS,
no CDN. Motto on the page.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. No network. Stdlib runtime. pytest is the dev extra.

## Heuristics (v0.1)

Documented in `decisiongate/gates.py`. Kept small and tested.

- **Definition** fails if the statement is empty (BLOCK), shorter than 12 words (REVISE), or contains only the hedges `maybe`, `somehow`, `stuff`, `things` without a verb+object (REVISE).
- **Evidence** fails if the evidence list is empty (REVISE).
- **Impact** fails if either the positive or the negative list is empty (REVISE).
- **Integrity** fails if values are empty (REVISE) or the statement clearly contradicts a provided constraint via a simple substring/negation check (BLOCK).
- **Responsibility** fails if `accountable_person` is blank (BLOCK).

## Worker

Isolated download counter, undeployed until a real KV id replaces `REPLACE_ME`.
See [workers/download-tracker/README.md](workers/download-tracker/README.md).
Do not deploy wrangler from this tree until then.

## Use with Grok, ChatGPT, Venice

Live HTTPS runtime on the existing download-tracker Worker. `GET /download`, live count, and KV isolation are unchanged. `/v1` calls do **not** increment DOWNLOADS. Hosted API does **not** include `wrap` (no remote command execution).

OpenAPI (paste into ChatGPT GPT Actions; import for Venice custom HTTP; Grok/xAI custom tool):

```
https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json
```

Setup notes: [https://decisiongate-download-tracker.vibelock.workers.dev/ai](https://decisiongate-download-tracker.vibelock.workers.dev/ai)

MCP catalog (ships separately): `https://aziel-runtime.vibelock.workers.dev/mcp`

```bash
curl -sS -X POST https://decisiongate-download-tracker.vibelock.workers.dev/v1/check \
  -H "content-type: application/json" \
  -d '{
    "statement": "Release DecisionGATE 0.1.0 as a standalone Python package with Apache-2.0 licensing on GitHub this month.",
    "evidence": ["Whitepaper dated July 2026 names five sequential gates."],
    "impact_pos": ["Authors get a named scrutiny path before acting."],
    "impact_neg": ["Vague drafts take longer because they must be rewritten."],
    "values": ["Clarity without force"],
    "accountable": "Aziel Eliab"
  }'
```

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
