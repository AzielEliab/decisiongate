/* DecisionGATE UI. No CDN. Filter, do not advise. Simple by default. */
(function () {
  const form = document.getElementById("proposal-form");
  const banner = document.getElementById("banner");
  const exportBtn = document.getElementById("export");
  const importBtn = document.getElementById("import");
  const importEl = document.getElementById("import-json");
  const verifyBtn = document.getElementById("verify");
  const kid = document.getElementById("kid-plain");
  const rowsPre = document.getElementById("rows-pre");
  const viewSimple = document.getElementById("view-simple");
  const viewAdvanced = document.getElementById("view-advanced");
  const advancedPanel = document.getElementById("advanced-panel");
  const names = ["Definition", "Evidence", "Impact", "Integrity", "Responsibility"];
  let lastReport = null;
  let advanced = false;
  document.body.classList.add("simple");

  function setView(next) {
    advanced = next;
    document.body.classList.toggle("simple", !advanced);
    viewSimple.classList.toggle("on", !advanced);
    viewAdvanced.classList.toggle("on", advanced);
    viewSimple.setAttribute("aria-pressed", String(!advanced));
    viewAdvanced.setAttribute("aria-pressed", String(advanced));
    if (advancedPanel) advancedPanel.hidden = !advanced;
  }

  function lines(id) {
    const el = document.getElementById(id);
    if (!el) return [];
    return el.value.split(/\n|;/).map(function (s) { return s.trim(); }).filter(Boolean);
  }

  function proposalFromForm() {
    return {
      statement: document.getElementById("statement").value,
      evidence: lines("evidence"),
      impacts_positive: lines("impacts_positive"),
      impacts_negative: lines("impacts_negative"),
      values: lines("values"),
      commitments: lines("commitments"),
      constraints: lines("constraints"),
      accountable_person: document.getElementById("accountable").value
    };
  }

  function overrides() {
    const out = {};
    names.forEach(function (name) {
      const box = document.querySelector('input[data-override="' + name + '"]');
      const note = document.querySelector('input[data-note="' + name + '"]');
      if (box && box.checked) {
        out[name] = { state: "REVISE", note: note ? note.value.trim() : "" };
      }
    });
    return out;
  }

  document.querySelectorAll("input[data-override]").forEach(function (box) {
    box.addEventListener("change", function () {
      const name = box.getAttribute("data-override");
      const note = document.querySelector('input[data-note="' + name + '"]');
      if (note) note.disabled = !box.checked;
    });
  });

  function paint(report) {
    lastReport = report;
    const ran = {};
    (report.lineage || []).forEach(function (g) { ran[g.name] = g; });
    names.forEach(function (name) {
      const li = document.querySelector('.gate[data-gate="' + name + '"]');
      if (!li) return;
      li.classList.remove("PASS", "REVISE", "BLOCK", "pending", "skipped");
      const result = ran[name];
      const stateEl = li.querySelector(".state");
      const feedbackEl = li.querySelector(".feedback");
      if (!result) {
        li.classList.add("skipped");
        stateEl.textContent = "not reached";
        feedbackEl.textContent = "Stopped before this gate. First failure ends the chain.";
        return;
      }
      li.classList.add(result.state);
      stateEl.textContent = result.state + (result.overridden ? " (override)" : "");
      feedbackEl.textContent = result.feedback || "";
    });
    const final = report.final_state || "REVISE";
    banner.className = "banner " + final;
    let text = "Final: " + final;
    let kidText = "Tap Run after you type a plan.";
    if (final === "PASS") {
      text = "PASS — all five gates survived scrutiny. This is not advice to proceed; it is clearance that the proposal was inspectable.";
      kidText = "All five lights said yes. That is not 'go do it.' It only means the plan was clear enough to inspect.";
    } else if (final === "REVISE") {
      text = "REVISE — first failure needs a more specific proposal. Feedback is on the lit gate.";
      kidText = "Stop. Make the plan clearer. Read the yellow light.";
    } else if (final === "BLOCK") {
      text = "BLOCK at " + (report.blocked_at || "a gate") + " — cannot be remedied without changing the proposal's nature.";
      kidText = "Stop. This plan cannot pass unless you change what it is.";
    }
    banner.textContent = text;
    if (kid) kid.textContent = kidText;
    if (rowsPre) rowsPre.textContent = JSON.stringify(report, null, 2);
  }

  viewSimple.addEventListener("click", function () { setView(false); });
  viewAdvanced.addEventListener("click", function () { setView(true); });

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    const body = proposalFromForm();
    body.overrides = overrides();
    fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
      .then(function (r) { return r.json(); })
      .then(paint)
      .catch(function (err) {
        banner.className = "banner BLOCK";
        banner.textContent = "Request failed: " + err;
        if (kid) kid.textContent = "The check could not run. This is not advice.";
      });
  });

  function downloadJson(obj, name) {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  exportBtn.addEventListener("click", function () {
    const doc = lastReport
      ? Object.assign({
          product: "DecisionGATE",
          author: "Aziel Eliab",
          version: "0.1.0"
        }, lastReport)
      : {
          product: "DecisionGATE",
          author: "Aziel Eliab",
          version: "0.1.0",
          proposal: proposalFromForm()
        };
    if (!doc.proposal) doc.proposal = proposalFromForm();
    downloadJson(doc, "decisiongate.json");
    if (kid) kid.textContent = "Saved a JSON file. Import file loads it back. This is not advice.";
  });

  importBtn.addEventListener("click", function () {
    importEl.click();
  });

  importEl.addEventListener("change", function () {
    const f = importEl.files && importEl.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = function () {
      let obj;
      try { obj = JSON.parse(String(reader.result || "{}")); } catch (e) {
        banner.className = "banner BLOCK";
        banner.textContent = "That file is not JSON.";
        if (kid) kid.textContent = "Import needs a JSON file. Export file makes one.";
        return;
      }
      const p = obj.proposal || obj.payload || obj;
      function set(id, v) {
        const el = document.getElementById(id);
        if (el && v != null) el.value = Array.isArray(v) ? v.join("\n") : String(v);
      }
      set("statement", p.statement);
      set("evidence", p.evidence);
      set("impacts_positive", p.impacts_positive || p.impact_pos);
      set("impacts_negative", p.impacts_negative || p.impact_neg);
      set("values", p.values);
      set("commitments", p.commitments);
      set("constraints", p.constraints);
      set("accountable", p.accountable_person || p.accountable);
      if (obj.lineage || obj.final_state) paint(obj);
      else if (kid) kid.textContent = "Loaded the file into the form. Tap Run to check it.";
    };
    reader.readAsText(f);
    importEl.value = "";
  });

  verifyBtn.addEventListener("click", function () {
    fetch("/api/verify")
      .then(function (r) { return r.json(); })
      .then(function (doc) {
        const lines = (doc.plain || []).join(" ");
        banner.className = "banner " + (doc.ok ? "PASS" : "BLOCK");
        banner.textContent = doc.summary || lines;
        if (kid) kid.textContent = lines || "Verify finished.";
        if (rowsPre) rowsPre.textContent = JSON.stringify(doc, null, 2);
      })
      .catch(function (err) {
        banner.className = "banner BLOCK";
        banner.textContent = "Verify failed: " + err;
      });
  });
})();
