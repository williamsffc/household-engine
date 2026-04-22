function formatMoney(n) {
  const v = Number(n || 0);
  return v.toLocaleString(undefined, { style: "currency", currency: "USD" });
}

async function fetchJson(path) {
  const res = await fetch(path, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${path} failed: ${res.status} ${text}`);
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

function cssVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

async function load() {
  const incomeEl = document.getElementById("card-income");
  const incomeHintEl = document.getElementById("card-income-hint");
  const expensesEl = document.getElementById("card-expenses");
  const netEl = document.getElementById("card-net");
  const pendingEl = document.getElementById("card-pending");

  const recentDocsEl = document.getElementById("recent-docs");
  const pendingReviewEl = document.getElementById("pending-review");

  // Summary card uses view-backed overview summary (income is approved-only).
  const summary = await fetchJson("/api/overview/summary");
  incomeEl.textContent = formatMoney(summary.total_income);
  expensesEl.textContent = formatMoney(summary.total_expenses);
  netEl.textContent = formatMoney(summary.net_cashflow);

  if (Number(summary.total_income || 0) <= 0) {
    incomeHintEl.style.display = "block";
    incomeHintEl.textContent = "No approved payroll yet (draft paystubs are excluded).";
  } else {
    incomeHintEl.style.display = "none";
  }

  // Recent documents widget.
  const recent = await fetchJson("/api/overview/recent-documents?limit=10");
  renderRows(
    recentDocsEl,
    recent.map((d) => {
      const title = escapeHtml(d.original_filename || `Document ${d.document_id}`);
      const subtitle = `${escapeHtml(d.module_owner)} · ${escapeHtml(d.status)} · ${escapeHtml(d.uploaded_at)}`;
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
    "No documents yet."
  );

  // Pending review widget.
  const pending = await fetchJson("/api/review-queue");
  pendingEl.textContent = String(pending.length || 0);
  renderRows(
    pendingReviewEl,
    pending.map((d) => {
      const title = escapeHtml(d.original_filename || `Document ${d.document_id}`);
      const subtitle = `${escapeHtml(d.module_owner)} · uploaded ${escapeHtml(d.uploaded_at)}`;
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
    "No pending review items."
  );

  // Cashflow chart (view-backed).
  const cashflow = await fetchJson("/api/overview/cashflow");
  const metaEl = document.getElementById("cashflow-meta");
  const emptyEl = document.getElementById("cashflow-empty");
  const canvas = document.getElementById("cashflow-chart");

  if (!cashflow || cashflow.length === 0) {
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
