/**
 * main.js – Molecular Theory Explained
 * Global UI behaviours: navbar toggle, flash message auto-dismiss,
 * accordion fallback (used when learn.html toggleAccordion isn't
 * already defined), and misc helpers.
 */

/* ── Navbar hamburger ─────────────────────────────── */
(function initNavToggle() {
  const toggle = document.getElementById('navToggle');
  const links  = document.getElementById('navLinks');
  if (!toggle || !links) return;

  toggle.addEventListener('click', function () {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });

  // Close menu when a link is clicked
  links.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      links.classList.remove('open');
    });
  });
})();


/* ── Flash message auto-dismiss ──────────────────── */
(function autoFlash() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });
})();


/* ── Accordion (global fallback) ─────────────────── */
// learn.html defines its own toggleAccordion; this is a safe fallback
// so no "undefined function" errors on other pages that may link accordions.
if (typeof window.toggleAccordion === 'undefined') {
  window.toggleAccordion = function (header) {
    var item = header.parentElement;
    var body = item.querySelector('.accordion-body');
    var isOpen = item.classList.contains('open');

    // Close all open items
    document.querySelectorAll('.accordion-item.open').forEach(function (el) {
      el.classList.remove('open');
      el.querySelector('.accordion-body').style.maxHeight = '0';
    });

    // Open clicked item if it was closed
    if (!isOpen) {
      item.classList.add('open');
      body.style.maxHeight = body.scrollHeight + 'px';
    }
  };
}


/* ── Active nav link highlight ───────────────────── */
(function highlightNav() {
  var path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(function (a) {
    if (a.getAttribute('href') === path) {
      a.classList.add('active');
    }
  });
})();
