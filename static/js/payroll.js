function escapeHtml(s) {
  return String(s || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

const PAYROLL_LIST_LIMIT = 50;

function formatDate(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return raw;
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function formatDateTime(value) {
  const raw = String(value || "").trim();
  if (!raw) return "—";
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return raw;
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
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

async function postJson(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body || {}),
  });
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

function bindListRowInteractions(listEl, selector, onActivate) {
  if (!listEl) return;
  listEl.querySelectorAll(selector).forEach((el) => {
    if (el.dataset.bound) return;
    el.dataset.bound = "1";
    el.addEventListener("click", () => onActivate(el));
  });
}

function setBanner(kind, title, message) {
  const el = document.getElementById("payroll-status");
  if (!el) return;
  if (!kind) {
    el.innerHTML = "";
    return;
  }
  const bannerClass = kind === "error" ? "banner--error" : kind === "success" ? "banner--success" : "banner--warning";
  el.innerHTML = `
    <div class="banner ${bannerClass}">
      <div class="banner__title">${escapeHtml(title || "Payroll")}</div>
      <div class="banner__body">${escapeHtml(message || "Unknown error")}</div>
    </div>
  `;
}

function clearBanner() {
  setBanner(null);
}

let _flashBanner = null;

function flashBanner(kind, title, message) {
  _flashBanner = { kind, title, message };
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

function extractReasonFromDetails(details) {
  const s = String(details || "");
  const m = s.match(/(?:^|,\\s*)reason=([^,]+)\\s*$/i);
  return m ? String(m[1]).trim() : null;
}

function latestDecisionSummary(auditEvents) {
  const rows = Array.isArray(auditEvents) ? auditEvents : [];
  const interesting = rows.find((e) => {
    const a = String(e?.action || "");
    return a === "payroll_approved" || a === "payroll_rejected" || a === "payroll_reopened";
  });
  if (!interesting) return null;
  const action = String(interesting.action || "");
  const when = formatDateTime(interesting.created_at || "—");
  const actor = String(interesting.actor || "—");
  const reason = extractReasonFromDetails(interesting.details);
  let label = action;
  if (action === "payroll_approved") label = "Approved";
  if (action === "payroll_rejected") label = "Rejected";
  if (action === "payroll_reopened") label = "Reopened";
  return { label, when, actor, reason };
}

function decisionMetadataSummary(latest, paystub) {
  if (!latest) return { has: false, reason: null, decidedAt: null, decisionActor: null };
  const p = paystub || {};
  const decidedAt = p.decided_at ? String(p.decided_at) : null;
  const decisionActor = p.decision_actor ? String(p.decision_actor) : null;
  // Prefer explicit stored rejection_reason when paystub is currently rejected.
  const effective = effectiveStatusLabel(p);
  if (latest.label === "Rejected" && effective === "rejected" && p.rejection_reason) {
    return { has: true, reason: String(p.rejection_reason), decidedAt, decisionActor };
  }
  return { has: true, reason: latest.reason || null, decidedAt, decisionActor };
}

function prettyAuditAction(action) {
  const a = String(action || "");
  if (a === "payroll_ingest_started") return "Ingest started";
  if (a === "payroll_text_extracted") return "Text extracted";
  if (a === "payroll_pii_scrubbed") return "PII scrubbed";
  if (a === "payroll_draft_stored") return "Draft stored";
  if (a === "payroll_ingest_requested") return "Ingest requested";
  if (a === "payroll_ingest_failed") return "Ingest failed";
  if (a === "payroll_approved") return "Approved";
  if (a === "payroll_rejected") return "Rejected";
  if (a === "payroll_reopened") return "Reopened";
  return a || "—";
}

function summarizeAuditDetails(details) {
  const s = String(details || "").trim();
  if (!s) return "";
  let out = s.replace(/\bpaystub_id=\d+\b/gi, "").replace(/\bmember_id=\d+\b/gi, "");
  out = out.replace(/\bfrom_document_status=[^,]+/gi, "").replace(/\bfrom_paystub_status=[^,]+/gi, "");
  out = out.replace(/\s*,\s*/g, " · ").replace(/\s+/g, " ").trim();
  out = out.replace(/^·\s*/g, "").replace(/\s*·\s*$/g, "");
  if (out.length > 160) out = out.slice(0, 157) + "…";
  return out;
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

function renderAuditEvents(events) {
  const rows = Array.isArray(events) ? events : [];
  if (!rows.length) return `<div class="panel__empty">No recent events.</div>`;
  return `<div class="table">
    ${rows
      .slice(0, 12)
      .map((e) => {
        const action = escapeHtml(prettyAuditAction(e.action));
        const when = escapeHtml(formatDateTime(e.created_at || "—"));
        const actor = escapeHtml(e.actor || "—");
        const details = escapeHtml(summarizeAuditDetails(e.details || ""));
        return `
          <div class="row">
            <div class="row__left">
              <div class="row__title">${action}</div>
              <div class="row__subtitle">${when} · ${actor}${details ? ` · ${details}` : ""}</div>
            </div>
            <div class="pill pill--muted">audit</div>
          </div>
        `;
      })
      .join("")}
  </div>`;
}

async function load() {
  const listEl = document.getElementById("payroll-list");
  const detailEl = document.getElementById("payroll-detail");
  const metaEl = document.getElementById("payroll-meta");
  const detailMetaEl = document.getElementById("payroll-detail-meta");
  const memberSel = document.getElementById("payroll-member");
  const statusSel = document.getElementById("payroll-status-filter");

  if (_flashBanner) {
    setBanner(_flashBanner.kind, _flashBanner.title, _flashBanner.message);
    _flashBanner = null;
  } else {
    clearBanner();
  }
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
    params.set("limit", String(PAYROLL_LIST_LIMIT));

    const items = await fetchJson(`/api/payroll/paystubs?${params.toString()}`);
    if (metaEl) metaEl.textContent = `${items.length || 0} paystub(s)`;

    const selectedId = getParamInt("paystub_id") ?? (items[0] ? Number(items[0].id) : null);

    renderRows(
      listEl,
      items.map((p) => {
        const id = Number(p.id);
        const member = escapeHtml(p.member_display_name || `member_id=${p.member_id}`);
        const date = escapeHtml(formatDate(p.pay_date || "—"));
        const net = p.net_pay != null ? escapeHtml(String(p.net_pay)) : "—";
        const effective = effectiveStatusLabel(p);
        const active = selectedId === id;
        return `
          <button type="button" class="row list-row ${active ? "row--active" : ""}" data-paystub-id="${id}">
            <div class="row__left">
              <div class="row__title">${member} · ${date}</div>
              <div class="row__subtitle">net ${net} · paystub_id=${escapeHtml(id)} · document_id=${escapeHtml(p.document_id)}</div>
            </div>
            <div class="pill ${pillClass(effective)}">${escapeHtml(effective)}</div>
          </button>
        `;
      }),
      "🧾 No paystubs"
    );

    bindListRowInteractions(listEl, "[data-paystub-id]", async (el) => {
      const id = Number(el.getAttribute("data-paystub-id"));
      setParam("paystub_id", id);
      await loadDetail(id, detailEl, detailMetaEl);
      listEl.querySelectorAll("[data-paystub-id]").forEach((n) => n.classList.remove("row--active"));
      el.classList.add("row--active");
    });

    if (selectedId) {
      await loadDetail(selectedId, detailEl, detailMetaEl);
    } else {
      renderRows(detailEl, [], "Select a paystub to examine details.");
      if (detailMetaEl) detailMetaEl.textContent = "";
    }
  } catch (e) {
    setBanner("error", "Payroll unavailable", e.message || String(e));
    renderRows(listEl, [], "🧾 No paystubs");
    renderRows(detailEl, [], "Select a paystub");
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
    const audit = Array.isArray(payload.audit_events) ? payload.audit_events : [];
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
          <div class="callout__title">No line items</div>
          <div class="callout__body">No line items stored yet. Check totals.</div>
        </div>`;
    } else if (lines.length < 3) {
      lineHint = `
        <div class="callout callout--info">
          <div class="callout__title">Limited line items</div>
          <div class="callout__body">Only ${escapeHtml(String(lines.length))} stored. Check totals.</div>
        </div>`;
    } else if (lines.length >= 40) {
      lineHint = `
        <div class="callout callout--info">
          <div class="callout__title">Noisy line items</div>
          <div class="callout__body">${escapeHtml(String(lines.length))} stored. Skim for junk rows.</div>
        </div>`;
    }

    const latest = latestDecisionSummary(audit);
    const latestHtml = latest
      ? `
        <div class="row" style="grid-template-columns: 1fr;">
          <div class="row__left">
            <div class="row__title">Latest decision</div>
            <div class="row__subtitle">
              ${escapeHtml(latest.label)} · ${escapeHtml(latest.when)} · ${escapeHtml(latest.actor)}${
                latest.reason ? ` · reason: ${escapeHtml(latest.reason)}` : ""
              }
            </div>
          </div>
          <div class="pill pill--muted">recent</div>
        </div>
      `
      : `
        <div class="row" style="grid-template-columns: 1fr;">
          <div class="row__left">
            <div class="row__title">Latest decision</div>
            <div class="row__subtitle">No decision yet.</div>
          </div>
          <div class="pill pill--muted">—</div>
        </div>
      `;

    const meta = decisionMetadataSummary(latest, p);
    const decisionMetaHtml = meta.has
      ? `
        <div class="row" style="grid-template-columns: 1fr;">
          <div class="row__left">
            <div class="row__title">Decision metadata</div>
            <div class="row__subtitle">
              ${
                meta.decidedAt || meta.decisionActor
                  ? `${meta.decidedAt ? `decided_at ${escapeHtml(meta.decidedAt)}` : "decided_at —"} · ${
                      meta.decisionActor ? `actor ${escapeHtml(meta.decisionActor)}` : "actor —"
                    }<br/>`
                  : ""
              }${meta.reason ? `reason: ${escapeHtml(meta.reason)}` : "No reason recorded for the latest decision."}
            </div>
          </div>
          <div class="pill pill--muted">meta</div>
        </div>
      `
      : ``;

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

      ${latestHtml}

      ${decisionMetaHtml}

      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Recent lifecycle</div>
          <div class="row__subtitle">Most recent audit log events for this document</div>
        </div>
      </div>
      ${renderAuditEvents(audit)}

      ${
        canReopen
          ? `
            <div class="row" style="grid-template-columns: 1fr;">
              <div class="row__left">
                <div class="row__title">Reopen</div>
                <div class="row__subtitle">Move back to review (excluded until re‑approved).</div>
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
          <div class="kv__value">${escapeHtml(formatDate(p.pay_date || "—"))}</div>
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

    const reopenBtn = detailEl?.querySelector("#payroll-reopen");
    if (reopenBtn && !reopenBtn.dataset.bound) {
      reopenBtn.dataset.bound = "1";
      reopenBtn.addEventListener("click", async (e) => {
        const btn = e.currentTarget;
        if (btn && btn.disabled) return;
        const confirmed = window.confirm(
          "Reopen this payroll item into Review Queue? It will be excluded from approved-only analytics until re-approved."
        );
        if (!confirmed) return;
        const reason = window.prompt("Optional reopen reason (stored in audit log):", "") || "";
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Reopening…";
        }
        try {
          await postJson(`/api/review-queue/${encodeURIComponent(String(p.document_id))}/reopen`, {
            reason: reason.trim() ? reason.trim() : null,
          });
          flashBanner("success", "Reopened", "Reopened into Review Queue. It is excluded from approved-only analytics until re-approved.");
          window.location.href = `/review-queue?document_id=${encodeURIComponent(String(p.document_id))}`;
        } catch (err) {
          if (Number(err?.status) === 409) {
            flashBanner(
              "warning",
              "Already changed",
              "State changed. Refreshing…"
            );
            await load();
          } else {
            setBanner("error", "Reopen failed", err.message || String(err));
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Reopen into Review Queue";
            }
          }
        }
      });
    }
  } catch (e) {
    renderRows(detailEl, [], `Failed to load paystub: ${escapeHtml(e.message || String(e))}`);
  }
}

load().catch((err) => {
  console.error(err);
  setBanner("error", "Payroll unavailable", err.message || String(err));
});
