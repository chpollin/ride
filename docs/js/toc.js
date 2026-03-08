/**
 * Scroll-spy for the sidebar Table of Contents + reading progress bar.
 *
 * Highlights the currently visible section in the TOC and updates the
 * progress bar width based on scroll position within the article.
 */
(function () {
  'use strict';

  var article = document.querySelector('.review-article');
  var progressBar = document.querySelector('.reading-progress-bar');
  var tocLinks = document.querySelectorAll('.sidebar-toc .toc-link');
  if (!article || tocLinks.length === 0) return;

  // Collect section elements that correspond to TOC entries
  var sections = [];
  tocLinks.forEach(function (link) {
    var id = link.getAttribute('href');
    if (id && id.charAt(0) === '#') {
      var el = document.getElementById(id.slice(1));
      if (el) sections.push({ id: id.slice(1), el: el, link: link });
    }
  });

  var activeLink = null;

  function setActive(link) {
    if (link === activeLink) return;
    if (activeLink) activeLink.classList.remove('is-active');
    link.classList.add('is-active');
    activeLink = link;
  }

  function onScroll() {
    // --- Reading progress ---
    if (progressBar) {
      var rect = article.getBoundingClientRect();
      var total = article.scrollHeight - window.innerHeight;
      var scrolled = -rect.top;
      var pct = total > 0 ? Math.min(Math.max(scrolled / total, 0), 1) * 100 : 0;
      progressBar.style.width = pct + '%';
    }

    // --- Scroll-spy ---
    // Find the last section whose top has scrolled past the viewport trigger
    var trigger = window.innerHeight * 0.25;
    var current = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].el.getBoundingClientRect().top <= trigger) {
        current = sections[i];
      }
    }
    if (current) {
      setActive(current.link);
    } else if (sections.length > 0) {
      setActive(sections[0].link);
    }
  }

  // Throttle scroll events to ~60 fps
  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        onScroll();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // Initial state
  onScroll();
})();
