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

async function load() {
  const listEl = document.getElementById("rq-list");
  const detailEl = document.getElementById("rq-detail");
  const metaEl = document.getElementById("rq-meta");
  const detailMetaEl = document.getElementById("rq-detail-meta");

  const items = await fetchJson("/api/review-queue");
  metaEl.textContent = `${items.length || 0} item(s)`;

  const selectedId = getParamInt("document_id") ?? (items[0] ? Number(items[0].document_id) : null);

  renderRows(
    listEl,
    items.map((d) => {
      const docId = Number(d.document_id);
      const title = escapeHtml(d.original_filename || `Document ${docId}`);
      const subtitle = `${escapeHtml(d.module_owner)} · uploaded ${escapeHtml(d.uploaded_at)}`;
      const active = selectedId === docId;
      return `
        <div class="row" style="cursor:pointer; ${active ? "border-color: rgba(56,189,248,0.35);" : ""}" data-doc-id="${docId}">
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

  // click behavior
  listEl.querySelectorAll("[data-doc-id]").forEach((el) => {
    el.addEventListener("click", async () => {
      const id = Number(el.getAttribute("data-doc-id"));
      setParam("document_id", id);
      await loadDetail(id, detailEl, detailMetaEl);
      // lightweight "active" highlight refresh
      await load();
    });
  });

  if (selectedId) {
    await loadDetail(selectedId, detailEl, detailMetaEl);
  } else {
    renderRows(detailEl, [], "Select an item to see details.");
    detailMetaEl.textContent = "";
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
        ? `<div class="row"><div class="row__left"><div class="row__title">Validation warnings</div><div class="row__subtitle">${warnings
            .map((w) => escapeHtml(w))
            .join("<br/>")}</div></div><div class="pill pill--review">${warnings.length}</div></div>`
        : `<div class="panel__empty">No validation warnings detected.</div>`;

    const redacted = escapeHtml(review.redacted_text || "");
    const redactionCounts = escapeHtml(JSON.stringify(review.redaction_counts || {}));

    detailEl.innerHTML = `
      <div class="row">
        <div class="row__left">
          <div class="row__title">${escapeHtml(doc.original_filename || `Document ${documentId}`)}</div>
          <div class="row__subtitle">${escapeHtml(doc.module_owner)} · status ${escapeHtml(doc.status)} · uploaded ${escapeHtml(doc.uploaded_at)}</div>
        </div>
        <div class="pill">${escapeHtml(doc.status)}</div>
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
          <div class="row__subtitle" style="white-space: pre-wrap; line-height: 1.35;">${redacted || "(empty)"}</div>
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
