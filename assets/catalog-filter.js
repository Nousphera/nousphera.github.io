/* Progressive, shareable filtering: every paper remains in the static HTML. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else { root.ResearchCatalog = api; api.init(); }
})(typeof globalThis === 'object' ? globalThis : this, function () {
  'use strict';
  const normalize = value => String(value || '').normalize('NFKD').replace(/\p{M}/gu, '').toLowerCase().replace(/[^\p{L}\p{N}]+/gu, ' ').trim();
  function readState(search, areas) {
    const params = new URLSearchParams(search);
    const area = params.get('area') || params.get('topic');
    return {area: areas.includes(area) ? area : 'all', query: params.get('q') || ''};
  }
  function writeState(search, state) {
    const params = new URLSearchParams(search);
    params.delete('topic');
    for (const [key, value] of [['area', state.area], ['q', state.query]]) {
      if (value && (key !== 'area' || value !== 'all')) params.set(key, value);
      else params.delete(key);
    }
    return params.size ? '?' + params.toString() : '';
  }
  function matches(record, state) {
    if (state.area !== 'all' && !record.areas.includes(state.area)) return false;
    const text = normalize(record.search), query = normalize(state.query);
    if (!query) return true;
    const words = text.split(/\s+/), terms = query.split(/\s+/);
    return terms.every(term => words.some(word => word.startsWith(term))) ||
      (query.replace(/ /g, '').length >= 3 && text.replace(/ /g, '').includes(query.replace(/ /g, '')));
  }
  function filterRecords(records, state) {
    const visible = records.filter(record => matches(record, state));
    const years = {};
    for (const record of visible) years[record.year] = (years[record.year] || 0) + 1;
    return {visible, years};
  }
  function init(doc = document, win = window) {
    const collection = doc.querySelector('[data-unified-catalog]');
    if (!collection || collection.dataset.ready) return;
    const input = collection.querySelector('#catalog-search');
    const filters = [...collection.querySelectorAll('[data-filter]')];
    if (!input || !filters.length) return;
    collection.dataset.ready = 'true';
    const areas = filters.map(button => button.dataset.filter);
    const groups = [...collection.querySelectorAll('[data-project-year]')];
    const records = groups.flatMap(group => [...group.querySelectorAll('[data-project]')].map(element => ({element, year: group.dataset.projectYear, areas: element.dataset.areas.split(/\s+/), search: element.dataset.search})));
    const status = collection.querySelector('#catalog-status');
    const reset = collection.querySelector('[data-reset-projects]');
    const empty = collection.querySelector('.catalog-empty');
    const links = [...collection.querySelectorAll('[data-year-link]')];
    let state = readState(win.location.search, areas);
    function render(historyMode) {
      const result = filterRecords(records, state), visible = new Set(result.visible);
      records.forEach(record => { record.element.hidden = !visible.has(record); });
      groups.forEach(group => {
        const count = result.years[group.dataset.projectYear] || 0;
        group.hidden = count === 0;
        group.dataset.visibleCount = String(count);
        group.querySelector('[data-year-count]').textContent = String(count).padStart(2, '0');
      });
      links.forEach(link => { link.hidden = !result.years[link.dataset.yearLink]; });
      filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === state.area)));
      if (input.value !== state.query) input.value = state.query;
      status.textContent = result.visible.length === records.length ? records.length + ' projects' : result.visible.length + ' of ' + records.length + ' projects';
      empty.hidden = result.visible.length > 0;
      reset.hidden = state.area === 'all' && !state.query;
      if (historyMode) {
        const url = win.location.pathname + writeState(win.location.search, state) + win.location.hash;
        try { win.history[historyMode + 'State'](win.history.state, '', url); } catch (_) { /* file previews still filter */ }
      }
    }
    const clear = () => { state = {area: 'all', query: ''}; render('push'); input.focus({preventScroll:true}); };
    filters.forEach(button => button.addEventListener('click', () => {
      if (state.area === button.dataset.filter) return;
      state.area = button.dataset.filter; render('push');
    }));
    input.addEventListener('input', () => { state.query = input.value; render('replace'); });
    input.addEventListener('keydown', event => {
      if (event.key === 'Escape' && state.query) { event.preventDefault(); state.query = ''; render('replace'); }
    });
    reset.addEventListener('click', clear);
    collection.querySelector('[data-empty-reset]').addEventListener('click', clear);
    win.addEventListener('popstate', () => { state = readState(win.location.search, areas); render(); });
    win.addEventListener('pageshow', () => { state = readState(win.location.search, areas); render(); });
    collection.querySelector('.catalog-filters').hidden = false;
    input.disabled = false;
    render();
    return {render};
  }
  return {normalize, readState, writeState, matches, filterRecords, init};
});
