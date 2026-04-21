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

async function load() {
  const monthTotalEl = document.getElementById("exp-card-month-total");
  const monthCountEl = document.getElementById("exp-card-month-count");
  const topCatEl = document.getElementById("exp-card-top-category");
  const topCatHintEl = document.getElementById("exp-card-top-category-hint");
  const recentCountEl = document.getElementById("exp-card-recent-count");

  const categoriesEl = document.getElementById("exp-categories");
  const recentEl = document.getElementById("exp-recent");

  // Monthly view-backed expenses.
  const monthly = await fetchJson("/api/expenses/monthly");
  const latest = monthly && monthly.length ? monthly[0] : null;
  monthTotalEl.textContent = formatMoney(latest ? latest.total_expenses : 0);
  monthCountEl.textContent = String(latest ? latest.transaction_count : 0);

  // Category breakdown.
  const categories = await fetchJson("/api/expenses/categories?limit=12");
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
    "No category data yet."
  );

  // Recent expense activity.
  const recent = await fetchJson("/api/expenses/recent?limit=25");
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
    "No recent expenses yet."
  );

  // Monthly trend chart.
  const metaEl = document.getElementById("exp-monthly-meta");
  const emptyEl = document.getElementById("exp-monthly-empty");
  const canvas = document.getElementById("exp-monthly-chart");

  if (!monthly || monthly.length === 0) {
    emptyEl.style.display = "block";
    canvas.style.display = "none";
    return;
  }

  metaEl.textContent = `Showing last ${Math.min(monthly.length, 12)} months`;
  const rows = monthly.slice(0, 12).reverse();
  const labels = rows.map((x) => x.month);
  const totals = rows.map((x) => Number(x.total_expenses || 0));

  // eslint-disable-next-line no-undef
  new Chart(canvas.getContext("2d"), {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Expenses",
          data: totals,
          backgroundColor: "rgba(251,113,133,0.18)",
          borderColor: "#fb7185",
          borderWidth: 1,
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: "#cbd5e1" } } },
      scales: {
        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.12)" } },
        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(148,163,184,0.12)" } },
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
