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

async function postJson(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body || {}),
  });
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

function setBannerError(message) {
  const el = document.getElementById("payroll-status");
  if (!el) return;
  el.innerHTML = `
    <div class="banner banner--error">
      <div class="banner__title">Payroll unavailable</div>
      <div class="banner__body">${escapeHtml(message || "Unknown error")}</div>
    </div>
  `;
}

function clearBanner() {
  const el = document.getElementById("payroll-status");
  if (el) el.innerHTML = "";
}

function skeletonRows(n) {
  return `<div class="skeleton">${Array.from({ length: n })
    .map(() => '<div class="skeleton__line"></div>')
    .join("")}</div>`;
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

function getParamStr(key) {
  const url = new URL(window.location.href);
  const v = url.searchParams.get(key);
  return v == null ? null : String(v);
}

function effectiveStatusLabel(paystub) {
  const ps = String(paystub?.status || "");
  const ds = String(paystub?.document_status || "");
  if (ps === "draft" && ds === "in_review") return "in_review";
  return ps || ds || "—";
}

function pillClass(status) {
  const s = String(status || "");
  if (s === "approved") return "pill--ok";
  if (s === "rejected") return "pill--danger";
  return "pill--review";
}

function parseValidationSummary(raw) {
  if (!raw) return { warnings: [], extraction_source: null };
  try {
    const parsed = JSON.parse(String(raw));
    const warnings = Array.isArray(parsed?.warnings) ? parsed.warnings.map((w) => String(w)) : [];
    const extraction_source =
      typeof parsed?.extraction_source === "string" && parsed.extraction_source.trim() ? parsed.extraction_source.trim() : null;
    return { warnings, extraction_source };
  } catch {
    return { warnings: [], extraction_source: null };
  }
}

async function loadMembers(selectEl) {
  const members = await fetchJson("/api/household/members");
  const options = [
    { id: "", label: "Household (all members)" },
    ...members.map((m) => ({ id: String(m.id), label: `${m.display_name} (id=${m.id})` })),
  ];
  selectEl.innerHTML = options.map((o) => `<option value="${escapeHtml(o.id)}">${escapeHtml(o.label)}</option>`).join("");
  return members;
}

async function load() {
  const listEl = document.getElementById("payroll-list");
  const detailEl = document.getElementById("payroll-detail");
  const metaEl = document.getElementById("payroll-meta");
  const detailMetaEl = document.getElementById("payroll-detail-meta");
  const memberSel = document.getElementById("payroll-member");
  const statusSel = document.getElementById("payroll-status-filter");

  clearBanner();
  if (listEl) listEl.innerHTML = skeletonRows(4);
  if (detailEl) detailEl.innerHTML = skeletonRows(6);
  if (metaEl) metaEl.textContent = "Loading…";
  if (detailMetaEl) detailMetaEl.textContent = "";

  try {
    if (memberSel && memberSel.options.length === 0) {
      await loadMembers(memberSel);
      const initialMember = getParamStr("member_id") || "";
      memberSel.value = initialMember;
      memberSel.addEventListener("change", async () => {
        setParam("member_id", memberSel.value || null);
        setParam("paystub_id", null);
        await load();
      });
    }

    if (statusSel) {
      if (!statusSel.dataset.bound) {
        statusSel.dataset.bound = "1";
        statusSel.addEventListener("change", async () => {
          setParam("status", statusSel.value || null);
          setParam("paystub_id", null);
          await load();
        });
      }
      const initialStatus = getParamStr("status") || "";
      statusSel.value = initialStatus;
    }

    const memberId = memberSel?.value ? Number(memberSel.value) : null;
    const status = statusSel?.value || "";

    const params = new URLSearchParams();
    if (memberId != null) params.set("member_id", String(memberId));
    if (status) params.set("status", status);
    params.set("limit", "200");

    const items = await fetchJson(`/api/payroll/paystubs?${params.toString()}`);
    if (metaEl) metaEl.textContent = `${items.length || 0} paystub(s)`;

    const selectedId = getParamInt("paystub_id") ?? (items[0] ? Number(items[0].id) : null);

    renderRows(
      listEl,
      items.map((p) => {
        const id = Number(p.id);
        const member = escapeHtml(p.member_display_name || `member_id=${p.member_id}`);
        const date = escapeHtml(p.pay_date || "—");
        const net = p.net_pay != null ? escapeHtml(String(p.net_pay)) : "—";
        const effective = effectiveStatusLabel(p);
        const active = selectedId === id;
        return `
          <div class="row list-row ${active ? "row--active" : ""}" data-paystub-id="${id}">
            <div class="row__left">
              <div class="row__title">${member} · ${date}</div>
              <div class="row__subtitle">net ${net} · paystub_id=${escapeHtml(id)} · document_id=${escapeHtml(p.document_id)}</div>
            </div>
            <div class="pill ${pillClass(effective)}">${escapeHtml(effective)}</div>
          </div>
        `;
      }),
      "No payroll paystubs found for the selected view."
    );

    listEl?.querySelectorAll("[data-paystub-id]").forEach((el) => {
      el.addEventListener("click", async () => {
        const id = Number(el.getAttribute("data-paystub-id"));
        setParam("paystub_id", id);
        await loadDetail(id, detailEl, detailMetaEl);
        listEl.querySelectorAll("[data-paystub-id]").forEach((n) => n.classList.remove("row--active"));
        el.classList.add("row--active");
      });
    });

    if (selectedId) {
      await loadDetail(selectedId, detailEl, detailMetaEl);
    } else {
      renderRows(detailEl, [], "Select a paystub to examine details.");
      if (detailMetaEl) detailMetaEl.textContent = "";
    }
  } catch (e) {
    setBannerError(e.message || String(e));
    renderRows(listEl, [], "No payroll paystubs.");
    renderRows(detailEl, [], "No paystub selected.");
    if (metaEl) metaEl.textContent = "";
    if (detailMetaEl) detailMetaEl.textContent = "";
  }
}

async function loadDetail(paystubId, detailEl, detailMetaEl) {
  if (detailMetaEl) detailMetaEl.textContent = `paystub_id=${paystubId}`;
  try {
    const payload = await fetchJson(`/api/payroll/paystubs/${paystubId}`);
    const p = payload.paystub || {};
    const lines = Array.isArray(payload.lines) ? payload.lines : [];
    const vs = parseValidationSummary(p.validation_summary);

    const effective = effectiveStatusLabel(p);
    const member = escapeHtml(p.member_display_name || `member_id=${p.member_id}`);
    const canReopen = effective === "approved" || effective === "rejected";

    let extractionHint = "";
    if (vs.extraction_source === "pdf_ocr_fallback") {
      extractionHint = `
        <div class="callout callout--info">
          <div class="callout__title">Draft text source</div>
          <div class="callout__body">PDF OCR fallback — selectable text was missing or insufficient. Verify fields carefully against the original.</div>
        </div>`;
    } else if (vs.extraction_source === "image_ocr") {
      extractionHint = `
        <div class="callout callout--info">
          <div class="callout__title">Draft text source</div>
          <div class="callout__body">Image OCR — verify fields carefully.</div>
        </div>`;
    } else if (vs.extraction_source === "native_pdf") {
      extractionHint = `
        <div class="callout callout--info">
          <div class="callout__title">Draft text source</div>
          <div class="callout__body">Native PDF text extraction.</div>
        </div>`;
    }

    let lineHint = "";
    if (lines.length === 0) {
      lineHint = `
        <div class="callout callout--info">
          <div class="callout__title">Line detail is missing</div>
          <div class="callout__body">No payroll lines are stored for this paystub yet. Totals may require closer review.</div>
        </div>`;
    } else if (lines.length < 3) {
      lineHint = `
        <div class="callout callout--info">
          <div class="callout__title">Line detail is limited</div>
          <div class="callout__body">Only ${escapeHtml(String(lines.length))} line item(s) are stored. Totals may require closer review.</div>
        </div>`;
    } else if (lines.length >= 40) {
      lineHint = `
        <div class="callout callout--info">
          <div class="callout__title">Line detail may be noisy</div>
          <div class="callout__body">${escapeHtml(String(lines.length))} lines are stored. Large tables sometimes include extra rows; skim for obvious junk.</div>
        </div>`;
    }

    detailEl.innerHTML = `
      <div class="row">
        <div class="row__left">
          <div class="row__title">${member}</div>
          <div class="row__subtitle">document_id=${escapeHtml(p.document_id)} · paystub_id=${escapeHtml(p.id)}</div>
        </div>
        <div class="pill ${pillClass(effective)}">${escapeHtml(effective)}</div>
      </div>

      ${extractionHint}
      ${lineHint}

      ${
        canReopen
          ? `
            <div class="row" style="grid-template-columns: 1fr;">
              <div class="row__left">
                <div class="row__title">Reopen</div>
                <div class="row__subtitle">Move this paystub back into review (removes it from approved-only analytics until re-approved).</div>
              </div>
              <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
                <button class="icon-button" type="button" id="payroll-reopen">Reopen into Review Queue</button>
              </div>
            </div>
          `
          : ``
      }

      ${
        effective === "rejected" && p.rejection_reason
          ? `
            <div class="row" style="grid-template-columns: 1fr;">
              <div class="row__left">
                <div class="row__title">Rejection reason</div>
                <div class="row__subtitle">${escapeHtml(String(p.rejection_reason))}</div>
              </div>
            </div>
          `
          : ``
      }

      <div class="kv">
        <div class="kv__item">
          <div class="kv__label">Pay date</div>
          <div class="kv__value">${escapeHtml(p.pay_date || "—")}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Pay period</div>
          <div class="kv__value">${escapeHtml(p.period_start || "—")} → ${escapeHtml(p.period_end || "—")}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Gross pay</div>
          <div class="kv__value">${p.gross_pay != null ? escapeHtml(String(p.gross_pay)) : "—"}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Net pay</div>
          <div class="kv__value">${p.net_pay != null ? escapeHtml(String(p.net_pay)) : "—"}</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Member</div>
          <div class="kv__value">${member} (${escapeHtml(String(p.member_id || "—"))})</div>
        </div>
        <div class="kv__item">
          <div class="kv__label">Source file</div>
          <div class="kv__value">${escapeHtml(p.document_original_filename || "—")}</div>
        </div>
      </div>

      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Lines</div>
          <div class="row__subtitle">${escapeHtml(String(lines.length))} line(s)</div>
        </div>
      </div>

      ${
        lines.length
          ? `<div class="table">
              ${lines
                .slice(0, 200)
                .map(
                  (ln) => `
                    <div class="row">
                      <div class="row__left">
                        <div class="row__title">${escapeHtml(ln.description)}</div>
                        <div class="row__subtitle">${escapeHtml(ln.category)}</div>
                      </div>
                      <div class="pill pill--muted">${escapeHtml(String(ln.amount))}</div>
                    </div>
                  `
                )
                .join("")}
            </div>`
          : `<div class="panel__empty">No payroll lines are stored yet (draft heuristic ingest).</div>`
      }
    `;

    const reopenBtn = document.getElementById("payroll-reopen");
    if (reopenBtn && !reopenBtn.dataset.bound) {
      reopenBtn.dataset.bound = "1";
      reopenBtn.addEventListener("click", async () => {
        const reason = window.prompt("Optional reopen reason (stored in audit log):", "") || "";
        try {
          await postJson(`/api/review-queue/${encodeURIComponent(String(p.document_id))}/reopen`, {
            reason: reason.trim() ? reason.trim() : null,
          });
          window.location.href = `/review-queue?document_id=${encodeURIComponent(String(p.document_id))}`;
        } catch (err) {
          setBannerError(err.message || String(err));
        }
      });
    }
  } catch (e) {
    renderRows(detailEl, [], `Failed to load paystub: ${escapeHtml(e.message || String(e))}`);
  }
}

load().catch((err) => {
  console.error(err);
  setBannerError(err.message || String(err));
});
