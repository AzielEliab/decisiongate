/* DecisionGATE UI. No CDN. Filter, do not advise. */
(function () {
  const form = document.getElementById("proposal-form");
  const banner = document.getElementById("banner");
  const exportBtn = document.getElementById("export");
  const names = ["Definition", "Evidence", "Impact", "Integrity", "Responsibility"];
  let lastReport = null;

  function lines(id) {
    const el = document.getElementById(id);
    if (!el) return [];
    return el.value.split(/\n|;/).map(function (s) { return s.trim(); }).filter(Boolean);
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
    exportBtn.disabled = !report;
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
    if (report.blocked_at) text += " at " + report.blocked_at;
    if (final === "PASS") text = "PASS — all five gates survived scrutiny. This is not advice to proceed; it is clearance that the proposal was inspectable.";
    if (final === "REVISE") text = "REVISE — first failure needs a more specific proposal. Feedback is on the lit gate.";
    if (final === "BLOCK") text = "BLOCK at " + (report.blocked_at || "a gate") + " — cannot be remedied without changing the proposal's nature.";
    banner.textContent = text;
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    const body = {
      statement: document.getElementById("statement").value,
      evidence: lines("evidence"),
      impacts_positive: lines("impacts_positive"),
      impacts_negative: lines("impacts_negative"),
      values: lines("values"),
      commitments: lines("commitments"),
      constraints: lines("constraints"),
      accountable_person: document.getElementById("accountable").value,
      overrides: overrides(),
    };
    fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    })
      .then(function (r) { return r.json(); })
      .then(paint)
      .catch(function (err) {
        banner.className = "banner BLOCK";
        banner.textContent = "Request failed: " + err;
      });
  });

  exportBtn.addEventListener("click", function () {
    if (!lastReport) return;
    const blob = new Blob([JSON.stringify(lastReport, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "decisiongate-lineage.json";
    a.click();
    URL.revokeObjectURL(a.href);
  });
})();
