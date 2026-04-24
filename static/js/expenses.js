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

const EXPLORER_LIMIT = 50;

function formatDate(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return raw;
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

// ── Transaction explorer: month range + search (client filter) ──────────────

/** @param {string} ym "YYYY-MM" */
function _lastDayOfMonth(ym) {
  const [y, m] = ym.split("-").map((x) => parseInt(x, 10));
  const last = new Date(y, m, 0).getDate();
  return `${y}-${String(m).padStart(2, "0")}-${String(last).padStart(2, "0")}`;
}

/** Inclusive start/end YYYY-MM-DD from two "YYYY-MM" month pickers. */
function rangeFromMonthInputs(fromYm, toYm) {
  let a = fromYm;
  let b = toYm;
  if (a && b && a > b) {
    const t = a;
    a = b;
    b = t;
  }
  if (!a || !b) return { start: null, end: null };
  return {
    start: `${a}-01`,
    end: _lastDayOfMonth(b),
  };
}

function filterTxnsBySearch(rows, q) {
  if (!q || !String(q).trim()) return rows;
  const s = String(q).trim().toLowerCase();
  return rows.filter((r) => {
    const parts = [
      r.merchant_raw,
      r.merchant_normalized,
      r.category,
      r.subcategory,
      r.transaction_date,
      r.document_id,
      r.amount,
      r.txn_type,
      r.account_label,
      r.flag_reason,
      r.is_flagged,
      r.is_recurring,
    ]
      .filter((x) => x !== undefined && x !== null)
      .map((x) => String(x));
    return parts.some((p) => p.toLowerCase().includes(s));
  });
}

function isFlaggedRow(r) {
  return r.is_flagged === 1 || r.is_flagged === true;
}

function isRecurringRow(r) {
  return r.is_recurring === 1 || r.is_recurring === true;
}

function txnTypeNorm(r) {
  return String(r.txn_type || "expense")
    .trim()
    .toLowerCase();
}

function truncateText(s, max) {
  const t = String(s || "").trim();
  if (t.length <= max) return t;
  return `${t.slice(0, Math.max(0, max - 1))}…`;
}

function populateFilterSelect(selectEl, values, placeholder, previous) {
  if (!selectEl) return;
  const sorted = [...values].filter(Boolean).sort((a, b) => a.localeCompare(b));
  const opts = [`<option value="">${placeholder}</option>`].concat(
    sorted.map((v) => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`)
  );
  selectEl.innerHTML = opts.join("");
  if (previous === "" || sorted.includes(previous)) {
    selectEl.value = previous;
  }
}

function applyExplorerFilters(raw) {
  let rows = raw.slice();
  const typeEl = document.getElementById("exp-explorer-type");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  const flaggedEl = document.getElementById("exp-explorer-flagged");
  const recEl = document.getElementById("exp-explorer-recurring");
  const searchEl = document.getElementById("exp-explorer-search");

  const t = typeEl && typeEl.value;
  if (t) rows = rows.filter((r) => txnTypeNorm(r) === t);

  const acc = accEl && accEl.value;
  if (acc) rows = rows.filter((r) => String(r.account_label || "") === acc);

  const cat = catEl && catEl.value;
  if (cat) rows = rows.filter((r) => String(r.category || "Uncategorized") === cat);

  if (flaggedEl && flaggedEl.checked) rows = rows.filter(isFlaggedRow);
  if (recEl && recEl.checked) rows = rows.filter(isRecurringRow);

  rows = filterTxnsBySearch(rows, searchEl && searchEl.value);
  return rows;
}

function explorerFiltersActive() {
  const typeEl = document.getElementById("exp-explorer-type");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  const flaggedEl = document.getElementById("exp-explorer-flagged");
  const recEl = document.getElementById("exp-explorer-recurring");
  const searchEl = document.getElementById("exp-explorer-search");
  const q = searchEl && searchEl.value && searchEl.value.trim();
  return Boolean(
    (typeEl && typeEl.value) ||
      (accEl && accEl.value) ||
      (catEl && catEl.value) ||
      (flaggedEl && flaggedEl.checked) ||
      (recEl && recEl.checked) ||
      q
  );
}

function describeActiveFilters() {
  const parts = [];
  const flaggedEl = document.getElementById("exp-explorer-flagged");
  const recEl = document.getElementById("exp-explorer-recurring");
  const typeEl = document.getElementById("exp-explorer-type");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  const searchEl = document.getElementById("exp-explorer-search");
  if (flaggedEl && flaggedEl.checked) parts.push("Flagged only");
  if (recEl && recEl.checked) parts.push("Recurring only");
  if (typeEl && typeEl.value) parts.push(`Type: ${typeEl.value}`);
  if (accEl && accEl.value) parts.push(`Account: ${accEl.value}`);
  if (catEl && catEl.value) parts.push(`Category: ${catEl.value}`);
  if (searchEl && searchEl.value.trim()) parts.push(`Search: “${truncateText(searchEl.value.trim(), 40)}”`);
  return parts;
}

function renderExplorerSummary(summaryEl, visibleRows) {
  if (!summaryEl) return;
  const n = visibleRows.length;
  let flagged = 0;
  let recurring = 0;
  let fees = 0;
  visibleRows.forEach((r) => {
    if (isFlaggedRow(r)) flagged += 1;
    if (isRecurringRow(r)) recurring += 1;
    if (txnTypeNorm(r) === "fee") fees += 1;
  });
  summaryEl.innerHTML = `
    <span class="exp-explorer__stat"><strong>${n}</strong> visible</span>
    <span class="exp-explorer__stat">${flagged} flagged</span>
    <span class="exp-explorer__stat">${recurring} recurring</span>
    <span class="exp-explorer__stat">${fees} fees</span>
  `;
}

function updateActiveFiltersLine(activeEl) {
  if (!activeEl) return;
  const parts = describeActiveFilters();
  const filtersWrap = document.getElementById("exp-explorer-filters");
  if (parts.length === 0) {
    activeEl.hidden = true;
    activeEl.textContent = "";
    if (filtersWrap) filtersWrap.open = false;
    return;
  }
  activeEl.hidden = false;
  activeEl.textContent = `Filters: ${parts.join(" · ")}`;
  if (filtersWrap) filtersWrap.open = true;
}

function exportVisibleRowsCsv(rows) {
  const headers = [
    "transaction_date",
    "txn_type",
    "account_label",
    "merchant_normalized",
    "category",
    "subcategory",
    "amount",
    "is_flagged",
    "is_recurring",
    "flag_reason",
  ];
  function csvCell(v) {
    const t = String(v ?? "");
    if (/[",\n\r]/.test(t)) return `"${t.replace(/"/g, '""')}"`;
    return t;
  }
  const lines = [headers.join(",")].concat(
    rows.map((r) =>
      headers
        .map((h) => {
          let v = r[h];
          if (h === "is_flagged") v = isFlaggedRow(r) ? "1" : "0";
          if (h === "is_recurring") v = isRecurringRow(r) ? "1" : "0";
          return csvCell(v);
        })
        .join(",")
    )
  );
  const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `expenses-explorer-${new Date().toLocaleDateString("sv-SE")}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}

function clearExplorerFilters() {
  const flaggedEl = document.getElementById("exp-explorer-flagged");
  const recEl = document.getElementById("exp-explorer-recurring");
  const typeEl = document.getElementById("exp-explorer-type");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  const searchEl = document.getElementById("exp-explorer-search");
  if (flaggedEl) flaggedEl.checked = false;
  if (recEl) recEl.checked = false;
  if (typeEl) typeEl.value = "";
  if (accEl) accEl.value = "";
  if (catEl) catEl.value = "";
  if (searchEl) searchEl.value = "";
}

let _txCache = { key: null, rows: null };
let _searchDebounce = null;
let _explorerWired = false;

function renderTxnTableInto(el, rows, emptyCtx) {
  if (!el) return;
  const rawLen = emptyCtx && typeof emptyCtx.rawLen === "number" ? emptyCtx.rawLen : 0;
  const filterActive = emptyCtx && emptyCtx.filterActive;

  if (!rows || rows.length === 0) {
    if (rawLen === 0) {
      el.innerHTML = `<div class="panel__empty">No transactions in this date range (or nothing loaded yet).</div>`;
    } else if (filterActive) {
      el.innerHTML = `<div class="panel__empty panel__empty--soft">No rows match your current filters or search. Try <button type="button" class="exp-explorer__linkbtn" id="exp-explorer-clear-inline">clearing filters</button>.</div>`;
      const inline = document.getElementById("exp-explorer-clear-inline");
      if (inline) {
        inline.addEventListener("click", () => {
          clearExplorerFilters();
          refreshExplorer();
        });
      }
    } else {
      el.innerHTML = `<div class="panel__empty">No rows to show.</div>`;
    }
    return;
  }
  const head = `<table class="exp-txn-table" role="table" aria-label="Transactions">
<thead><tr>
  <th scope="col">Merchant</th>
  <th scope="col">Category & status</th>
  <th scope="col" class="exp-txn-table__num">Amount</th>
</tr></thead><tbody>`;
  const body = rows
    .map((r) => {
      const date = escapeHtml(formatDate(r.transaction_date));
      const tt = txnTypeNorm(r);
      const typePill =
        tt === "fee"
          ? `<span class="pill pill--fee">Fee</span>`
          : `<span class="pill pill--type-exp">Expense</span>`;
      const merch = escapeHtml((r.merchant_normalized || r.merchant_raw || "—").toString());
      const acc = escapeHtml((r.account_label || "—").toString());
      const txnLabel = tt === "fee" ? "Fee" : "Expense";
      const merchMeta = `${date} · ${acc} · ${txnLabel}`;
      const sub = r.subcategory ? `<div class="exp-txn-cell__sub">${escapeHtml(r.subcategory)}</div>` : "";
      const cat = escapeHtml((r.category || "Uncategorized").toString());
      const flagged = isFlaggedRow(r);
      const rec = isRecurringRow(r);
      const flagFull = (r.flag_reason && String(r.flag_reason).trim()) ? String(r.flag_reason) : "";
      const flagShort = flagFull ? truncateText(flagFull, 72) : "";
      const badges = [
        flagged ? `<span class="pill pill--review">Flagged</span>` : "",
        rec ? `<span class="pill pill--muted">Recurring</span>` : "",
        typePill,
      ]
        .filter(Boolean)
        .join(" ");
      const reasonBlock =
        flagged && flagFull
          ? `<div class="exp-txn-flag-reason" title="${escapeHtml(flagFull)}">${escapeHtml(flagShort)}</div>`
          : "";
      const reconInner =
        (badges || reasonBlock)
          ? `<div class="exp-txn-recon-cell">${badges ? `<div class="exp-txn-badges">${badges}</div>` : ""}${reasonBlock}</div>`
          : "—";
      const amt = formatMoney(r.amount);
      return `<tr>
  <td>
    <div class="exp-txn-cell">
      <div class="exp-txn-cell__title">${merch}</div>
      <div class="exp-txn-cell__meta">${merchMeta}</div>
    </div>
  </td>
  <td class="exp-txn-table__recon">
    <div class="exp-txn-cell">
      <div class="exp-txn-cell__title">${cat}</div>
      ${sub}
      ${reconInner === "—" ? "" : reconInner}
    </div>
  </td>
  <td class="exp-txn-table__num">${escapeHtml(amt)}</td>
</tr>`;
    })
    .join("");
  el.innerHTML = head + body + `</tbody></table>`;
}

async function runIngest(documentId) {
  const res = await fetch(`/api/expenses/documents/${documentId}/ingest`, { method: "POST" });
  const text = await res.text();
  /** @type {any} */
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = null;
  }
  if (!res.ok) {
    const detail = parseHttpErrorDetail(data, text, res.status);
    return { ok: false, error: detail };
  }
  return { ok: true, data: data || {} };
}

function parseHttpErrorDetail(data, text, status) {
  if (data && data.detail != null) {
    const d = data.detail;
    if (Array.isArray(d)) {
      return d
        .map((x) => (typeof x === "object" && x && "msg" in x ? x.msg : String(x)))
        .join(" ");
    }
    return String(d);
  }
  if (text && text.length < 2000) return text;
  return `Request failed (${status})`;
}

function setIngestResultBanner(result) {
  const statusEl = document.getElementById("exp-status");
  if (!statusEl) return;
  if (!result) {
    statusEl.innerHTML = "";
    return;
  }
  if (!result.ok) {
    statusEl.innerHTML = `
      <div class="banner banner--error">
        <div class="banner__title">Import failed</div>
        <div class="banner__body">${escapeHtml(result.error || "Unknown error")}</div>
      </div>`;
    return;
  }

  const d = result.data || {};
  const inserted = d.inserted != null ? d.inserted : 0;
  const months = Array.isArray(d.months) && d.months.length ? d.months.join(", ") : "—";
  const rep = d.sanitize_report;
  const noteLines = Array.isArray(rep) ? rep.map((x) => String(x).trim()).filter(Boolean) : [];
  const summary = `Inserted ${Number(inserted)} transaction(s). Affected months: ${months}.`;
  const notesBlock =
    noteLines.length > 0
      ? `<div class="banner__ingest-notes"><div class="banner__ingest-notes-title">Sanitizer report</div><ul class="banner__ingest-list">${noteLines
          .map((line) => `<li>${escapeHtml(line)}</li>`)
          .join("")}</ul></div>`
      : "";
  statusEl.innerHTML = `
    <div class="banner banner--success">
      <div class="banner__title">Import complete</div>
      <div class="banner__body">
        <p class="banner__ingest-summary">${escapeHtml(summary)}</p>
        ${notesBlock}
      </div>
    </div>`;
}

let _uploadMounted = false;
let _chart = null;

function setBanner(kind, title, message) {
  const statusEl = document.getElementById("exp-status");
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

async function refreshExplorer() {
  const fromEl = document.getElementById("exp-explorer-month-from");
  const toEl = document.getElementById("exp-explorer-month-to");
  const tableEl = document.getElementById("exp-explorer-table");
  const metaEl = document.getElementById("exp-explorer-meta");
  const summaryEl = document.getElementById("exp-explorer-summary");
  const activeEl = document.getElementById("exp-explorer-active");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  if (!fromEl || !toEl || !tableEl || !metaEl) return;

  const { start, end } = rangeFromMonthInputs(fromEl.value, toEl.value);
  if (!start || !end) {
    metaEl.textContent = "Choose a month range";
    if (summaryEl) summaryEl.innerHTML = "";
    updateActiveFiltersLine(activeEl);
    tableEl.innerHTML = `<div class="panel__empty">Set both From and To month values.</div>`;
    return;
  }

  const key = `${start}|${end}`;
  if (_txCache.key !== key || !_txCache.rows) {
    metaEl.textContent = "Loading…";
    const prevAcc = accEl ? accEl.value : "";
    const prevCat = catEl ? catEl.value : "";
    try {
      const path = `/api/expenses/transactions?start_date=${encodeURIComponent(
        start
      )}&end_date=${encodeURIComponent(end)}&limit=${EXPLORER_LIMIT}`;
      const rows = await fetchJson(path);
      _txCache = { key, rows: Array.isArray(rows) ? rows : [] };
      const raw = _txCache.rows || [];
      const accounts = new Set();
      const categories = new Set();
      raw.forEach((r) => {
        if (r.account_label) accounts.add(String(r.account_label));
        const c = r.category || "Uncategorized";
        categories.add(String(c));
      });
      populateFilterSelect(accEl, accounts, "All accounts", prevAcc);
      populateFilterSelect(catEl, categories, "All categories", prevCat);
    } catch (e) {
      metaEl.textContent = "Error";
      if (summaryEl) summaryEl.innerHTML = "";
      tableEl.innerHTML = `<div class="panel__empty">Could not load transactions: ${escapeHtml(e.message || String(e))}</div>`;
      _txCache = { key: null, rows: null };
      updateActiveFiltersLine(activeEl);
      return;
    }
  }

  const raw = _txCache.rows || [];
  const filtered = applyExplorerFilters(raw);
  const filterOn = explorerFiltersActive();

  if (raw.length === 0) {
    metaEl.textContent = `0 loaded in range (max ${EXPLORER_LIMIT})`;
  } else if (filtered.length === raw.length && !filterOn) {
    metaEl.textContent = `${raw.length} loaded in range — all visible`;
  } else {
    metaEl.textContent = `${raw.length} loaded · ${filtered.length} visible${filterOn ? " (filters on)" : ""}`;
  }

  renderExplorerSummary(summaryEl, filtered);
  updateActiveFiltersLine(activeEl);
  renderTxnTableInto(tableEl, filtered, {
    rawLen: raw.length,
    filterActive: filterOn,
  });
}

function wireExplorerOnce() {
  if (_explorerWired) return;
  const fromEl = document.getElementById("exp-explorer-month-from");
  const toEl = document.getElementById("exp-explorer-month-to");
  const searchEl = document.getElementById("exp-explorer-search");
  const flaggedEl = document.getElementById("exp-explorer-flagged");
  const recEl = document.getElementById("exp-explorer-recurring");
  const typeEl = document.getElementById("exp-explorer-type");
  const accEl = document.getElementById("exp-explorer-account");
  const catEl = document.getElementById("exp-explorer-category");
  const clearBtn = document.getElementById("exp-explorer-clear");
  const exportBtn = document.getElementById("exp-explorer-export");
  if (!fromEl || !toEl) return;
  _explorerWired = true;
  fromEl.addEventListener("change", () => {
    _txCache = { key: null, rows: null };
    refreshExplorer();
  });
  toEl.addEventListener("change", () => {
    _txCache = { key: null, rows: null };
    refreshExplorer();
  });
  if (searchEl) {
    searchEl.addEventListener("input", () => {
      if (_searchDebounce) window.clearTimeout(_searchDebounce);
      _searchDebounce = window.setTimeout(() => {
        _searchDebounce = null;
        refreshExplorer();
      }, 200);
    });
  }
  [flaggedEl, recEl, typeEl, accEl, catEl].forEach((el) => {
    if (el) el.addEventListener("change", () => refreshExplorer());
  });
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      clearExplorerFilters();
      refreshExplorer();
    });
  }
  if (exportBtn) {
    exportBtn.addEventListener("click", () => {
      const raw = _txCache.rows || [];
      const filtered = applyExplorerFilters(raw);
      if (filtered.length === 0) return;
      exportVisibleRowsCsv(filtered);
    });
  }
}

function setDefaultMonthInputs(monthly) {
  const fromEl = document.getElementById("exp-explorer-month-from");
  const toEl = document.getElementById("exp-explorer-month-to");
  if (!fromEl || !toEl) return;
  if (fromEl.dataset.explorerInit === "1") return;
  const ym = monthly && monthly.length ? String(monthly[0].month) : null;
  const d = new Date();
  const fallback = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  const v = ym || fallback;
  fromEl.value = v;
  toEl.value = v;
  fromEl.dataset.explorerInit = "1";
  toEl.dataset.explorerInit = "1";
}

async function load(ingestOutcome) {
  if (!ingestOutcome) {
    clearBanner();
  } else {
    setIngestResultBanner(ingestOutcome);
  }

  const uploadHost = document.getElementById("expenses-upload");
  if (!_uploadMounted && uploadHost && window.HE && typeof window.HE.mountUploadSurface === "function") {
    _uploadMounted = true;
    window.HE.mountUploadSurface(uploadHost, {
      omitHead: true,
      title: "",
      help: "",
      moduleOwner: "expenses",
      accept: ".csv,.xlsx,.xls",
      onUploaded: async (payload) => {
        const docId = payload && payload.document_id;
        if (!docId) {
          setBanner("error", "Upload incomplete", "No document_id returned from upload.");
          return;
        }
        const outcome = await runIngest(docId);
        if (outcome.ok) {
          _txCache = { key: null, rows: null };
          await load({ ok: true, data: outcome.data });
        } else {
          await load({ ok: false, error: outcome.error });
        }
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
  const metaEl = document.getElementById("exp-monthly-meta");
  const emptyEl = document.getElementById("exp-monthly-empty");
  const canvas = document.getElementById("exp-monthly-chart");

  function warnPartial() {
    setBanner("warning", "Some data unavailable", "Showing what’s available.");
  }

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

  let monthApiFailed = false;
  let partialFailures = 0;
  const tryWarnPartial = () => {
    if (ingestOutcome) return;
    if (monthApiFailed) return;
    partialFailures += 1;
    if (partialFailures === 1) warnPartial();
  };

  let monthly = [];
  try {
    monthly = await fetchJson("/api/expenses/monthly");
  } catch (e) {
    monthApiFailed = true;
    if (!ingestOutcome) {
      setBanner("error", "Expenses unavailable", e.message || String(e));
    }
    monthly = [];
  }

  const latest = monthly && monthly.length ? monthly[0] : null;
  monthTotalEl.textContent = formatMoney(latest ? latest.total_expenses : 0);
  monthCountEl.textContent = String(latest ? latest.transaction_count : 0);

  let categories = [];
  try {
    categories = await fetchJson("/api/expenses/categories?limit=12");
  } catch (e) {
    tryWarnPartial();
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
    "🏷️ No categories"
  );

  let recent = [];
  try {
    recent = await fetchJson("/api/expenses/recent?limit=25");
  } catch (e) {
    tryWarnPartial();
    recent = [];
  }
  recentCountEl.textContent = String((recent || []).length);
  renderRows(
    recentEl,
    (recent || []).map((r) => {
      const title = escapeHtml(r.merchant_normalized || "Unknown");
      const subtitle = `${escapeHtml(formatDate(r.transaction_date))} · ${escapeHtml(r.category || "Uncategorized")}`;
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
    "🕒 No recent transactions"
  );

  setDefaultMonthInputs(monthly);
  wireExplorerOnce();
  await refreshExplorer();

  if (!monthly || monthly.length === 0) {
    if (emptyEl) emptyEl.style.display = "block";
    if (canvas) canvas.style.display = "none";
    if (metaEl) metaEl.textContent = "No trend data";
    return;
  }

  if (emptyEl) emptyEl.style.display = "none";
  if (canvas) canvas.style.display = "block";
  if (metaEl) metaEl.textContent = `Showing last ${Math.min(monthly.length, 12)} months`;
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
