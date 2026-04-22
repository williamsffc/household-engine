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

function setParam(key, value) {
  const url = new URL(window.location.href);
  if (value === null || value === undefined || value === "") {
    url.searchParams.delete(key);
  } else {
    url.searchParams.set(key, String(value));
  }
  window.history.replaceState({}, "", url.toString());
}

function getParamStr(key) {
  const url = new URL(window.location.href);
  const v = url.searchParams.get(key);
  return v == null ? null : String(v);
}

function clampInt(n, min, max) {
  const x = Math.trunc(Number(n));
  if (!Number.isFinite(x)) return null;
  return Math.max(min, Math.min(max, x));
}

function clampFloat(n, min, max) {
  const x = Number(n);
  if (!Number.isFinite(x)) return null;
  return Math.max(min, Math.min(max, x));
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

let _loading = false;

function getControls() {
  return {
    trailingInput: document.getElementById("portfolio-trailing-months"),
    reserveInput: document.getElementById("portfolio-liquidity-reserve-months"),
    applyBtn: document.getElementById("portfolio-apply"),
  };
}

function getRequestedParamsFromUrlOrDefaults() {
  const trailingRaw = getParamStr("trailing_months");
  const reserveRaw = getParamStr("liquidity_reserve_months");
  const trailing = clampInt(trailingRaw ?? 3, 1, 12) ?? 3;
  const reserve = clampFloat(reserveRaw ?? 1.0, 0.0, 6.0);
  return {
    trailing_months: trailing,
    liquidity_reserve_months: reserve == null ? 1.0 : Math.round(reserve * 10) / 10,
  };
}

function setControlsFromParams(params) {
  const { trailingInput, reserveInput } = getControls();
  if (trailingInput) trailingInput.value = String(params.trailing_months);
  if (reserveInput) reserveInput.value = String(params.liquidity_reserve_months);
}

function readParamsFromControls() {
  const { trailingInput, reserveInput } = getControls();
  const trailing = clampInt(trailingInput?.value ?? "", 1, 12);
  const reserve = clampFloat(reserveInput?.value ?? "", 0.0, 6.0);
  if (trailing == null) throw new Error("Trailing months must be a number between 1 and 12.");
  if (reserve == null) throw new Error("Liquidity reserve months must be a number between 0 and 6.");
  return {
    trailing_months: trailing,
    liquidity_reserve_months: Math.round(reserve * 10) / 10,
  };
}

async function load(params) {
  if (_loading) return;
  _loading = true;
  const cards = document.getElementById("portfolio-cards");
  if (cards) cards.innerHTML = skeletonCards();
  setBanner(null);

  try {
    const qs = new URLSearchParams();
    if (params?.trailing_months != null) qs.set("trailing_months", String(params.trailing_months));
    if (params?.liquidity_reserve_months != null)
      qs.set("liquidity_reserve_months", String(params.liquidity_reserve_months));
    const summary = await fetchJson(`/api/overview/portfolio?${qs.toString()}`);
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
  } finally {
    _loading = false;
  }
}

function bindControlsOnce() {
  const { trailingInput, reserveInput, applyBtn } = getControls();
  if (applyBtn && !applyBtn.dataset.bound) {
    applyBtn.dataset.bound = "1";
    applyBtn.addEventListener("click", async () => {
      try {
        const p = readParamsFromControls();
        setParam("trailing_months", p.trailing_months);
        setParam("liquidity_reserve_months", p.liquidity_reserve_months);
        await load(p);
      } catch (e) {
        setBanner("error", "Invalid controls", e.message || String(e));
      }
    });
  }

  // Enter in either input applies.
  [trailingInput, reserveInput].forEach((inp) => {
    if (inp && !inp.dataset.bound) {
      inp.dataset.bound = "1";
      inp.addEventListener("keydown", async (e) => {
        if (e.key !== "Enter") return;
        e.preventDefault();
        applyBtn?.click();
      });
    }
  });
}

(() => {
  const initial = getRequestedParamsFromUrlOrDefaults();
  setControlsFromParams(initial);
  bindControlsOnce();
  load(initial).catch((err) => {
    console.error(err);
    setBanner("error", "Portfolio unavailable", err.message || String(err));
  });
})();

