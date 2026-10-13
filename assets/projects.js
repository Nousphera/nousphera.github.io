(function () {
  'use strict';
  const root = document.documentElement;
  const themeButton = document.querySelector('.theme-toggle');
  const modes = ['auto', 'light', 'dark'];
  function updateThemeButton() {
    if (!themeButton) return;
    const mode = modes.includes(root.dataset.theme) ? root.dataset.theme : 'auto';
    const next = modes[(modes.indexOf(mode) + 1) % modes.length];
    themeButton.querySelector('[data-theme-label]').textContent = {auto: 'Auto', light: 'Light', dark: 'Dark'}[mode];
    const label = `Theme: ${mode === 'auto' ? 'automatic' : mode}. Switch to ${next === 'auto' ? 'automatic' : next} theme.`;
    themeButton.setAttribute('aria-label', label);
    themeButton.title = label;
  }
  if (themeButton) {
    updateThemeButton();
    themeButton.addEventListener('click', () => {
      const mode = modes.includes(root.dataset.theme) ? root.dataset.theme : 'auto';
      const next = modes[(modes.indexOf(mode) + 1) % modes.length];
      root.dataset.theme = next;
      try { localStorage.setItem('nousphera-theme', next); } catch (_) {}
      updateThemeButton();
    });
  }
  const dialog = document.querySelector('.figure-dialog');
  if (dialog && typeof dialog.showModal === 'function') {
    document.querySelectorAll('[data-figure]').forEach(link => {
      link.addEventListener('click', event => {
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        const img = dialog.querySelector('img');
        img.src = link.href;
        img.alt = link.querySelector('img').alt;
        dialog.querySelector('.dialog-caption').textContent = link.dataset.caption;
        dialog.querySelector('.dialog-original').href = link.href;
        dialog.showModal();
        document.body.classList.add('dialog-open');
        dialog.querySelector('[data-close-figure]').focus();
      });
    });
    dialog.querySelector('[data-close-figure]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => document.body.classList.remove('dialog-open'));
  }
  const copyButton = document.querySelector('[data-copy-citation]');
  if (copyButton) {
    copyButton.addEventListener('click', async () => {
      const text = document.querySelector('#bibtex').textContent;
      const label = copyButton.querySelector('span');
      const status = document.querySelector('.copy-status');
      copyButton.setAttribute('aria-busy', 'true');
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(text);
        label.textContent = 'Copied';
        status.textContent = 'Citation copied to clipboard.';
      } catch (_) {
        const range = document.createRange();
        range.selectNodeContents(document.querySelector('#bibtex'));
        const selection = window.getSelection();
        selection.removeAllRanges(); selection.addRange(range);
        label.textContent = 'Selected';
        status.textContent = 'Citation selected. Use your copy shortcut or download the BibTeX file.';
      } finally {
        copyButton.setAttribute('aria-busy', 'false');
        window.setTimeout(() => { label.textContent = 'Copy'; }, 2200);
      }
    });
  }
  const input = document.querySelector('#project-search');
  const cards = [...document.querySelectorAll('.project-card')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  if (input && cards.length) {
    let category = 'all';
    function filterProjects() {
      const terms = input.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => {
        const visible = (category === 'all' || card.dataset.category === category) && terms.every(term => card.dataset.search.includes(term));
        card.hidden = !visible;
        if (visible) count++;
      });
      document.querySelector('#filter-status').textContent = `${count} ${count === 1 ? 'project' : 'projects'}`;
      document.querySelector('.no-results').hidden = count !== 0;
    }
    input.addEventListener('input', filterProjects);
    filters.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.filter;
      filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      filterProjects();
    }));
  }
})();
