/* Run before paint; blocked storage leaves the automatic theme intact. */
(function () {
  'use strict';
  try {
    const theme = localStorage.getItem('nousphera-theme');
    if (['light', 'dark', 'auto'].includes(theme)) document.documentElement.dataset.theme = theme;
  } catch (_) { /* Browser privacy settings may disable storage. */ }
})();
