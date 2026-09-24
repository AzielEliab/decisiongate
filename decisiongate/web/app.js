/* DecisionGATE local screen. No CDN. */
(function () {
  const form = document.getElementById("proposal-form");
  const banner = document.getElementById("banner");
  const exportBtn = document.getElementById("export");
  const importBtn = document.getElementById("import");
  const importEl = document.getElementById("import-json");
  const verifyBtn = document.getElementById("verify");
  const kid = document.getElementById("kid-plain");
  const rowsPre = document.getElementById("rows-pre");
  const advanced = document.getElementById("advanced");
  const names = ["Definition", "Evidence", "Impact", "Integrity", "Responsibility"];
  let lastReport = null;

  function syncAdvanced() {
    document.body.classList.toggle("show-advanced", !!(advanced && advanced.open));
  }
  if (advanced) {
    advanced.addEventListener("toggle", syncAdvanced);
    syncAdvanced();
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
        feedbackEl.textContent = "Stopped before this gate. The first one that does not pass ends the chain.";
        return;
      }
      li.classList.add(result.state);
      stateEl.textContent = result.state + (result.overridden ? " (override)" : "");
      feedbackEl.textContent = result.feedback || "";
    });
    const final = report.final_state || "REVISE";
    banner.className = "banner " + final;
    let text = "Final: " + final;
    let kidText = "Run the check after you fill in the plan.";
    if (final === "PASS") {
      text = "PASS. All five gates were clear enough to inspect.";
      kidText = "You can export this result from Advanced.";
    } else if (final === "REVISE") {
      text = "REVISE. The highlighted gate needs a more specific plan. Update it, then run the check again.";
      kidText = "Read the amber gate, change that part, and run the check again.";
    } else if (final === "BLOCK") {
      text = "BLOCK at " + (report.blocked_at || "a gate") + ". Change the plan, then run the check again.";
      kidText = "The red gate stopped the chain. Change that part, then run the check again.";
    }
    banner.textContent = text;
    if (kid) kid.textContent = kidText;
    if (rowsPre) rowsPre.textContent = JSON.stringify(report, null, 2);
  }

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
      .catch(function () {
        banner.className = "banner BLOCK";
        banner.textContent = "The check did not run. Try again, or run decisiongate doctor in a terminal.";
        if (kid) kid.textContent = "If this keeps happening, run decisiongate doctor.";
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
    if (kid) kid.textContent = "Saved a JSON file. Import file in Advanced loads it back.";
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
        banner.textContent = "That file is not JSON. Export a file from Advanced, then import that file.";
        if (kid) kid.textContent = "Import file needs a JSON file.";
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
      if (obj.lineage || obj.final_state) {
        paint(obj);
      } else {
        banner.className = "banner idle";
        banner.textContent = "Loaded " + f.name + ". Run the check when you are ready.";
        if (kid) kid.textContent = "Loaded the file into the form. Run the check when you are ready.";
      }
    };
    reader.readAsText(f);
    importEl.value = "";
  });

  verifyBtn.addEventListener("click", function () {
    fetch("/api/verify")
      .then(function (r) { return r.json(); })
      .then(function (doc) {
        const linesOut = (doc.plain || []).join(" ");
        banner.className = "banner " + (doc.ok ? "PASS" : "BLOCK");
        banner.textContent = doc.summary || linesOut;
        if (kid) kid.textContent = linesOut || "Verify finished.";
        if (rowsPre) rowsPre.textContent = JSON.stringify(doc, null, 2);
      })
      .catch(function () {
        banner.className = "banner BLOCK";
        banner.textContent = "Verify did not finish. Try decisiongate doctor in a terminal.";
      });
  });
})();
