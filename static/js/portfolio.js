function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function fetchJson(path) {
  const res = await fetch(path, { headers: { Accept: "application/json" } });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${path} failed: ${res.status} ${text}`);
  }
  return await res.json();
}

function money(v) {
  const n = Number(v || 0);
  if (!Number.isFinite(n)) return "—";
  return n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function skeletonCards() {
  return Array.from({ length: 4 })
    .map(
      () => `
      <div class="card">
        <div class="card__label skeleton__line" style="height:12px; width:120px;"></div>
        <div class="card__value skeleton__line" style="height:24px; width:180px; margin-top:8px;"></div>
        <div class="card__hint skeleton__line" style="height:12px; width:220px; margin-top:10px;"></div>
      </div>
    `
    )
    .join("");
}

function setBanner(kind, title, body) {
  const el = document.getElementById("portfolio-status");
  if (!el) return;
  if (!kind) {
    el.innerHTML = "";
    return;
  }
  const bannerClass = kind === "error" ? "banner--error" : "banner--warning";
  el.innerHTML = `
    <div class="banner ${bannerClass}">
      <div class="banner__title">${escapeHtml(title)}</div>
      <div class="banner__body">${escapeHtml(body)}</div>
    </div>
  `;
}

function renderCards(summary) {
  const el = document.getElementById("portfolio-cards");
  if (!el) return;

  const est = summary?.estimates || {};
  const asOf = summary?.as_of_month || "—";
  const availOk = Boolean(summary?.availability?.ok);

  el.innerHTML = `
    <div class="card">
      <div class="card__label">Deployable surplus</div>
      <div class="card__value">${money(est.current_estimated_surplus)}</div>
      <div class="card__hint">As of ${escapeHtml(asOf)} (flow-based estimate)</div>
    </div>
    <div class="card">
      <div class="card__label">Liquidity reserve target</div>
      <div class="card__value">${money(est.liquidity_reserve)}</div>
      <div class="card__hint">Based on trailing expenses</div>
    </div>
    <div class="card">
      <div class="card__label">Available for allocation</div>
      <div class="card__value">${money(est.available_for_allocation)}</div>
      <div class="card__hint">${availOk ? "Only when approved payroll exists" : "Unavailable until approved payroll exists"}</div>
    </div>
    <div class="card">
      <div class="card__label">Available for trading</div>
      <div class="card__value">${money(est.available_for_trading)}</div>
      <div class="card__hint">Remainder after allocation split</div>
    </div>
  `;
}

function renderExplain(summary) {
  const el = document.getElementById("portfolio-explain");
  if (!el) return;
  const a = summary?.assumptions || {};
  const availability = summary?.availability || { ok: false, reason: "Unknown" };

  el.innerHTML = `
    <div class="callout callout--info">
      <div class="callout__title">Definition</div>
      <div class="callout__body">${escapeHtml(a.deployable_surplus_definition || "Flow-based estimate derived from monthly cashflow.")}</div>
    </div>
    <div class="callout callout--info">
      <div class="callout__title">Income semantics</div>
      <div class="callout__body">${escapeHtml(a.income_semantics || "Approved payroll only.")}</div>
    </div>
    <div class="callout callout--info">
      <div class="callout__title">Availability</div>
      <div class="callout__body">
        ${availability.ok ? "Available: approved payroll exists." : escapeHtml(availability.reason || "Unavailable.")}
      </div>
    </div>
  `;
}

function renderInputs(summary) {
  const el = document.getElementById("portfolio-inputs");
  const metaEl = document.getElementById("portfolio-inputs-meta");
  if (!el) return;

  const a = summary?.assumptions || {};
  const ta = summary?.inputs?.trailing_averages || {};

  if (metaEl) metaEl.textContent = `trailing_months=${escapeHtml(a.trailing_months)}`;

  el.innerHTML = `
    <div class="kv">
      <div class="kv__item">
        <div class="kv__label">Trailing avg income</div>
        <div class="kv__value">${money(ta.monthly_income)}</div>
      </div>
      <div class="kv__item">
        <div class="kv__label">Trailing avg expenses</div>
        <div class="kv__value">${money(ta.monthly_expenses)}</div>
      </div>
      <div class="kv__item">
        <div class="kv__label">Trailing avg net</div>
        <div class="kv__value">${money(ta.monthly_net_cashflow)}</div>
      </div>
      <div class="kv__item">
        <div class="kv__label">Liquidity reserve months</div>
        <div class="kv__value">${escapeHtml(a.liquidity_reserve_months_target)}</div>
      </div>
    </div>
  `;
}

function renderCashflow(summary) {
  const el = document.getElementById("portfolio-cashflow");
  if (!el) return;
  const rows = Array.isArray(summary?.inputs?.cashflow_rows) ? summary.inputs.cashflow_rows : [];
  if (!rows.length) {
    el.innerHTML = `<div class="panel__empty">No cashflow rows available yet.</div>`;
    return;
  }

  el.innerHTML = rows
    .slice(0, 12)
    .map((r) => {
      const m = escapeHtml(r.month);
      return `
        <div class="row">
          <div class="row__left">
            <div class="row__title">${m}</div>
            <div class="row__subtitle">income ${money(r.total_income)} · expenses ${money(r.total_expenses)}</div>
          </div>
          <div class="pill pill--muted">${money(r.net_cashflow)}</div>
        </div>
      `;
    })
    .join("");
}

async function load() {
  const cards = document.getElementById("portfolio-cards");
  if (cards) cards.innerHTML = skeletonCards();
  setBanner(null);

  try {
    const summary = await fetchJson("/api/overview/portfolio");
    renderCards(summary);
    renderExplain(summary);
    renderInputs(summary);
    renderCashflow(summary);

    const availability = summary?.availability || {};
    if (!availability.ok) {
      setBanner("warning", "Portfolio planning is limited", availability.reason || "Approved payroll is required.");
    }
  } catch (e) {
    setBanner("error", "Portfolio unavailable", e.message || String(e));
    const el = document.getElementById("portfolio-cards");
    if (el) el.innerHTML = "";
  }
}

load().catch((err) => {
  console.error(err);
  setBanner("error", "Portfolio unavailable", err.message || String(err));
});

