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

  // Desktop: show on hover
  var isTouchDevice = 'ontouchstart' in window;

  refs.forEach(function (ref) {
    if (!isTouchDevice) {
      ref.addEventListener('mouseenter', function () {
        createPopover(ref);
      });
      ref.addEventListener('mouseleave', function () {
        removePopover();
      });
    }

    // Click: toggle popover (mobile) or follow link to footnote section
    ref.addEventListener('click', function (e) {
      if (isTouchDevice) {
        // On mobile, first click shows popover, second follows link
        if (currentPopover && currentPopover.parentElement === (ref.closest('.footnote-ref') || ref)) {
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
