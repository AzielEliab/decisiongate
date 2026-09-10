# decisiongate download tracker

Isolated Worker `decisiongate-download-tracker`. Project `decisiongate`.
KV namespace `DECISIONGATE_DOWNLOADS` bound as `DOWNLOADS`.
Does **not** 302 to GitHub on `/download`. Serves gzip via `ASSETS.fetch`,
`Cache-Control: private, no-store`.

GET `/` increments a **page-view** counter (separate from downloads).
GET `/download` increments **downloads**.
GET `/count` returns `{project, views, downloads, total}` and does not increment.
`/v1` never increments DOWNLOADS KV.
GET `/install.sh` one-click install (does not increment; script curls `/download`).
GET `/v1/skill` returns skill markdown (`text/markdown`). Does not increment views or downloads.
`/v1/mesh/*` PROXY to aziel-runtime suite mesh (`AZIEL_RUNTIME` / `https://aziel-runtime.vibelock.workers.dev`). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 hub cite / Worker mesh cross-map (photon QNS1 packet transfer). Local qnsd is [qnm-node](https://github.com/AzielEliab/qnm-node). Runtime cites + catalog field live in [aziel-runtime](https://github.com/AzielEliab/aziel-runtime). AZInterface has pair custody. Not a Softwares-tab product. No Node Gate. No public qnsd proxy. No auto-heal. Not anonymity. Human UI Live Nodes strip polls `GET /v1/mesh`. Status / Live Nodes JSON includes `qns_cd` / `qns_cd_spec`.

Verify: `curl -sS -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/mesh/status` returns MESH-OK style JSON with `enabled: false` by default.

Host: https://decisiongate-download-tracker.vibelock.workers.dev
