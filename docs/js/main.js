/* ============================================================
   Icarus Macro Maker – main.js
   Nav active state, mobile menu, smooth scroll, misc
   ============================================================ */

(function () {
  "use strict";

  /* ── Active nav link ──────────────────────────────────────── */
  function setActiveNav() {
    const page = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav__links a").forEach(function (a) {
      const href = a.getAttribute("href");
      a.classList.remove("active");
      if (
        href === page ||
        (page === "" && href === "index.html") ||
        (page === "index.html" && href === "index.html")
      ) {
        a.classList.add("active");
      }
    });
  }

  /* ── Mobile hamburger ─────────────────────────────────────── */
  function initHamburger() {
    var btn = document.querySelector(".nav__hamburger");
    var menu = document.querySelector(".nav__links");
    if (!btn || !menu) return;

    btn.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });

    // Close on outside click
    document.addEventListener("click", function (e) {
      if (!btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.remove("open");
        btn.setAttribute("aria-expanded", false);
      }
    });
  }

  /* ── Smooth-scroll for anchor links ───────────────────────── */
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener("click", function (e) {
        var id = a.getAttribute("href").slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  /* ── Scroll-reveal (simple intersection observer) ─────────── */
  function initReveal() {
    if (!("IntersectionObserver" in window)) return;

    var style = document.createElement("style");
    style.textContent =
      ".reveal{opacity:0;transform:translateY(20px);transition:opacity 0.45s ease,transform 0.45s ease}" +
      ".reveal.visible{opacity:1;transform:none}";
    document.head.appendChild(style);

    var targets = document.querySelectorAll(
      ".card, .dl-card, .yt-card, .step, .cl-version, .feature-block, .stat"
    );

    targets.forEach(function (el) {
      el.classList.add("reveal");
    });

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 }
    );

    targets.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ── Animated count-up for stat numbers ───────────────────── */
  function initCountUp() {
    var stats = document.querySelectorAll(".stat__num[data-count]");
    if (!stats.length) return;
    if (!("IntersectionObserver" in window)) return;

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          var end = parseInt(el.dataset.count, 10);
          var suffix = el.dataset.suffix || "";
          var duration = 900;
          var start = performance.now();
          io.unobserve(el);

          function tick(now) {
            var elapsed = now - start;
            var progress = Math.min(elapsed / duration, 1);
            // ease-out quad
            var eased = 1 - (1 - progress) * (1 - progress);
            el.textContent = Math.round(eased * end) + suffix;
            if (progress < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
        });
      },
      { threshold: 0.5 }
    );

    stats.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ── Copy-to-clipboard for code blocks ────────────────────── */
  function initCopyCode() {
    document.querySelectorAll("pre").forEach(function (pre) {
      var btn = document.createElement("button");
      btn.textContent = "Copy";
      btn.style.cssText =
        "position:absolute;top:10px;right:10px;padding:4px 10px;" +
        "font-size:0.75rem;border-radius:5px;border:1px solid #30363d;" +
        "background:#21262d;color:#8b949e;cursor:pointer;";
      pre.style.position = "relative";
      pre.appendChild(btn);

      btn.addEventListener("click", function () {
        var code = pre.textContent.replace("Copy", "").trim();
        navigator.clipboard.writeText(code).then(function () {
          btn.textContent = "Copied!";
          btn.style.color = "#4FC3F7";
          setTimeout(function () {
            btn.textContent = "Copy";
            btn.style.color = "#8b949e";
          }, 1800);
        });
      });
    });
  }

  /* ── Init ─────────────────────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", function () {
    setActiveNav();
    initHamburger();
    initSmoothScroll();
    initReveal();
    initCountUp();
    initCopyCode();
  });
})();
