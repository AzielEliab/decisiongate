# Contributing to DecisionGATE

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only (`dataclasses`, `json`, `http.server`,
`argparse`). pytest is the dev extra. No network. No ML.

## Ground rules

1. **This is a filter, not an advisor.** Do not add scoring, ranking,
   recommendations, predictions, or "you should". PASS is clearance that
   the proposal survived scrutiny, not a suggestion to act.
2. **Keep the five gates sequential.** First failure stops the chain.
   Do not evaluate later gates after a failure.
3. **Heuristics stay small, deterministic, and tested.** No models.
4. **Keep the dependency list tiny.** Stdlib only in the core.
5. **UI binds loopback only** (`127.0.0.1`). Do not listen on `0.0.0.0`.
6. **Do not merge this product into ForgeReceipts, ZionPattern Solver,
   or any sibling tree.** DecisionGATE is standalone.
7. **Keep `/download` HTTP 200 gzip** (no 302 to GitHub). Isolated KV `DECISIONGATE_DOWNLOADS`.
8. **Door vs local op.** `/v1/mesh/*` PROXY to aziel-runtime. Local ops are `/v1/{op}` only.
   Suite mesh default OFF; QNM rollup live|locked|isolated; QNS-CD-1.0
   hub cite only (photon QNS1 packet transfer); no Node Gate; no public
   qnsd proxy; no auto-heal; not anonymity.
9. New behavior needs a test that fails without the change.
10. Human override of a gate is to **REVISE** with a note recorded in
   lineage. Do not silently convert BLOCK to PASS.

## Where to change things

- Proposal fields: `decisiongate/proposal.py`
- Gate heuristics: `decisiongate/gates.py`
- Sequential engine / lineage: `decisiongate/engine.py`
- CLI: `decisiongate/cli.py`
- Local UI: `decisiongate/ui.py`, `decisiongate/web/`
- Spec: `docs/whitepaper.md`
- Isolated counter: `workers/download-tracker/`
- Suite mesh / QNM Live Nodes: `workers/download-tracker/src/mesh.js` (`/v1/mesh/*` PROXY to aziel-runtime). QNS-CD-1.0 is a hub cite / Worker mesh cross-map (`QNS_CD_SPEC` + `QNS_CD`); do not implement qnsd or a public proxy here.

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
