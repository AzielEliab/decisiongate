---
name: DecisionGATE
description: Use when calling DecisionGATE hosted /v1 or installing the local package. Author Aziel Eliab.
---

# DecisionGATE

A lightweight ethical pre-execution filter. Advisory, not predictive. Author: **Aziel Eliab**.

**THIS IS:** a lightweight ethical pre-execution filter.

**THIS IS NOT:** a predictor, a court, or a truth score. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill
```

## Local (after one-click install)

```bash
curl -fsSL https://decisiongate-download-tracker.vibelock.workers.dev/install.sh | bash
decisiongate ui
decisiongate doctor
```

Then open http://127.0.0.1:8791 (loopback only).

Counted download (gzip HTTP 200, no 302): https://decisiongate-download-tracker.vibelock.workers.dev/download?asset=decisiongate-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/decisiongate

Paper: DOI https://doi.org/10.5281/zenodo.21435730 · https://zenodo.org/records/21435730 · Apache-2.0. Forks welcome.
