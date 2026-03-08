/**
 * Dark/light mode toggle with localStorage persistence.
 *
 * The initial theme is set inline in base.html (prevents flash of wrong
 * theme).  This script wires up the toggle button and keeps state in sync.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'theme';
  var btn = document.querySelector('.theme-toggle');
  if (!btn) return;

  function currentTheme() {
    return document.documentElement.dataset.theme || 'light';
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    localStorage.setItem(STORAGE_KEY, theme);
  }

  btn.addEventListener('click', function () {
    applyTheme(currentTheme() === 'dark' ? 'light' : 'dark');
  });

  // Sync aria-pressed on load (theme was set by inline script)
  btn.setAttribute('aria-pressed', currentTheme() === 'dark' ? 'true' : 'false');
})();
