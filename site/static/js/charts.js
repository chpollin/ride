/**
 * Data page charts — renders bar charts from JSON in data-chart attributes.
 *
 * Uses pure CSS/HTML bars (no external chart library) so the page works
 * without JavaScript too (fallback tables are in the template).
 *
 * Expected data-chart JSON formats:
 *   #chart-scores:     { labels: [...], values: [...] }
 *   #chart-categories: { labels: [...], yes: [...], no: [...], na: [...] }
 */
(function () {
  'use strict';

  // Safely set text content without innerHTML XSS risk
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  // --- Score distribution (single-series bar chart) ---
  var scoresEl = document.getElementById('chart-scores');
  if (scoresEl) {
    try {
      var data = JSON.parse(scoresEl.dataset.chart);
      var maxVal = Math.max(1, Math.max.apply(null, data.values));
      var wrapper = el('div', 'chart-bars');
      wrapper.setAttribute('role', 'img');
      wrapper.setAttribute('aria-label', 'Score distribution');

      for (var i = 0; i < data.labels.length; i++) {
        var pct = (data.values[i] / maxVal) * 100;
        var group = el('div', 'chart-bar-group');
        var bar = el('div', 'chart-bar');
        bar.style.height = pct + '%';
        bar.title = data.labels[i] + ': ' + data.values[i];
        bar.appendChild(el('span', 'chart-bar-value', data.values[i]));
        group.appendChild(bar);
        group.appendChild(el('span', 'chart-bar-label', data.labels[i]));
        wrapper.appendChild(group);
      }

      scoresEl.textContent = '';
      scoresEl.appendChild(wrapper);
    } catch (e) {
      console.warn('chart-scores error:', e);
    }
  }

  // --- Category breakdown (stacked horizontal bars) ---
  var catEl = document.getElementById('chart-categories');
  if (catEl) {
    try {
      var cdata = JSON.parse(catEl.dataset.chart);
      var stacked = el('div', 'chart-stacked');
      stacked.setAttribute('role', 'img');
      stacked.setAttribute('aria-label', 'Criteria breakdown');

      for (var j = 0; j < cdata.labels.length; j++) {
        var total = cdata.yes[j] + cdata.no[j] + cdata.na[j];
        if (total === 0) continue;
        var yesPct = ((cdata.yes[j] / total) * 100).toFixed(1);
        var noPct = ((cdata.no[j] / total) * 100).toFixed(1);
        var naPct = ((cdata.na[j] / total) * 100).toFixed(1);

        var row = el('div', 'chart-stacked-row');
        row.appendChild(el('span', 'chart-stacked-label', cdata.labels[j]));

        var barContainer = el('div', 'chart-stacked-bar');
        barContainer.title = 'Yes: ' + cdata.yes[j] + ', No: ' + cdata.no[j] + ', N/A: ' + cdata.na[j];

        var segYes = el('div', 'chart-seg chart-seg-yes');
        segYes.style.width = yesPct + '%';
        var segNo = el('div', 'chart-seg chart-seg-no');
        segNo.style.width = noPct + '%';
        var segNa = el('div', 'chart-seg chart-seg-na');
        segNa.style.width = naPct + '%';

        barContainer.appendChild(segYes);
        barContainer.appendChild(segNo);
        barContainer.appendChild(segNa);
        row.appendChild(barContainer);
        stacked.appendChild(row);
      }

      catEl.textContent = '';
      catEl.appendChild(stacked);
    } catch (e) {
      console.warn('chart-categories error:', e);
    }
  }
})();
