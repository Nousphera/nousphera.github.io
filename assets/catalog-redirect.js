/* Preserve shared filters and history when opening the former catalog URL. */
(function () {
  'use strict';
  window.location.replace('/' + window.location.search + (window.location.hash || '#collection'));
})();
