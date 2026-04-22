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

function renderRows(el, rows, emptyText) {
  if (!rows || rows.length === 0) {
    el.innerHTML = `<div class="panel__empty">${emptyText}</div>`;
    return;
  }
  el.innerHTML = rows.join("");
}

let _uploadMounted = false;
let _loading = false;

function setParam(key, value) {
  const url = new URL(window.location.href);
  if (value === null || value === undefined || value === "") {
    url.searchParams.delete(key);
  } else {
    url.searchParams.set(key, String(value));
  }
  window.history.replaceState({}, "", url.toString());
}

function getParamInt(key) {
  const url = new URL(window.location.href);
  const v = url.searchParams.get(key);
  if (!v) return null;
  const n = Number(v);
  return Number.isFinite(n) ? Math.trunc(n) : null;
}

function setBannerError(message) {
  const el = document.getElementById("rq-status");
  if (!el) return;
  el.innerHTML = `
    <div class="banner banner--error">
      <div class="banner__title">Review Queue unavailable</div>
      <div class="banner__body">${escapeHtml(message || "Unknown error")}</div>
    </div>
  `;
}

function clearBanner() {
  const el = document.getElementById("rq-status");
  if (el) el.innerHTML = "";
}

function skeletonRows(n) {
  return `<div class="skeleton">${Array.from({ length: n })
    .map(() => '<div class="skeleton__line"></div>')
    .join("")}</div>`;
}

async function load() {
  if (_loading) return;
  _loading = true;

  try {
    // Step 14C: in-app upload surface (payroll docs enter review queue).
    const uploadHost = document.getElementById("payroll-upload");
    if (!_uploadMounted && uploadHost && window.HE && typeof window.HE.mountUploadSurface === "function") {
      _uploadMounted = true;
      window.HE.mountUploadSurface(uploadHost, {
        title: "Upload payroll document",
        help: "Upload a paystub (PDF or image) to create a draft for review. Draft payroll does not affect analytics until approval exists.",
        moduleOwner: "payroll",
        accept: ".pdf,.png,.jpg,.jpeg",
        extraFieldsHtml: `
          <div class="upload__field">
            <div class="upload__label">member_id (required for payroll ingest)</div>
            <input class="upload__input" id="payroll-member-id" inputmode="numeric" placeholder="e.g. 1" />
          </div>
          <div class="upload__field">
            <div class="upload__label">After upload</div>
            <label class="upload__label" style="display:flex; gap:8px; align-items:center;">
              <input type="checkbox" id="payroll-auto-ingest" checked />
              Run draft ingest (moves document to in_review)
            </label>
          </div>
        `,
        getExtraFields: (root) => {
          const memberId = root.querySelector("#payroll-member-id")?.value;
          const auto = root.querySelector("#payroll-auto-ingest")?.checked;
          return { member_id: memberId, auto_ingest: Boolean(auto) };
        },
        onUploaded: async (payload, root) => {
          const docId = payload?.document_id;
          const auto = root.querySelector("#payroll-auto-ingest")?.checked;
          if (docId && auto) {
            try {
              await fetch(`/api/payroll/documents/${docId}/ingest`, { method: "POST" });
            } catch {
              // Ignore; ingest errors will be improved in Step 15/16 UX later.
            }
          }
          await load();
        },
      });
    }

    const listEl = document.getElementById("rq-list");
    const detailEl = document.getElementById("rq-detail");
    const metaEl = document.getElementById("rq-meta");
    const detailMetaEl = document.getElementById("rq-detail-meta");

    clearBanner();
    if (listEl) listEl.innerHTML = skeletonRows(4);
    if (detailEl) detailEl.innerHTML = skeletonRows(6);
    if (metaEl) metaEl.textContent = "Loading…";
    if (detailMetaEl) detailMetaEl.textContent = "";

    let items = [];
    try {
      items = await fetchJson("/api/review-queue");
    } catch (e) {
      setBannerError(e.message || String(e));
      items = [];
    }

    if (metaEl) metaEl.textContent = `${items.length || 0} item(s)`;

    const selectedId = getParamInt("document_id") ?? (items[0] ? Number(items[0].document_id) : null);

    renderRows(
      listEl,
      items.map((d) => {
        const docId = Number(d.document_id);
        const title = escapeHtml(d.original_filename || `Document ${docId}`);
        const subtitle = `${escapeHtml(d.module_owner)} · uploaded ${escapeHtml(d.uploaded_at)}`;
        const active = selectedId === docId;
        const ocr = d.ocr_used ? "OCR" : "native";
        return `
          <div class="row list-row ${active ? "row--active" : ""}" data-doc-id="${docId}">
            <div class="row__left">
              <div class="row__title">${title}</div>
              <div class="row__subtitle">${subtitle}</div>
              <div class="list-row__meta">
                <span>document_id=${escapeHtml(docId)}</span>
                <span>text=${escapeHtml(ocr)}</span>
              </div>
            </div>
            <div class="pill pill--review">in_review</div>
          </div>
        `;
      }),
      "No pending review items."
    );

    // click behavior
    listEl?.querySelectorAll("[data-doc-id]").forEach((el) => {
      el.addEventListener("click", async () => {
        const id = Number(el.getAttribute("data-doc-id"));
        setParam("document_id", id);
        await loadDetail(id, detailEl, detailMetaEl);
        // lightweight active highlight refresh without re-fetching
        listEl.querySelectorAll("[data-doc-id]").forEach((n) => n.classList.remove("row--active"));
        el.classList.add("row--active");
      });
    });

    if (selectedId) {
      await loadDetail(selectedId, detailEl, detailMetaEl);
    } else {
      renderRows(detailEl, [], "Select an item to see details.");
      if (detailMetaEl) detailMetaEl.textContent = "";
    }
  } finally {
    _loading = false;
  }
}

