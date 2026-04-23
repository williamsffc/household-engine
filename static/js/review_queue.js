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
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : "{}",
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
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.addEventListener("click", () => onActivate(el));
    el.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      onActivate(el);
    });
  });
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

function setBanner(kind, title, message) {
  const el = document.getElementById("rq-status");
  if (!el) return;
  if (!kind) {
    el.innerHTML = "";
    return;
  }
  const bannerClass = kind === "error" ? "banner--error" : kind === "success" ? "banner--success" : "banner--warning";
  el.innerHTML = `
    <div class="banner ${bannerClass}">
      <div class="banner__title">${escapeHtml(title || "Review")}</div>
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

function _safeLocalStorageGet(key) {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function _safeLocalStorageSet(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch {
    // ignore
  }
}

async function loadHouseholdMembers() {
  return await fetchJson("/api/household/members");
}

function renderAuditEvents(events) {
  const rows = Array.isArray(events) ? events : [];
  if (!rows.length) return `<div class="panel__empty">No recent events.</div>`;
  return `<div class="table">
    ${rows
      .slice(0, 12)
      .map((e) => {
        const action = escapeHtml(prettyAuditAction(e.action));
        const when = escapeHtml(e.created_at || "—");
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
  const when = String(interesting.created_at || "—");
  const actor = String(interesting.actor || "—");
  const reason = extractReasonFromDetails(interesting.details);
  let label = action;
  if (action === "payroll_approved") label = "Approved";
  if (action === "payroll_rejected") label = "Rejected";
  if (action === "payroll_reopened") label = "Reopened";
  return { label, when, actor, reason };
}

function decisionMetadataSummary(latest) {
  if (!latest) return { has: false, reason: null };
  return { has: true, reason: latest.reason || null };
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
        help: "Upload a paystub (PDF or image). Draft payroll doesn’t affect analytics until approved.",
        moduleOwner: "payroll",
        accept: ".pdf,.png,.jpg,.jpeg",
        extraFieldsHtml: `
          <div class="upload__field">
            <div class="upload__label">Member (required)</div>
            <select class="upload__input" id="payroll-member-id" style="min-width:240px;"></select>
            <div class="upload__label" id="payroll-member-hint">Who is this paystub for?</div>
          </div>
          <div class="upload__field">
            <div class="upload__label">After upload</div>
            <label class="upload__label" style="display:flex; gap:8px; align-items:center;">
              <input type="checkbox" id="payroll-auto-ingest" checked />
              Run draft ingest (moves to <code>in_review</code>)
            </label>
          </div>
        `,
        getExtraFields: (root) => {
          const memberId = root.querySelector("#payroll-member-id")?.value;
          const auto = root.querySelector("#payroll-auto-ingest")?.checked;
          if (!memberId || String(memberId).trim() === "") {
            throw new Error("Select a household member for this payroll upload.");
          }
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

      // Populate member picker (Step 17).
      (async () => {
        try {
          const root = uploadHost;
          const sel = root.querySelector("#payroll-member-id");
          const hint = root.querySelector("#payroll-member-hint");
          if (!sel) return;

          sel.innerHTML = `<option value="">Loading members…</option>`;
          const members = await loadHouseholdMembers();
          const stored = _safeLocalStorageGet("he-payroll-upload-member-id");
          sel.innerHTML =
            `<option value="">Select member…</option>` +
            (members || [])
              .map((m) => `<option value="${escapeHtml(m.id)}">${escapeHtml(m.display_name)} (id=${escapeHtml(m.id)})</option>`)
              .join("");

          if (stored && Array.from(sel.options).some((o) => String(o.value) === String(stored))) {
            sel.value = String(stored);
          } else if (members && members.length === 1) {
            sel.value = String(members[0].id);
          }

          const updateHint = () => {
            const v = String(sel.value || "");
            const opt = sel.options && sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex] : null;
            const name = opt && v ? String(opt.textContent || "").split(" (id=")[0] : "";
            if (hint) {
              hint.textContent = v ? `For: ${name || `member_id=${v}`}` : "Who is this paystub for?";
            }
            if (v) _safeLocalStorageSet("he-payroll-upload-member-id", v);
          };

          sel.addEventListener("change", updateHint);
          updateHint();
        } catch (e) {
          // Keep upload usable even if member list can't load; user will see validation error on upload.
          const sel = uploadHost.querySelector("#payroll-member-id");
          const hint = uploadHost.querySelector("#payroll-member-hint");
          if (sel) sel.innerHTML = `<option value="">(Failed to load members)</option>`;
          if (hint) hint.textContent = "Member list unavailable. Try again, or check /api/household/members.";
        }
      })();
    }

    const listEl = document.getElementById("rq-list");
    const detailEl = document.getElementById("rq-detail");
    const metaEl = document.getElementById("rq-meta");
    const detailMetaEl = document.getElementById("rq-detail-meta");

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

    let items = [];
    try {
      items = await fetchJson("/api/review-queue");
    } catch (e) {
      setBanner("error", "Review unavailable", e.message || String(e));
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
      "Nothing to review"
    );

    // click behavior
    bindListRowInteractions(listEl, "[data-doc-id]", async (el) => {
      const id = Number(el.getAttribute("data-doc-id"));
      setParam("document_id", id);
      await loadDetail(id, detailEl, detailMetaEl);
      // lightweight active highlight refresh without re-fetching
      listEl.querySelectorAll("[data-doc-id]").forEach((n) => n.classList.remove("row--active"));
      el.classList.add("row--active");
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
  if (detailMetaEl) detailMetaEl.textContent = `document_id=${documentId}`;
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
    const canDecide = String(doc.status) === "in_review" && String(paystub.status) === "draft";

    const exSrc = review.extraction_source ? String(review.extraction_source) : "";
    let extractionCallout = "";
    if (exSrc === "pdf_ocr_fallback") {
      extractionCallout = `
        <div class="callout callout--info">
          <div class="callout__title">Text source</div>
          <div class="callout__body">PDF OCR fallback — selectable text was missing or insufficient. Draft may be noisy; verify all fields against the original.</div>
        </div>`;
    } else if (exSrc === "image_ocr") {
      extractionCallout = `
        <div class="callout callout--info">
          <div class="callout__title">Text source</div>
          <div class="callout__body">Image OCR — verify all fields carefully.</div>
        </div>`;
    } else if (exSrc === "native_pdf") {
      extractionCallout = `
        <div class="callout callout--info">
          <div class="callout__title">Text source</div>
          <div class="callout__body">Native PDF text extraction.</div>
        </div>`;
    }

    let lineDetailCallout = "";
    if (lines.length === 0) {
      lineDetailCallout = `
        <div class="callout callout--info">
          <div class="callout__title">No line items</div>
          <div class="callout__body">No line items extracted. Check fields against the original.</div>
        </div>`;
    } else if (lines.length < 3) {
      lineDetailCallout = `
        <div class="callout callout--info">
          <div class="callout__title">Limited line items</div>
          <div class="callout__body">Only ${escapeHtml(String(lines.length))} extracted. Check totals.</div>
        </div>`;
    } else if (lines.length >= 40) {
      lineDetailCallout = `
        <div class="callout callout--info">
          <div class="callout__title">Noisy line items</div>
          <div class="callout__body">${escapeHtml(String(lines.length))} extracted. Skim for junk rows.</div>
        </div>`;
    }

    const artifactMeta = review.artifact_meta || {};
    const artifactWarning = review.artifact_warning ? String(review.artifact_warning) : "";
    const artifactWarningHtml = artifactWarning
      ? `
        <div class="callout callout--info">
          <div class="callout__title">Review artifact note</div>
          <div class="callout__body">${escapeHtml(artifactWarning)}</div>
        </div>`
      : "";
    const artifactMetaHtml = `
      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Review artifact</div>
          <div class="row__subtitle">
            source ${escapeHtml(String(artifactMeta.source || "—"))} · text_chars ${escapeHtml(String(artifactMeta.text_chars ?? "—"))} · ocr_used_for_review ${escapeHtml(String(artifactMeta.ocr_used_for_review ?? "—"))}
          </div>
        </div>
      </div>
    `;

    const auditHtml = `
      <div class="row" style="grid-template-columns: 1fr;">
        <div class="row__left">
          <div class="row__title">Recent lifecycle</div>
          <div class="row__subtitle">Most recent audit log events for this document</div>
        </div>
      </div>
      ${renderAuditEvents(review.audit_events)}
    `;

    const latest = latestDecisionSummary(review.audit_events);
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

    const meta = decisionMetadataSummary(latest);
    const decisionMetaHtml = meta.has
      ? `
        <div class="row" style="grid-template-columns: 1fr;">
          <div class="row__left">
            <div class="row__title">Decision metadata</div>
            <div class="row__subtitle">${
              meta.reason ? `reason: ${escapeHtml(meta.reason)}` : "No reason recorded for the latest decision."
            }</div>
          </div>
          <div class="pill pill--muted">meta</div>
        </div>
      `
      : ``;

    detailEl.innerHTML = `
      <div class="row">
        <div class="row__left">
          <div class="row__title">${escapeHtml(doc.original_filename || `Document ${documentId}`)}</div>
          <div class="row__subtitle">${escapeHtml(doc.module_owner)} · status ${escapeHtml(doc.status)} · uploaded ${escapeHtml(doc.uploaded_at)} · text ${escapeHtml(doc.ocr_used ? "OCR" : "native")}</div>
        </div>
        <div class="pill pill--review">${escapeHtml(doc.status)}</div>
      </div>

      ${extractionCallout}

      ${lineDetailCallout}

      ${artifactWarningHtml}

      ${artifactMetaHtml}

      ${latestHtml}

      ${decisionMetaHtml}

      ${auditHtml}

      ${
        canDecide
          ? `
            <div class="row" style="grid-template-columns: 1fr;">
              <div class="row__left">
                <div class="row__title">Decision</div>
                <div class="row__subtitle" style="display:flex; gap:10px; flex-wrap:wrap; margin-top:6px;">
                  <button class="icon-button icon-button--primary" id="rq-approve" type="button">Approve</button>
                  <button class="icon-button icon-button--danger" id="rq-reject" type="button">Reject</button>
                  <span style="color:var(--color-text-muted);">Draft payroll is excluded until approved.</span>
                </div>
              </div>
            </div>
          `
          : `
            <div class="panel__empty">Not eligible (must be <code>in_review</code> + draft).</div>
          `
      }

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

    if (canDecide) {
      detailEl.querySelector("#rq-approve")?.addEventListener("click", async (e) => {
        const btn = e.currentTarget;
        if (btn && btn.disabled) return;
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Approving…";
        }
        try {
          await postJson(`/api/review-queue/${documentId}/approve`, {});
          setParam("document_id", null);
          flashBanner("success", "Approved", "Moved out of Review Queue.");
          await load();
        } catch (e) {
          if (Number(e?.status) === 409) {
            flashBanner("warning", "Already decided", "State changed. Refreshing…");
            setParam("document_id", null);
            await load();
          } else {
            setBanner("error", "Approve failed", e.message || String(e));
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Approve";
            }
          }
        }
      });

      detailEl.querySelector("#rq-reject")?.addEventListener("click", async (e) => {
        const btn = e.currentTarget;
        if (btn && btn.disabled) return;
        const reason = window.prompt("Reject reason (optional):", "") || "";
        if (btn) {
          btn.disabled = true;
          btn.textContent = "Rejecting…";
        }
        try {
          await postJson(`/api/review-queue/${documentId}/reject`, reason.trim() ? { reason: reason.trim() } : {});
          setParam("document_id", null);
          flashBanner("success", "Rejected", "Moved out of Review Queue.");
          await load();
        } catch (e) {
          if (Number(e?.status) === 409) {
            flashBanner("warning", "Already decided", "State changed. Refreshing…");
            setParam("document_id", null);
            await load();
          } else {
            setBanner("error", "Reject failed", e.message || String(e));
            if (btn) {
              btn.disabled = false;
              btn.textContent = "Reject";
            }
          }
        }
      });
    }
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
