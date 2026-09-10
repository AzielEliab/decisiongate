---
name: DecisionGATE
description: Use when calling DecisionGATE hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite (photon QNS1 packet transfer). No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Author Aziel Eliab.
---

# DecisionGATE

A five-gate check before you act. Not a predictor. Not advice. Not a command. Author: **Aziel Eliab**.

**THIS IS:** a lightweight ethical pre-execution filter (PASS / REVISE / BLOCK).

**THIS IS NOT:** a predictor, a court, a truth score, advice, or a hosted command runner. Hosted `/v1` does not increment downloads or views. wrap is not hosted.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- `GET /v1/mesh` — PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map (photon QNS1 packet transfer). Never enables. No public qnsd proxy.
- `GET /v1/mesh/nodes` — PROXY Live Nodes roster (5-minute presence). Payload includes the QNS-CD-1.0 cross-map.
- `POST /v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` — PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path.
- Product POSTs listed in OpenAPI

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the Worker OpenAPI as a custom tool, GPT Action, or HTTP tool.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/mesh
```

## Local (after one-click install)

```bash
curl -fsSL https://decisiongate-download-tracker.vibelock.workers.dev/install.sh | bash
decisiongate ui
decisiongate doctor
```

Then open http://127.0.0.1:8791 (this computer only). Import file and Export file both exist. Verify speaks in plain words.

Counted download (gzip HTTP 200, no 302): https://decisiongate-download-tracker.vibelock.workers.dev/download?asset=decisiongate-0.1.0.tar.gz
GitHub: https://github.com/AzielEliab/decisiongate

Paper: DOI https://doi.org/10.5281/zenodo.21435730 · https://zenodo.org/records/21435730 · Apache-2.0. Forks welcome.

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Five sequential gates on a proposal. Freedom without clarity is chaos.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/decisiongate/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://decisiongate-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `decisiongate doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF). Mesh JSON carries `qns_cd` (QNS-CD-1.0) pointing at [qnm-node](https://github.com/AzielEliab/qnm-node) and [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). Hub cite only — not a Softwares-tab product.

Works with ChatGPT (GPT Actions / OpenAI), Grok (xAI), Venice, Claude (Anthropic), Cursor (MCP), Glama (MCP), Perplexity, Microsoft Copilot / Bing, Google Gemini / Vertex, Mistral, Meta AI, Apple Intelligence surfaces, Amazon Q tooling, DuckAssist, You.com, Cohere, and other MCP/OpenAPI-capable assistants. Import the catalog or Worker OpenAPI as a custom tool, GPT Action, or HTTP tool. MCP clients can use the catalog MCP endpoint.