async function loadDetail(documentId, detailEl, detailMetaEl) {
  detailMetaEl.textContent = `document_id=${documentId}`;
  try {
    const payload = await fetchJson(`/api/review-queue/${documentId}`);
    const doc = payload.document || {};
    const review = payload.review || {};

    const warnings = Array.isArray(review.validation_warnings) ? review.validation_warnings : [];
    const warningHtml =
      warnings.length > 0
        ? `
          <div class="row">
            <div class="row__left">
              <div class="row__title">Validation warnings</div>
              <div class="row__subtitle">
                <ul style="margin:6px 0 0 18px; padding:0;">
                  ${warnings.map((w) => `<li>${escapeHtml(w)}</li>`).join("")}
                </ul>
              </div>
            </div>
            <div class="pill pill--review">${warnings.length}</div>
          </div>
        `
        : `<div class="panel__empty">No validation warnings detected.</div>`;

    const redacted = escapeHtml(review.redacted_text || "");
    const redactionCounts = escapeHtml(JSON.stringify(review.redaction_counts || {}));
    const paystub = review.draft_paystub || {};
    const payDate = escapeHtml(paystub.pay_date || "—");
    const periodStart = escapeHtml(paystub.period_start || "—");
    const periodEnd = escapeHtml(paystub.period_end || "—");
    const netPay = paystub.net_pay != null ? escapeHtml(String(paystub.net_pay)) : "—";
    const grossPay = paystub.gross_pay != null ? escapeHtml(String(paystub.gross_pay)) : "—";
    const memberId = paystub.member_id != null ? escapeHtml(String(paystub.member_id)) : "—";
    const lines = Array.isArray(review.draft_lines) ? review.draft_lines : [];

    detailEl.innerHTML = `
      <div class="row">
        <div class="row__left">
          <div class="row__title">${escapeHtml(doc.original_filename || `Document ${documentId}`)}</div>
          <div class="row__subtitle">${escapeHtml(doc.module_owner)} · status ${escapeHtml(doc.status)} · uploaded ${escapeHtml(doc.uploaded_at)}</div>
        </div>
        <div class="pill pill--review">${escapeHtml(doc.status)}</div>
      </div>

      <div class="kv">
        <div class="kv__item">
          <div class="kv__label">Pay date</div>
          <div class="kv__value">${payDate}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Pay period</div>
          <div class="kv__value">${periodStart} → ${periodEnd}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Net pay (draft)</div>
          <div class="kv__value">${escapeHtml(netPay)}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Gross pay (draft)</div>
          <div class="kv__value">${escapeHtml(grossPay)}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">member_id</div>
          <div class="kv__value">${memberId}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Draft lines</div>
          <div class="kv__value">${escapeHtml(String(lines.length))}</div>
        </div>
      </div>

      ${warningHtml}

      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Redaction counts</div>
          <div class="row__subtitle"><code>${redactionCounts}</code></div>
        </div>
      </div>

      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Redacted text (regenerated on read)</div>
          <div class="row__subtitle">
            <div class="codeblock">${redacted || "(empty)"}</div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    renderRows(detailEl, [], `Failed to load review payload: ${escapeHtml(err.message || String(err))}`);
  }
}

load().catch((err) => {
  console.error(err);
  const main = document.querySelector(".main");
  if (main) {
    const div = document.createElement("div");
    div.className = "panel";
    div.innerHTML = `<div class="panel__title">Review Queue failed to load</div><div class="panel__empty">${escapeHtml(
      err.message
    )}</div>`;
    main.prepend(div);
  }
});

// Placeholder (Phase 3+ UI)
