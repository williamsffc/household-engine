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

function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderRows(el, rows, emptyText) {
  if (!rows || rows.length === 0) {
    el.innerHTML = `<div class="panel__empty">${emptyText}</div>`;
    return;
  }
  el.innerHTML = rows.join("");
}

function cssVar(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

let _uploadMounted = false;
let _chart = null;

async function load() {
  // Step 14C: in-app upload surface (expenses documents).
  const uploadHost = document.getElementById("expenses-upload");
  if (!_uploadMounted && uploadHost && window.HE && typeof window.HE.mountUploadSurface === "function") {
    _uploadMounted = true;
    window.HE.mountUploadSurface(uploadHost, {
      title: "Upload expense document",
      help: "Upload CSV/XLS/XLSX statements for the Expenses module. This registers the document in the system.",
      moduleOwner: "expenses",
      accept: ".csv,.xlsx,.xls",
      onUploaded: async (payload) => {
        const docId = payload?.document_id;
        if (!docId) return;
        try {
          await fetch(`/api/expenses/documents/${docId}/ingest`, { method: "POST" });
        } catch {
          // Ignore; ingest errors will surface in later UX work (Step 14D).
        }
        // Reload the page data (not the upload UI).
        await load();
      },
    });
  }

  const monthTotalEl = document.getElementById("exp-card-month-total");
  const monthCountEl = document.getElementById("exp-card-month-count");
  const topCatEl = document.getElementById("exp-card-top-category");
  const topCatHintEl = document.getElementById("exp-card-top-category-hint");
  const recentCountEl = document.getElementById("exp-card-recent-count");

  const categoriesEl = document.getElementById("exp-categories");
  const recentEl = document.getElementById("exp-recent");
  const statusEl = document.getElementById("exp-status");
  const metaEl = document.getElementById("exp-monthly-meta");
  const emptyEl = document.getElementById("exp-monthly-empty");
  const canvas = document.getElementById("exp-monthly-chart");

  function setBanner(kind, title, message) {
    if (!statusEl) return;
    if (!kind) {
      statusEl.innerHTML = "";
      return;
    }
    const bannerClass = kind === "error" ? "banner--error" : kind === "success" ? "banner--success" : "banner--warning";
    statusEl.innerHTML = `
      <div class="banner ${bannerClass}">
        <div class="banner__title">${escapeHtml(title || "Expenses")}</div>
        <div class="banner__body">${escapeHtml(message || "Unknown error")}</div>
      </div>
    `;
  }

  function clearBanner() {
    setBanner(null);
  }

  // Loading placeholders (keeps page calm).
  monthTotalEl.textContent = "—";
  monthCountEl.textContent = "—";
  topCatEl.textContent = "—";
  topCatHintEl.textContent = "";
  recentCountEl.textContent = "—";
  if (categoriesEl) {
    categoriesEl.innerHTML = `<div class="skeleton"><div class="skeleton__line"></div><div class="skeleton__line"></div><div class="skeleton__line"></div></div>`;
  }
  if (recentEl) {
    recentEl.innerHTML = `<div class="skeleton"><div class="skeleton__line"></div><div class="skeleton__line"></div><div class="skeleton__line"></div></div>`;
  }
  if (metaEl) metaEl.textContent = "Loading…";
  if (emptyEl) emptyEl.style.display = "none";
  if (canvas) canvas.style.display = "block";

  clearBanner();

  let partialFailures = 0;
  const warnPartial = () => {
    partialFailures += 1;
    if (partialFailures === 1) {
      setBanner("warning", "Some data unavailable", "Showing what’s available.");
    }
  };

  let monthly = [];
  try {
    monthly = await fetchJson("/api/expenses/monthly");
  } catch (e) {
    setBanner("error", "Expenses unavailable", e.message || String(e));
    monthly = [];
  }

  const latest = monthly && monthly.length ? monthly[0] : null;
  monthTotalEl.textContent = formatMoney(latest ? latest.total_expenses : 0);
  monthCountEl.textContent = String(latest ? latest.transaction_count : 0);

  // Category breakdown.
  let categories = [];
  try {
    categories = await fetchJson("/api/expenses/categories?limit=12");
  } catch (e) {
    warnPartial();
    categories = [];
  }
  const top = categories && categories.length ? categories[0] : null;
  topCatEl.textContent = top ? escapeHtml(top.category) : "—";
  topCatHintEl.textContent = top ? `${formatMoney(top.total_amount)} across ${top.transaction_count} txns` : "";

  renderRows(
    categoriesEl,
    (categories || []).map((c) => {
      const title = escapeHtml(c.category);
      const subtitle = `${formatMoney(c.total_amount)} · ${c.transaction_count} txns`;
      return `
        <div class="row">
          <div class="row__left">
            <div class="row__title">${title}</div>
            <div class="row__subtitle">${subtitle}</div>
          </div>
          <div class="pill">${formatMoney(c.total_amount)}</div>
        </div>
      `;
    }),
    "No categories"
  );

  // Recent expense activity.
  let recent = [];
  try {
    recent = await fetchJson("/api/expenses/recent?limit=25");
  } catch (e) {
    warnPartial();
    recent = [];
  }
  recentCountEl.textContent = String((recent || []).length);
  renderRows(
    recentEl,
    (recent || []).map((r) => {
      const title = escapeHtml(r.merchant_normalized || "Unknown");
      const subtitle = `${escapeHtml(r.transaction_date)} · ${escapeHtml(r.category || "Uncategorized")}`;
      return `
        <div class="row">
          <div class="row__left">
            <div class="row__title">${title}</div>
            <div class="row__subtitle">${subtitle}</div>
          </div>
          <div class="pill">${formatMoney(r.amount)}</div>
        </div>
      `;
    }),
    "No recent transactions"
  );

  // Monthly trend chart.
  if (!monthly || monthly.length === 0) {
    emptyEl.style.display = "block";
    canvas.style.display = "none";
    return;
  }

  metaEl.textContent = `Showing last ${Math.min(monthly.length, 12)} months`;
  const rows = monthly.slice(0, 12).reverse();
  const labels = rows.map((x) => x.month);
  const totals = rows.map((x) => Number(x.total_expenses || 0));

  const grid = cssVar("--chart-grid", "rgba(15,23,42,0.12)");
  const tick = cssVar("--color-text-muted", "#475569");
  const legend = cssVar("--color-text-muted", "#475569");

  // eslint-disable-next-line no-undef
  if (_chart && typeof _chart.destroy === "function") {
    try {
      _chart.destroy();
    } catch {
      // ignore
    }
  }
  _chart = new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Expenses",
          data: totals,
          backgroundColor: cssVar("--chart-expenses-fill", "rgba(220,38,38,0.12)"),
          borderColor: cssVar("--chart-expenses", "#dc2626"),
          borderWidth: 1,
          borderRadius: 8,
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
    div.innerHTML = `<div class="panel__title">Expenses failed to load</div><div class="panel__empty">${escapeHtml(
      err.message
    )}</div>`;
    main.prepend(div);
  }
});
