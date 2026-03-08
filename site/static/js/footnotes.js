/**
 * Footnote popovers — hover on desktop, click on mobile.
 *
 * When a footnote reference (sup.footnote-ref > a) is activated, a popover
 * with the footnote content appears below it.  CSS class: .footnote-popover.
 */
(function () {
  'use strict';

  var refs = document.querySelectorAll('.footnote-ref a[href^="#fn-"]');
  if (refs.length === 0) return;

  var currentPopover = null;

  function removePopover() {
    if (currentPopover) {
      currentPopover.remove();
      currentPopover = null;
    }
  }

  function createPopover(ref) {
    var fnId = ref.getAttribute('href').slice(1); // "fn-xxx"
    var fnItem = document.getElementById(fnId);
    if (!fnItem) return;

    removePopover();

    var popover = document.createElement('div');
    popover.className = 'footnote-popover';
    popover.setAttribute('role', 'tooltip');

    // Generate a unique ID for aria-describedby
    var popoverId = 'fn-popover-' + fnId;
    popover.id = popoverId;
    ref.setAttribute('aria-describedby', popoverId);

    // Clone footnote content, removing the backref link
    var clone = fnItem.cloneNode(true);
    var backref = clone.querySelector('.footnote-backref');
    if (backref) backref.remove();
    popover.innerHTML = clone.innerHTML;

    // Position below the reference
    var sup = ref.closest('.footnote-ref') || ref;
    sup.style.position = 'relative';
    sup.appendChild(popover);

    currentPopover = popover;
    return popover;
  }

  // Use hover-capable media query instead of unreliable ontouchstart check
  var canHover = window.matchMedia('(hover: hover)').matches;

  refs.forEach(function (ref) {
    if (canHover) {
      ref.addEventListener('mouseenter', function () {
        createPopover(ref);
      });
      ref.addEventListener('mouseleave', function () {
        removePopover();
      });
    }

    // Click: toggle popover (touch) or follow link to footnote section
    ref.addEventListener('click', function (e) {
      if (!canHover) {
        // On touch devices, first click shows popover, second follows link
        if (currentPopover && currentPopover.parentElement === (ref.closest('.footnote-ref') || ref)) {
          ref.removeAttribute('aria-describedby');
          removePopover();
          // Let the default link behavior happen (scroll to footnote)
          return;
        }
        e.preventDefault();
        createPopover(ref);
      }
    });
  });

  // Close popover on outside click
  document.addEventListener('click', function (e) {
    if (currentPopover && !e.target.closest('.footnote-ref')) {
      removePopover();
    }
  });

  // Close on Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') removePopover();
  });
})();
