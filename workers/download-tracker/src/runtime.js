/**
 * DecisionGATE hosted runtime (port of decisiongate/gates.py + engine).
 * Sequential PASS/REVISE/BLOCK. wrap / remote command execution is NOT hosted.
 * /v1 calls never touch DOWNLOADS KV.
 */
const PRODUCT = "decisiongate";
const VERSION = "0.1.0";
const MOTTO = "Freedom without clarity is chaos. Clarity without force is wisdom.";
const HOST = "https://decisiongate-download-tracker.vibelock.workers.dev";
const SKILL = "---\nname: DecisionGATE\ndescription: Use when a proposed action should pass structured ethical gates before execution. Hosted wrap never runs commands. Hosted /v1 via this Worker or aziel-runtime. Author Aziel Eliab.\n---\n\n# DecisionGATE\n\nFreedom without clarity is chaos. Clarity without force is wisdom.\n\nAuthor: **Aziel Eliab**.\n\nUse when a proposed action should pass structured ethical gates before execution. Hosted wrap never runs commands.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Endpoints (this Worker)\n\nHost: `https://decisiongate-download-tracker.vibelock.workers.dev`\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| POST | `/v1/check` | Run five gates on a proposal. |\n| POST | `/v1/evaluate` | Alias of /v1/check. |\n\nOpenAPI: `https://decisiongate-download-tracker.vibelock.workers.dev/openapi.json`\n\nCatalog OpenAPI: `https://aziel-runtime.vibelock.workers.dev/openapi.json`\n\nMCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n\nCatalog aliases under `/p/decisiongate/\u2026`.\n\n## How to call (Mozilla/5.0)\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' -X POST https://decisiongate-download-tracker.vibelock.workers.dev/v1/check \\\n  -H 'content-type: application/json' \\\n  -d '{\"action\":\"publish a receipt\",\"evidence\":\"hashed log\",\"impact\":\"local only\",\"integrity\":\"append-only\",\"responsible\":\"Aziel Eliab\"}'\ncurl -s -A 'Mozilla/5.0' https://decisiongate-download-tracker.vibelock.workers.dev/v1/skill\n```\n\nGrok: import the catalog OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://decisiongate-download-tracker.vibelock.workers.dev/install.sh | bash\ndecisiongate ui\n```\n\nThen open http://127.0.0.1:8791 (this computer only).\n\n## Honest banner\n\nTHIS IS: an ethical pre-execution filter (PASS / REVISE / BLOCK). THIS IS NOT: predictive, advisory-as-command, or a hosted command runner. wrap is not hosted. Author Aziel Eliab.\n\nDOI: https://doi.org/10.5281/zenodo.21435730  \nRecord: https://zenodo.org/records/21435730\n\nApache-2.0 (or the repo LICENSE). Forks are welcome and always allowed.\n";


const PASS = "PASS";
const REVISE = "REVISE";
const BLOCK = "BLOCK";
const HEDGES = new Set(["maybe", "somehow", "stuff", "things"]);
const COMMON_VERBS = new Set([
  "is","are","was","were","be","been","being","am","have","has","had","do","does","did",
  "will","would","shall","should","can","could","must","need","needs","make","makes","made",
  "take","takes","took","give","gives","gave","go","goes","went","come","keep","put","use",
  "uses","used","set","get","let","allow","allows","publish","release","releases","deploy",
  "ship","open","close","create","created","delete","write","read","run","execute","adopt",
  "reject","approve","block","collect","store","share","send","build","launch","hire","spend",
  "buy","sell","migrate","replace","update","install","announce","commit","sign","fund",
  "grant","revoke","host","serve","bind","filter","record","name","assign","document",
  "provide","provides","include","includes","add","remove","stop","start","move","change",
  "apply","submit","accept","refuse","pay","offer","request","require","requires",
  "implement","implements",
]);
const NEGATION_MARKERS = [
  "do not ","don't ","does not ","doesn't ","must not ","cannot ","can't ",
  "never ","no ","not ","without ",
];
const GATE_ORDER = ["Definition","Evidence","Impact","Integrity","Responsibility"];
const WORD_RE = /[A-Za-z0-9][A-Za-z0-9._+-]*/g;

export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function asStr(v) {
  return v == null ? "" : String(v);
}

