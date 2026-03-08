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

  // --- Score distribution (single-series bar chart) ---
  var scoresEl = document.getElementById('chart-scores');
  if (scoresEl) {
    try {
      var data = JSON.parse(scoresEl.dataset.chart);
      var maxVal = Math.max.apply(null, data.values) || 1;
      var html = '<div class="chart-bars" role="img" aria-label="Score distribution">';
      for (var i = 0; i < data.labels.length; i++) {
        var pct = (data.values[i] / maxVal) * 100;
        html +=
          '<div class="chart-bar-group">' +
            '<div class="chart-bar" style="height:' + pct + '%" ' +
              'title="' + data.labels[i] + ': ' + data.values[i] + '">' +
              '<span class="chart-bar-value">' + data.values[i] + '</span>' +
            '</div>' +
            '<span class="chart-bar-label">' + data.labels[i] + '</span>' +
          '</div>';
      }
      html += '</div>';
      scoresEl.innerHTML = html;
    } catch (e) { /* leave container empty, fallback table is available */ }
  }

  // --- Category breakdown (stacked horizontal bars) ---
  var catEl = document.getElementById('chart-categories');
  if (catEl) {
    try {
      var cdata = JSON.parse(catEl.dataset.chart);
      var chtml = '<div class="chart-stacked" role="img" aria-label="Criteria breakdown">';
      for (var j = 0; j < cdata.labels.length; j++) {
        var total = cdata.yes[j] + cdata.no[j] + cdata.na[j];
        if (total === 0) continue;
        var yesPct = (cdata.yes[j] / total) * 100;
        var noPct = (cdata.no[j] / total) * 100;
        var naPct = (cdata.na[j] / total) * 100;
        chtml +=
          '<div class="chart-stacked-row">' +
            '<span class="chart-stacked-label">' + cdata.labels[j] + '</span>' +
            '<div class="chart-stacked-bar" title="Yes: ' + cdata.yes[j] + ', No: ' + cdata.no[j] + ', N/A: ' + cdata.na[j] + '">' +
              '<div class="chart-seg chart-seg-yes" style="width:' + yesPct.toFixed(1) + '%"></div>' +
              '<div class="chart-seg chart-seg-no" style="width:' + noPct.toFixed(1) + '%"></div>' +
              '<div class="chart-seg chart-seg-na" style="width:' + naPct.toFixed(1) + '%"></div>' +
            '</div>' +
          '</div>';
      }
      chtml += '</div>';
      catEl.innerHTML = chtml;
    } catch (e) { /* fallback table */ }
  }
})();
