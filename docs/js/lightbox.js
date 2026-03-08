/**
 * Image lightbox — click to zoom, keyboard navigation, prev/next.
 *
 * Targets all images inside .review-article figures.  Creates an overlay
 * with close, prev, next buttons and a caption from <figcaption>.
 * Focus is trapped inside the dialog while open.
 */
(function () {
  'use strict';

  var article = document.querySelector('.review-article');
  if (!article) return;

  var images = Array.from(article.querySelectorAll('figure img'));
  if (images.length === 0) return;

  var overlay = null;
  var currentIndex = -1;
  var previousFocus = null;

  function getCaption(img) {
    var figure = img.closest('figure');
    if (!figure) return '';
    var cap = figure.querySelector('figcaption');
    return cap ? cap.textContent : '';
  }

  function getFocusable() {
    if (!overlay) return [];
    return Array.from(overlay.querySelectorAll('button:not([style*="display: none"]), button:not([style*="display:none"])'));
  }

  function trapFocus(e) {
    var focusable = getFocusable();
    if (focusable.length === 0) return;
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (e.key === 'Tab') {
      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
  }

  function open(index) {
    if (currentIndex < 0) {
      previousFocus = document.activeElement;
    }
    currentIndex = index;
    var img = images[index];

    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'lightbox';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-label', 'Image viewer');
      overlay.setAttribute('aria-modal', 'true');
      overlay.innerHTML =
        '<button class="lightbox-close" aria-label="Close">&times;</button>' +
        '<button class="lightbox-nav lightbox-prev" aria-label="Previous">&lsaquo;</button>' +
        '<img src="" alt="">' +
        '<button class="lightbox-nav lightbox-next" aria-label="Next">&rsaquo;</button>' +
        '<div class="lightbox-caption"></div>';

      overlay.querySelector('.lightbox-close').addEventListener('click', close);
      overlay.querySelector('.lightbox-prev').addEventListener('click', function () { navigate(-1); });
      overlay.querySelector('.lightbox-next').addEventListener('click', function () { navigate(1); });
      overlay.addEventListener('click', function (e) {
        if (e.target === overlay) close();
      });

      document.body.appendChild(overlay);
    }

    var lbImg = overlay.querySelector('img');
    lbImg.src = img.src;
    lbImg.alt = img.alt || '';
    overlay.querySelector('.lightbox-caption').textContent = getCaption(img);

    // Show/hide nav buttons
    overlay.querySelector('.lightbox-prev').style.display = images.length > 1 ? '' : 'none';
    overlay.querySelector('.lightbox-next').style.display = images.length > 1 ? '' : 'none';

    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    // Move focus into the dialog
    overlay.querySelector('.lightbox-close').focus();
  }

  function close() {
    if (!overlay) return;
    overlay.style.display = 'none';
    document.body.style.overflow = '';
    currentIndex = -1;

    // Restore focus to the triggering element
    if (previousFocus) {
      previousFocus.focus();
      previousFocus = null;
    }
  }

  function navigate(direction) {
    if (images.length <= 1) return;
    var next = (currentIndex + direction + images.length) % images.length;
    open(next);
  }

  // Click handler on images
  images.forEach(function (img, i) {
    img.style.cursor = 'zoom-in';
    img.addEventListener('click', function () {
      open(i);
    });
  });

  // Keyboard navigation + focus trapping
  document.addEventListener('keydown', function (e) {
    if (currentIndex < 0) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') navigate(-1);
    else if (e.key === 'ArrowRight') navigate(1);
    else trapFocus(e);
  });
})();