function asList(value) {
  if (value == null) return [];
  if (typeof value === "string") {
    let parts = value.replace(/\r\n/g, "\n").split("\n").map((p) => p.trim());
    if (parts.length === 1 && parts[0].includes(";")) {
      parts = parts[0].split(";").map((p) => p.trim());
    }
    return parts.filter(Boolean);
  }
  if (Array.isArray(value)) {
    return value.map((item) => asStr(item).trim()).filter(Boolean);
  }
  const text = asStr(value).trim();
  return text ? [text] : [];
}

function proposalFromBody(raw) {
  const data = raw && typeof raw === "object" ? raw : {};
  return {
    statement: asStr(data.statement).trim(),
    evidence: asList(data.evidence),
    impacts_positive: asList(data.impacts_positive ?? data.impact_pos),
    impacts_negative: asList(data.impacts_negative ?? data.impact_neg),
    values: asList(data.values),
    commitments: asList(data.commitments),
    constraints: asList(data.constraints),
    accountable_person: asStr(data.accountable_person ?? data.accountable).trim(),
  };
}

function tokenize(text) {
  if (!text) return [];
  const m = text.toLowerCase().match(WORD_RE);
  return m || [];
}

function looksLikeVerb(token) {
  if (COMMON_VERBS.has(token)) return true;
  if (token.length > 4 && (token.endsWith("ing") || token.endsWith("ize") || token.endsWith("ise") || token.endsWith("ify"))) return true;
  if (token.length > 4 && token.endsWith("ed")) return true;
  return false;
}

function hasVerbAndObject(tokens) {
  const content = tokens.filter((t) => !HEDGES.has(t));
  if (content.length < 2) return false;
  return content.some(looksLikeVerb);
}

function gateResult(name, state, feedback, extra = {}) {
  const out = { name, state, feedback };
  if (extra.overridden) {
    out.overridden = true;
    if (extra.automatic_state) out.automatic_state = extra.automatic_state;
    if (extra.override_note) out.override_note = extra.override_note;
  }
  return out;
}

function gateDefinition(p) {
  const statement = p.statement.trim();
  if (!statement) {
    return gateResult("Definition", BLOCK, "Statement is empty. A proposal with no concrete statement cannot pass Definition. Write an unambiguous action with a verb and an object, at least 12 words.");
  }
  const tokens = tokenize(statement);
  if (tokens.length < 12) {
    return gateResult("Definition", REVISE, `Statement has ${tokens.length} word(s); Definition requires at least 12. Expand into a concrete, unambiguous proposal (who does what, to what, under what bound).`);
  }
  if (!hasVerbAndObject(tokens)) {
    return gateResult("Definition", REVISE, "Statement is hedge-only or lacks a verb+object after removing maybe/somehow/stuff/things. Name a specific action and its object.");
  }
  return gateResult("Definition", PASS, "Statement is concrete enough to scrutinize (length, verb+object).");
}

function gateEvidence(p) {
  const items = p.evidence.filter((e) => e.trim());
  if (!items.length) {
    return gateResult("Evidence", REVISE, "Evidence list is empty. Identify at least one fact, datum, or observation that grounds the statement. Ungrounded assertions do not pass Evidence.");
  }
  return gateResult("Evidence", PASS, `${items.length} evidence item(s) identified.`);
}

function gateImpact(p) {
  const pos = p.impacts_positive.filter((i) => i.trim());
  const neg = p.impacts_negative.filter((i) => i.trim());
  const missing = [];
  if (!pos.length) missing.push("positive");
  if (!neg.length) missing.push("negative");
  if (missing.length) {
    return gateResult("Impact", REVISE, `Impact list(s) empty: ${missing.join(" and ")}. Name who or what is affected on both the positive and the negative side. Hidden impacts do not pass Impact.`);
  }
  return gateResult("Impact", PASS, `${pos.length} positive and ${neg.length} negative impact(s) named.`);
}

function constraintPayload(constraint) {
  let text = constraint.toLowerCase().split(/\s+/).join(" ");
  if (!text) return null;
  let found = false;
  let remainder = ` ${text} `;
  for (const marker of NEGATION_MARKERS) {
    const padded = marker.startsWith(" ") ? marker : ` ${marker}`;
    if (remainder.includes(padded) || remainder.trimStart().startsWith(marker)) {
      found = true;
      remainder = remainder.split(padded).join(" ");
      const stripped = remainder.trimStart();
      if (stripped.startsWith(marker)) {
        remainder = " " + stripped.slice(marker.length);
      }
    }
  }
  const payload = remainder.split(/\s+/).filter(Boolean).join(" ");
  if (found && payload) return payload;
  return null;
}

