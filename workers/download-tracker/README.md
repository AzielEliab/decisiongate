# DecisionGATE download tracker (Cloudflare Worker)

Counts GitHub-release downloads for DecisionGATE across the canonical
repository, other branches, and forks. Forks are identified by GitHub
`owner/repo`.

Homepage is an **isolated counter**: the number is on the download
button. Nobody reports a download. The click is the count.

**Do not deploy wrangler from this tree** until the KV namespace id in
`wrangler.toml` is a real id. It is the placeholder `REPLACE_ME`.

Until deploy,
`https://decisiongate-download-tracker.vibelock.workers.dev` will not
resolve. Send people to
[GitHub Releases](https://github.com/AzielEliab/decisiongate/releases).

No secrets belong in this directory.

Freedom without clarity is chaos. Forks are welcome and always allowed.

This worker is DecisionGATE only. It is not mixed with ForgeReceipts,
ZionPattern Solver, or any other product.

## Bindings

| Binding     | Type | Purpose |
|-------------|------|---------|
| `DOWNLOADS` | KV   | Counters keyed `project|owner|repo|branch|fork` |

## Deploy (later — not from this tree yet)

```bash
cd workers/download-tracker

# 1. Log in once (opens a browser; token stays in wrangler, not in git)
npx wrangler login

# 2. Create the KV namespace. Paste the id into wrangler.toml
#    replacing REPLACE_ME. Binding name MUST stay DOWNLOADS.
npx wrangler kv namespace create DOWNLOADS

# 3. Deploy
npx wrangler deploy
```

The `workers.dev` subdomain wrangler prints
(`decisiongate-download-tracker.<account>.workers.dev`) is enough until
custom DNS is ready. This tree documents the intended public URL
`https://decisiongate-download-tracker.vibelock.workers.dev`.

Do not deploy from this tree until KV is a real id.

## Routes

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Isolated homepage: live count on the download button |
| GET | `/download?repo=&tag=&asset=` | Increment KV, 302 to the GitHub asset (default: releases page) |
| GET | `/stats` | JSON totals plus per-repo and per-branch breakdown |
| POST | `/event` | A fork reports a download |

Query params on `/download`: `owner`, `repo` (`AzielEliab/decisiongate` is
accepted), `branch`, `fork` (`1` or `owner/repo`), `tag`, `asset`.

Default redirect with no asset:

```
https://github.com/AzielEliab/decisiongate/releases
```

Tracked asset URL (after deploy):

```
https://decisiongate-download-tracker.vibelock.workers.dev/download?repo=AzielEliab/decisiongate&tag=latest&asset=decisiongate-0.1.0.tar.gz
```

A fork reports its own download:

```bash
curl -X POST https://decisiongate-download-tracker.vibelock.workers.dev/event \
  -H "content-type: application/json" \
  -d '{
    "owner": "YourFork",
    "repo": "decisiongate",
    "branch": "main",
    "fork": "1",
    "asset": "decisiongate-0.1.0.tar.gz"
  }'
```

`fork=1` or `fork=YourFork/decisiongate`. If `owner/repo` is not
`AzielEliab/decisiongate`, the worker records `fork=1` automatically.

## Stats

`GET /stats` returns `total`, `by_repo`, `by_branch`, `by_fork`, and a
`breakdown` array so forks can read aggregates.

## CORS

All responses include `Access-Control-Allow-Origin: *`.
