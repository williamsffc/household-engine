function formatMoney(n) {
  const v = Number(n || 0);
  return v.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

async function fetchJson(path) {
  const res = await fetch(path, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    const text = await res.text();
    const err = new Error(text || `${path} failed`);
    err.status = res.status;
    err.path = path;
    throw err;
  }
  return await res.json();
}

function renderRows(el, rows, emptyText) {
  if (!rows || rows.length === 0) {
    el.innerHTML = `<div class="panel__empty">${emptyText}</div>`;
    return;
  }
  el.innerHTML = rows.join("");
}

function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDateTime(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return escapeHtml(raw);
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function cssVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

function setBanner(kind, title, message) {
  const el = document.getElementById("overview-status");
  if (!el) return;
  if (!kind) {
    el.innerHTML = "";
    return;
  }
  const bannerClass = kind === "error" ? "banner--error" : kind === "success" ? "banner--success" : "banner--warning";
  el.innerHTML = `
    <div class="banner ${bannerClass}">
      <div class="banner__title">${escapeHtml(title || "Overview")}</div>
      <div class="banner__body">${escapeHtml(message || "Unknown error")}</div>
    </div>
  `;
}

function clearBanner() {
  setBanner(null);
}

function readinessPillClass(sectionKey, status) {
  if (sectionKey === "approved_payroll") {
    return status === "ready" ? "pill--ok" : "pill--danger";
  }
  if (sectionKey === "expense_history") {
    if (status === "ready") return "pill--ok";
    if (status === "limited") return "pill--limited";
    return "pill--danger";
  }
  if (sectionKey === "review_queue") {
    return status === "pending" ? "pill--review" : "pill--muted";
  }
  if (sectionKey === "planning") {
    return status === "usable" ? "pill--ok" : "pill--limited";
  }
  return "pill--muted";
}

function readinessPillLabel(sectionKey, status, count) {
  if (sectionKey === "approved_payroll") return status === "ready" ? "Ready" : "Missing";
  if (sectionKey === "expense_history") {
    if (status === "ready") return "Ready";
    if (status === "limited") return "Limited";
    return "Missing";
  }
  if (sectionKey === "review_queue") {
    if (status === "pending") return count === 1 ? "1 pending" : `${count} pending`;
    return "Clear";
  }
  if (sectionKey === "planning") return status === "usable" ? "OK" : "Limited";
  return status || "—";
}

function renderReadiness(data) {
  const grid = document.getElementById("overview-readiness-grid");
  if (!grid) return;

  if (!data) {
    grid.innerHTML = `<div class="readiness-item" style="grid-column: 1 / -1;">
      <div class="readiness-item__detail">Readiness status unavailable. Other overview widgets may still load.</div>
    </div>`;
    return;
  }

  const keys = ["approved_payroll", "expense_history", "review_queue", "planning"];
  grid.innerHTML = keys
    .map((key) => {
      const block = data[key] || {};
      const title = escapeHtml(block.title || key);
      const detail = escapeHtml(block.detail || "");
      const status = block.status || "";
      const count = Number(block.count || 0);
      const pillLabel = escapeHtml(readinessPillLabel(key, status, count));
      const pillClass = readinessPillClass(key, status);
      return `
        <div class="readiness-item">
          <div class="readiness-item__top">
            <div class="readiness-item__label">${title}</div>
            <div class="pill ${pillClass}">${pillLabel}</div>
          </div>
          <div class="readiness-item__detail">${detail}</div>
        </div>
      `;
    })
    .join("");
}

async function load() {
  const incomeEl = document.getElementById("card-income");
  const incomeHintEl = document.getElementById("card-income-hint");
  const expensesEl = document.getElementById("card-expenses");
  const netEl = document.getElementById("card-net");
  const pendingEl = document.getElementById("card-pending");

  const recentDocsEl = document.getElementById("recent-docs");
  const pendingReviewEl = document.getElementById("pending-review");

  clearBanner();

  let partialFailures = 0;
  const warnPartial = () => {
    partialFailures += 1;
    if (partialFailures === 1) {
      setBanner("warning", "Some data unavailable", "Showing what’s available.");
    }
  };

  let summary = null;
  try {
    summary = await fetchJson("/api/overview/summary");
  } catch (e) {
    setBanner("error", "Overview unavailable", e.message || String(e));
    throw e;
  }

  const readinessRes = await fetchJson("/api/overview/readiness").catch((e) => {
    console.warn(e);
    warnPartial();
    return null;
  });
  renderReadiness(readinessRes);

  // Summary card uses view-backed overview summary (income is approved-only).
  incomeEl.textContent = formatMoney(summary.total_income);
  expensesEl.textContent = formatMoney(summary.total_expenses);
  netEl.textContent = formatMoney(summary.net_cashflow);
  // Align with /api/overview/readiness review_queue.count until the list loads.
  pendingEl.textContent = String(summary.pending_reviews ?? 0);

  if (Number(summary.total_income || 0) <= 0) {
    incomeHintEl.style.display = "block";
    incomeHintEl.textContent = "No approved payroll yet (draft excluded).";
  } else {
    incomeHintEl.style.display = "none";
  }

  // Recent documents widget.
  const recent = await fetchJson("/api/overview/recent-documents?limit=10").catch((e) => {
    console.warn(e);
    warnPartial();
    return [];
  });
  renderRows(
    recentDocsEl,
    recent.map((d) => {
      const title = escapeHtml(d.original_filename || `Document ${d.document_id}`);
      const subtitle = `${escapeHtml(d.module_owner)} · ${escapeHtml(d.status)} · ${escapeHtml(formatDateTime(d.uploaded_at))}`;
      return `
        <div class="row">
          <div class="row__left">
            <div class="row__title">${title}</div>
            <div class="row__subtitle">${subtitle}</div>
          </div>
          <div class="pill">${escapeHtml(d.status)}</div>
        </div>
      `;
    }),
    "🗂️ No documents"
  );

  // Pending review widget.
  const pending = await fetchJson("/api/review-queue").catch((e) => {
    console.warn(e);
    warnPartial();
    return null;
  });
  if (pending) pendingEl.textContent = String(pending.length || 0);
  renderRows(
    pendingReviewEl,
    (pending || []).map((d) => {
      const title = escapeHtml(d.original_filename || `Document ${d.document_id}`);
      const subtitle = `${escapeHtml(d.module_owner)} · uploaded ${escapeHtml(formatDateTime(d.uploaded_at))}`;
      return `
        <div class="row">
          <div class="row__left">
            <div class="row__title">${title}</div>
            <div class="row__subtitle">${subtitle}</div>
          </div>
          <div class="pill pill--review">in_review</div>
        </div>
      `;
    }),
    pending ? "✅ Nothing to review" : "⚠️ Review list unavailable"
  );

  // Cashflow chart (view-backed).
  const cashflow = await fetchJson("/api/overview/cashflow").catch((e) => {
    console.warn(e);
    warnPartial();
    return null;
  });
  const metaEl = document.getElementById("cashflow-meta");
  const emptyEl = document.getElementById("cashflow-empty");
  const canvas = document.getElementById("cashflow-chart");

  if (!cashflow) {
    emptyEl.style.display = "block";
    emptyEl.textContent = "Cashflow trend unavailable.";
    canvas.style.display = "none";
    return;
  }

  if (cashflow.length === 0) {
    emptyEl.style.display = "block";
    canvas.style.display = "none";
    return;
  }

  metaEl.textContent = `Showing last ${Math.min(cashflow.length, 12)} months`;

  const rows = cashflow.slice(0, 12).reverse();
  const labels = rows.map((r) => r.month);
  const net = rows.map((r) => Number(r.net_cashflow || 0));
  const income = rows.map((r) => Number(r.total_income || 0));
  const expenses = rows.map((r) => Number(r.total_expenses || 0));

  const grid = cssVar("--chart-grid", "rgba(15,23,42,0.12)");
  const tick = cssVar("--color-text-muted", "#475569");
  const legend = cssVar("--color-text-muted", "#475569");

  // eslint-disable-next-line no-undef
  new Chart(canvas.getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Net",
          data: net,
          borderColor: cssVar("--chart-net", "#2563eb"),
          backgroundColor: cssVar("--chart-net-fill", "rgba(37,99,235,0.14)"),
          tension: 0.25,
        },
        {
          label: "Income",
          data: income,
          borderColor: cssVar("--chart-income", "#16a34a"),
          backgroundColor: cssVar("--chart-income-fill", "rgba(22,163,74,0.12)"),
          tension: 0.25,
        },
        {
          label: "Expenses",
          data: expenses,
          borderColor: cssVar("--chart-expenses", "#dc2626"),
          backgroundColor: cssVar("--chart-expenses-fill", "rgba(220,38,38,0.12)"),
          tension: 0.25,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: legend } } },
      scales: {
        x: { ticks: { color: tick }, grid: { color: grid } },
        y: { ticks: { color: tick }, grid: { color: grid } },
      },
    },
  });
}

load().catch((err) => {
  console.error(err);
  const main = document.querySelector(".main");
  if (main) {
    const div = document.createElement("div");
    div.className = "panel";
    div.innerHTML = `<div class="panel__title">Overview failed to load</div><div class="panel__empty">${escapeHtml(
      err.message
    )}</div>`;
    main.prepend(div);
  }
});
