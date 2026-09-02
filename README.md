# DecisionGATE

A five-gate check before you act. Not a predictor. Not advice. Not a command.

**Author:** Aziel Eliab
**Date:** July 2026
**License:** [Apache-2.0](LICENSE)
**DOI:** [10.5281/zenodo.21435730](https://doi.org/10.5281/zenodo.21435730)

> Freedom without clarity is chaos. Clarity without force is wisdom.

**Forks are welcome and always allowed.**

## Honest scope

**THIS IS:** a local five-step filter (Definition, Evidence, Impact, Integrity, Responsibility). Each step is PASS, REVISE, or BLOCK. The first fail stops the chain.

**THIS IS NOT:** a predictor, a court, a truth score, advice, or a remote command runner. Hosted `wrap` is not offered. PASS means the plan was inspectable — not "you should do it."

This tree is a standalone product. It is not ForgeReceipts. It is not ZionPattern Solver.

## Three steps

1. Tap **Download** on the Worker page (or paste the one-click install line).
2. Run `decisiongate ui` and open http://127.0.0.1:8791 on this computer.
3. Type a plan. Tap **Run**. Green means it survived the five checks. That is not "go do it."

Self-check in plain words: `decisiongate doctor` (same as `decisiongate verify`).

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

## Quick start (from a clone)

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
decisiongate ui
```

Open http://127.0.0.1:8791 (loopback only). No CDN, no telemetry.

## CLI

```bash
decisiongate version
decisiongate check --statement "..." --evidence "..." --impact-pos "..." --impact-neg "..." --values "..." --accountable "Name"
decisiongate wrap --statement "..." --evidence "..." --impact-pos "..." --impact-neg "..." --values "..." --accountable "Name" -- -- CMD
decisiongate ui
decisiongate doctor
decisiongate verify
decisiongate import FILE.json
decisiongate export FILE.json
```

`check --json` prints lineage, `final_state`, and optional `blocked_at`.
`wrap` runs `CMD` only if all five gates PASS (no shell).
Import and export both write/read JSON files. Doctor/verify speak in plain words.

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

`decisiongate ui` binds **127.0.0.1:8791** only.

Simple: type a plan, **Run**, **Import file**, **Export file**, **Verify**.
Advanced (tucked away): extra fields, override to REVISE, JSON dump.
Five lights: PASS (green) / REVISE (amber) / BLOCK (red). Self-contained CSS, no CDN.

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. No network. Stdlib runtime. pytest is the dev extra.

## Heuristics (v0.1)

Documented in `decisiongate/gates.py`. Kept small and tested. Not ML.

- **Definition** fails if the statement is empty (BLOCK), shorter than 12 words (REVISE), or contains only the hedges `maybe`, `somehow`, `stuff`, `things` without a verb+object (REVISE).
- **Evidence** fails if the evidence list is empty (REVISE).
- **Impact** fails if either the positive or the negative list is empty (REVISE).
- **Integrity** fails if values are empty (REVISE) or the statement clearly contradicts a provided constraint via a simple substring/negation check (BLOCK).
- **Responsibility** fails if `accountable_person` is blank (BLOCK).

## Worker

Isolated download counter. Account `ac575a9b822bea2bed97d0ab73aed238`.
See [workers/download-tracker/README.md](workers/download-tracker/README.md).
`/download` is HTTP 200 gzip. No 302 to GitHub.

## Use with Grok, ChatGPT, Venice

- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json

Live HTTPS runtime on the existing download-tracker Worker. `GET /download`, live count, and KV isolation are unchanged. `/v1` calls do **not** increment DOWNLOADS. Hosted API does **not** include `wrap` (no remote command execution).

OpenAPI (paste into ChatGPT GPT Actions; import for Venice custom HTTP; Grok/xAI custom tool):

```
https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json
```

Setup notes: [https://decisiongate-download-tracker.vibelock.workers.dev/ai](https://decisiongate-download-tracker.vibelock.workers.dev/ai)

MCP catalog (ships separately): `https://aziel-runtime.vibelock.workers.dev/mcp`

```bash
curl -sS -A 'Mozilla/5.0' -X POST https://decisiongate-download-tracker.vibelock.workers.dev/v1/check \
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

## iPhone & Android

A local-first Flutter client lives in [`mobile/`](mobile/). Five-gate form, sequential PASS / REVISE / BLOCK, motto on screen.

## Cite this

Aziel Eliab. DecisionGATE. https://github.com/AzielEliab/decisiongate. https://decisiongate-download-tracker.vibelock.workers.dev. https://doi.org/10.5281/zenodo.21435730.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://decisiongate-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://decisiongate-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/decisiongate
- Citation JSON: https://decisiongate-download-tracker.vibelock.workers.dev/cite.json
- DOI: https://doi.org/10.5281/zenodo.21435730

## License

Apache-2.0. See [LICENSE](LICENSE). Spec: [docs/whitepaper.md](docs/whitepaper.md). How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

Forks are welcome and always allowed.