function statementContradictsConstraint(statement, constraint) {
  const payload = constraintPayload(constraint);
  if (!payload) return false;
  const hay = statement.toLowerCase().split(/\s+/).join(" ");
  return hay.includes(payload);
}

function gateIntegrity(p) {
  const values = p.values.filter((v) => v.trim());
  if (!values.length) {
    return gateResult("Integrity", REVISE, "Values list is empty. Integrity requires stated values so the proposal can be checked against them.");
  }
  const hits = [];
  for (const constraint of p.constraints) {
    if (statementContradictsConstraint(p.statement, constraint)) hits.push(constraint);
  }
  if (hits.length) {
    const shown = hits[0];
    return gateResult("Integrity", BLOCK, `Statement contradicts a provided constraint (${JSON.stringify(shown)}). A contradiction of this kind cannot pass Integrity without changing the proposal's nature.`);
  }
  return gateResult("Integrity", PASS, `${values.length} value(s) stated; no constraint contradiction detected.`);
}

function gateResponsibility(p) {
  const owner = p.accountable_person.trim();
  if (!owner) {
    return gateResult("Responsibility", BLOCK, "Accountable person is blank. Diffuse or absent ownership cannot pass Responsibility. Name one accountable owner.");
  }
  return gateResult("Responsibility", PASS, `Accountable owner named: ${owner}.`);
}

const GATE_FUNCS = [gateDefinition, gateEvidence, gateImpact, gateIntegrity, gateResponsibility];

function coerceOverrides(overrides) {
  const out = {};
  if (!overrides || typeof overrides !== "object") return out;
  const known = Object.fromEntries(GATE_ORDER.map((n) => [n.toLowerCase(), n]));
  for (const [key, raw] of Object.entries(overrides)) {
    const name = known[String(key).trim().toLowerCase()];
    if (!name) continue;
    let note = "";
    let state = REVISE;
    if (typeof raw === "string") note = raw.trim();
    else if (raw && typeof raw === "object") {
      const stateRaw = String(raw.state || REVISE).trim().toUpperCase();
      if (stateRaw === REVISE) state = stateRaw;
      note = String(raw.note || raw.feedback || "").trim();
    }
    out[name] = { state, note };
  }
  return out;
}

function runGates(proposal, overrides) {
  const prop = proposalFromBody(proposal);
  const forced = coerceOverrides(overrides);
  const lineage = [];
  let final_state = PASS;
  let blocked_at = null;
  for (const fn of GATE_FUNCS) {
    let result = fn(prop);
    if (forced[result.name]) {
      const { state, note } = forced[result.name];
      const auto = result.state;
      let feedback = result.feedback;
      feedback = note
        ? `${feedback} Human override to ${state}: ${note}`
        : `${feedback} Human override to ${state} (no note supplied).`;
      result = gateResult(result.name, state, feedback, {
        overridden: true,
        automatic_state: auto,
        override_note: note || undefined,
      });
    }
    lineage.push(result);
    if (result.state !== PASS) {
      final_state = result.state;
      if (result.state === BLOCK) blocked_at = result.name;
      break;
    }
  }
  return {
    lineage,
    final_state,
    blocked_at,
    proposal: prop,
    motto: MOTTO,
    product: PRODUCT,
    version: VERSION,
  };
}

function health() {
  return { ok: true, product: PRODUCT, version: VERSION };
}

