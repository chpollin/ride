/**
 * Image lightbox — click to zoom, keyboard navigation, prev/next.
 *
 * Targets all images inside .review-article figures.  Creates an overlay
 * with close, prev, next buttons and a caption from <figcaption>.
 */
(function () {
  'use strict';

  var article = document.querySelector('.review-article');
  if (!article) return;

  var images = Array.from(article.querySelectorAll('figure img'));
  if (images.length === 0) return;

  var overlay = null;
  var currentIndex = -1;

  function getCaption(img) {
    var figure = img.closest('figure');
    if (!figure) return '';
    var cap = figure.querySelector('figcaption');
    return cap ? cap.textContent : '';
  }

  function open(index) {
    currentIndex = index;
    var img = images[index];

    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'lightbox';
      overlay.setAttribute('role', 'dialog');
      overlay.setAttribute('aria-label', 'Image viewer');
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
  }

  function close() {
    if (!overlay) return;
    overlay.style.display = 'none';
    document.body.style.overflow = '';
    currentIndex = -1;
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

  // Keyboard navigation
  document.addEventListener('keydown', function (e) {
    if (currentIndex < 0) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') navigate(-1);
    else if (e.key === 'ArrowRight') navigate(1);
  });
})();
