/* Progressive enhancement: without JavaScript every section remains readable. */
(function () {
  'use strict';
  const tabList = document.querySelector('[data-project-tabs]');
  if (!tabList) return;
  const tabs = [...tabList.querySelectorAll('a[href^="#"]')];
  const panels = [...document.querySelectorAll('[data-tab-panel]')];
  if (tabs.length !== panels.length || tabs.length === 0) return;
  const ids = panels.map(panel => panel.id);
  let activeId;
  function hashTarget() {
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch (_) { return null; }
    const target = document.getElementById(id);
    if (!target) return null;
    const panel = target.closest('[data-tab-panel]');
    return panel ? {id: panel.id, target} : null;
  }
  function select(id, {focus = false, updateUrl = false, scroll = false} = {}) {
    if (!ids.includes(id)) return;
    // Measure before hiding anything: collapsing a long panel can clamp the
    // document scroll position. Ordinary tab switches keep their viewport.
    const previous = panels[ids.indexOf(activeId)];
    const startY = window.scrollY;
    const nav = tabList.getBoundingClientRect();
    const previousTop = previous ? previous.getBoundingClientRect().top : nav.bottom;
    const deep = scroll && previous && activeId !== id && previousTop < nav.bottom - 2;
    const destination = deep ? Math.max(0, startY + previousTop - nav.height) : startY;
    tabs.forEach((tab, index) => {
      const active = ids[index] === id;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      panels[index].hidden = !active;
      if (active && focus) tab.focus({preventScroll: true});
    });
    activeId = id;
    if (updateUrl && window.location.hash !== '#' + id) {
      window.history.pushState(null, '', '#' + id);
    }
    if (scroll && (deep || window.scrollY !== destination)) {
      window.scrollTo({top: destination, behavior: 'instant'});
    }
  }
  tabList.setAttribute('role', 'tablist');
  tabList.setAttribute('aria-label', 'Paper sections');
  tabs.forEach((tab, index) => {
    const panel = panels[index];
    tab.id = 'tab-' + panel.id;
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', panel.id);
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', tab.id);
    panel.tabIndex = 0;
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else if (event.key === ' ') next = index;
      else return;
      event.preventDefault();
      select(ids[next], {focus: true, updateUrl: true, scroll: true});
    });
  });
  document.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button > 0) return;
    const link = event.target.closest('a[href^="#"]');
    if (!link) return;
    let id;
    try { id = decodeURIComponent(link.getAttribute('href').slice(1)); } catch (_) { return; }
    if (!ids.includes(id)) return;
    event.preventDefault();
    select(id, {focus: true, updateUrl: true, scroll: true});
  });
  function restore() {
    const target = hashTarget();
    select(target ? target.id : ids[0]);
    if (target && target.target.id !== target.id) target.target.scrollIntoView({block: 'start'});
  }
  window.addEventListener('hashchange', restore);
  window.addEventListener('popstate', restore);
  window.addEventListener('beforeprint', () => panels.forEach(panel => { panel.hidden = false; }));
  window.addEventListener('afterprint', restore);
  restore();
  tabList.classList.add('tabs-ready');
})();
