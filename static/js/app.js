(() => {
  const STORAGE_KEY = "he-theme";
  const UPLOAD_ENDPOINT = "/api/documents/upload";

  function isValidTheme(v) {
    return v === "light" || v === "dark";
  }

  function getSystemTheme() {
    try {
      return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    } catch {
      return "light";
    }
  }

  function getInitialTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (isValidTheme(stored)) return stored;
    // Default direction is light; system preference is only a fallback.
    return getSystemTheme();
  }

  function applyTheme(theme) {
    const t = isValidTheme(theme) ? theme : "light";
    document.documentElement.setAttribute("data-theme", t);

    const btn = document.getElementById("theme-toggle");
    if (btn) {
      const isDark = t === "dark";
      btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
      btn.setAttribute("title", isDark ? "Light mode" : "Dark mode");
    }
  }

  function setTheme(theme) {
    const t = isValidTheme(theme) ? theme : "light";
    localStorage.setItem(STORAGE_KEY, t);
    applyTheme(t);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "dark" ? "light" : "dark");
  }

  // Apply immediately (avoid flash).
  applyTheme(getInitialTheme());

  // Wire toggle after DOM is ready.
  window.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.addEventListener("click", toggleTheme);

    // Step 14B: responsive nav drawer (small screens).
    const navBtn = document.getElementById("nav-toggle");
    const backdrop = document.getElementById("sidebar-backdrop");
    const sidebar = document.getElementById("sidebar");

    function setNavOpen(open) {
      document.documentElement.classList.toggle("nav-open", Boolean(open));
      if (navBtn) {
        navBtn.setAttribute("aria-expanded", open ? "true" : "false");
        navBtn.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      }
    }

    function isSmallScreen() {
      return window.matchMedia && window.matchMedia("(max-width: 720px)").matches;
    }

    function toggleNav() {
      const open = document.documentElement.classList.contains("nav-open");
      setNavOpen(!open);
      if (!open && sidebar) {
        const firstLink = sidebar.querySelector("a");
        if (firstLink && typeof firstLink.focus === "function") firstLink.focus();
      }
    }

    if (navBtn) navBtn.addEventListener("click", toggleNav);
    if (backdrop) backdrop.addEventListener("click", () => setNavOpen(false));

    // Close drawer on navigation.
    if (sidebar) {
      sidebar.querySelectorAll("a").forEach((a) => {
        a.addEventListener("click", () => {
          if (isSmallScreen()) setNavOpen(false);
        });
      });
    }

    // Escape closes drawer.
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") setNavOpen(false);
    });

    // If we leave small-screen, ensure drawer isn't stuck open.
    window.addEventListener("resize", () => {
      if (!isSmallScreen()) setNavOpen(false);
    });
  });

  // Step 14C: shared upload helper (small, explicit).
  function escapeHtml(s) {
    return String(s || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  async function uploadFile({ file, moduleOwner, memberId, institutionId }) {
    const form = new FormData();
    form.append("file", file);
    form.append("module_owner", moduleOwner);
    if (memberId !== null && memberId !== undefined && String(memberId).trim() !== "") {
      form.append("member_id", String(memberId));
    }
    if (institutionId !== null && institutionId !== undefined && String(institutionId).trim() !== "") {
      form.append("institution_id", String(institutionId));
    }

    const res = await fetch(UPLOAD_ENDPOINT, { method: "POST", body: form });
    const text = await res.text();
    if (!res.ok) throw new Error(text || `Upload failed (${res.status})`);
    try {
      return JSON.parse(text);
    } catch {
      throw new Error("Upload returned non-JSON response");
    }
  }

  function mountUploadSurface(rootEl, options) {
    const cfg = {
      title: options?.title || "Upload",
      help: options?.help || "",
      moduleOwner: options?.moduleOwner,
      accept: options?.accept || "",
      extraFieldsHtml: options?.extraFieldsHtml || "",
      getExtraFields: options?.getExtraFields || (() => ({})),
      onUploaded: options?.onUploaded || (() => {}),
    };

    if (!rootEl) return;
    if (!cfg.moduleOwner) throw new Error("mountUploadSurface requires moduleOwner");

    rootEl.innerHTML = `
      <div class="upload" data-state="idle">
        <div class="upload__head">
          <div class="upload__title">${escapeHtml(cfg.title)}</div>
          <div class="upload__hint">${escapeHtml(cfg.help)}</div>
        </div>

        <div class="upload__fields">${cfg.extraFieldsHtml || ""}</div>

        <div class="upload__drop" role="button" tabindex="0" aria-label="Upload file">
          <div class="upload__dropTitle">Drag & drop a file here</div>
          <div class="upload__dropSubtitle">or <span class="upload__link">choose a file</span></div>
          <div class="upload__types">${escapeHtml(cfg.accept ? `Allowed: ${cfg.accept}` : "")}</div>
          <input class="upload__file" type="file" ${cfg.accept ? `accept="${escapeHtml(cfg.accept)}"` : ""} />
        </div>

        <div class="upload__status" aria-live="polite"></div>
      </div>
    `;

    const wrap = rootEl.querySelector(".upload");
    const drop = rootEl.querySelector(".upload__drop");
    const input = rootEl.querySelector(".upload__file");
    const status = rootEl.querySelector(".upload__status");

    function setState(state, message, tone) {
      wrap?.setAttribute("data-state", state);
      if (!status) return;
      const cls = tone ? `upload__status upload__status--${tone}` : "upload__status";
      status.className = cls;
      status.innerHTML = message ? message : "";
    }

    async function handleFile(file) {
      if (!file) return;
      setState("uploading", `<div class="upload__msg">Uploading <b>${escapeHtml(file.name)}</b>…</div>`, "info");
      try {
        const extras = cfg.getExtraFields ? cfg.getExtraFields(rootEl) : {};
        const payload = await uploadFile({
          file,
          moduleOwner: cfg.moduleOwner,
          memberId: extras.member_id,
          institutionId: extras.institution_id,
        });
        const docId = payload?.document_id;
        setState(
          "success",
          `<div class="upload__msg"><b>Uploaded.</b> document_id=<code>${escapeHtml(docId)}</code></div>`,
          "success"
        );
        cfg.onUploaded?.(payload, rootEl);
      } catch (err) {
        setState("error", `<div class="upload__msg"><b>Upload failed.</b> ${escapeHtml(err.message || String(err))}</div>`, "error");
      }
    }

    function openPicker() {
      if (input) input.click();
    }

    if (drop) {
      drop.addEventListener("click", openPicker);
      drop.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") openPicker();
      });

      ["dragenter", "dragover"].forEach((ev) => {
        drop.addEventListener(ev, (e) => {
          e.preventDefault();
          wrap?.setAttribute("data-state", "dragover");
        });
      });
      ["dragleave", "drop"].forEach((ev) => {
        drop.addEventListener(ev, (e) => {
          e.preventDefault();
          wrap?.setAttribute("data-state", "idle");
        });
      });
      drop.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const file = dt && dt.files && dt.files[0] ? dt.files[0] : null;
        handleFile(file);
      });
    }

    if (input) {
      input.addEventListener("change", () => {
        const file = input.files && input.files[0] ? input.files[0] : null;
        handleFile(file);
      });
    }

    setState("idle", "", null);
  }

  // Expose minimal API for page scripts.
  window.HE = window.HE || {};
  window.HE.mountUploadSurface = mountUploadSurface;
})();