function openapiSpec() {
  const proposalProps = {
    statement: { type: "string", description: "Concrete proposal statement (CLI --statement)." },
    evidence: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }], description: "Facts/data (CLI --evidence)." },
    impacts_positive: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }], description: "CLI --impact-pos." },
    impact_pos: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }] },
    impacts_negative: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }], description: "CLI --impact-neg." },
    impact_neg: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }] },
    values: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }] },
    commitments: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }] },
    constraints: { oneOf: [{ type: "string" }, { type: "array", items: { type: "string" } }] },
    accountable_person: { type: "string", description: "CLI --accountable." },
    accountable: { type: "string" },
    overrides: { type: "object", additionalProperties: true, description: "Optional human override to REVISE with a note." },
  };
  const report = {
    type: "object",
    properties: {
      product: { type: "string" },
      version: { type: "string" },
      motto: { type: "string" },
      final_state: { type: "string", enum: ["PASS", "REVISE", "BLOCK"] },
      blocked_at: { type: ["string", "null"] },
      lineage: {
        type: "array",
        items: {
          type: "object",
          properties: {
            name: { type: "string" },
            state: { type: "string", enum: ["PASS", "REVISE", "BLOCK"] },
            feedback: { type: "string" },
          },
        },
      },
      proposal: { type: "object" },
    },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "DecisionGATE runtime",
      version: VERSION,
      description: "Ethical pre-execution filter. Sequential PASS/REVISE/BLOCK. wrap (shell exec) is not hosted. " + MOTTO,
    },
    servers: [{ url: HOST }],
    paths: {
      
      "/v1/skill": {
        get: {
          operationId: "decisiongate_skill",
          summary: "Return skill markdown. Does not increment download KV.",
          responses: { "200": { description: "markdown" } },
        },
      },
"/v1/health": {
        get: {
          operationId: "health",
          summary: "Liveness",
          responses: { "200": { description: "ok", content: { "application/json": { schema: { type: "object" } } } } },
        },
      },
      "/v1/check": {
        post: {
          operationId: "check",
          summary: "Run the five gates (CLI check).",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: proposalProps } } } },
          responses: { "200": { description: "Gate report", content: { "application/json": { schema: report } } } },
        },
      },
      "/v1/evaluate": {
        post: {
          operationId: "evaluate",
          summary: "Same sequential gates as check; returns PASS/REVISE/BLOCK + motto.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: proposalProps } } } },
          responses: { "200": { description: "Gate report", content: { "application/json": { schema: report } } } },
        },
      },
    },
  };
}

function aiHtml() {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DecisionGATE — use with Grok, ChatGPT, Venice</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  code, pre { background: #151922; padding: .15rem .4rem; border-radius: 4px; }
  a { color: #c9d4ff; }
  .motto { color: #9aa3b2; font-style: italic; }
</style>
<body>
  <h1>DecisionGATE live API</h1>
  <p class="motto">${MOTTO}</p>
  <p>This Worker is a sequential five-gate filter. It does <strong>not</strong> run commands. There is no hosted <code>wrap</code>.</p>
  <h2>ChatGPT (GPT Actions)</h2>
  <p>Paste this OpenAPI URL into GPT Actions:</p>
  <p><code>${HOST}/openapi.json</code></p>
  <h2>Grok / xAI</h2>
  <p>Add a custom tool pointing at <code>POST ${HOST}/v1/check</code> and <code>POST ${HOST}/v1/evaluate</code>. Import the OpenAPI document if the client accepts it.</p>
  <h2>Venice</h2>
  <p>Create a custom HTTP tool from the same OpenAPI URL.</p>
  <h2>MCP catalog</h2>
  <p>The shared catalog (ships separately) is <code>https://aziel-runtime.vibelock.workers.dev/mcp</code>.</p>
  <p><a href="/openapi.json">openapi.json</a> · <a href="/v1/health">health</a> · <a href="/">downloads</a></p>
</body>
</html>`;
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

export async function handleRuntimeApi(request, url) {
  const path = url.pathname;
  const isApi = path === "/v1" || path.startsWith("/v1/") || path === "/openapi.json" || path === "/ai";
  if (!isApi) return null;

  if (path === "/v1/health" && request.method === "GET") return json(health());
  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL, {
      status: 200,
      headers: { "Content-Type": "text/markdown; charset=utf-8", "Cache-Control": "private, no-store", ...corsHeaders() },
    });
  }
  if (path === "/openapi.json" && request.method === "GET") return json(openapiSpec());
  if (path === "/ai" && request.method === "GET") {
    return new Response(aiHtml(), {
      headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
    });
  }
  if ((path === "/v1/check" || path === "/v1/evaluate") && request.method === "POST") {
    const body = await readJson(request);
    if (body == null || typeof body !== "object") return json({ error: "JSON body required" }, 400);
    const report = runGates(body, body.overrides);
    return json(report);
  }
  if (path === "/v1/wrap" || path.startsWith("/v1/wrap")) {
    return json({ error: "wrap is not hosted; this API never executes commands" }, 404);
  }
  return json({ error: "not found" }, 404);
}
