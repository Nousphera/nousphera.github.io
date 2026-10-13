const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const asset = name => fs.readFileSync(path.join(__dirname, '..', 'assets', name), 'utf8');
function node(dataset = {}) {
  return {dataset, attributes: {}, hidden: false, value: '', textContent: '', handlers: {},
    addEventListener(name, fn) { this.handlers[name] = fn; },
    setAttribute(name, value) { this.attributes[name] = value; },
    querySelector() { return this.label; }};
}
function setup({theme, blocked = false, filter = false, clipboard = false} = {}) {
  const root = node(theme ? {theme} : {});
  const themeButton = node(); themeButton.label = node();
  const search = node(); const status = node(); const empty = node();
  const cards = [node({category: 'Efficient learning', search: 'ae-psl activation compression autoencoder'}), node({category: 'Private learning', search: 'enccluster encryption compression'})];
  const filters = [node({filter: 'all'}), node({filter: 'Efficient learning'}), node({filter: 'Private learning'})];
  const copyButton = node(); copyButton.label = node();
  const bibtex = node(); bibtex.textContent = '@article{test, year={2026}}';
  const copyStatus = node(); let selected = false; let copied;
  const map = {'.theme-toggle': themeButton, '#project-search': filter ? search : null, '#filter-status': status, '.no-results': empty, '[data-copy-citation]': clipboard ? copyButton : null, '#bibtex': bibtex, '.copy-status': copyStatus};
  const storage = {};
  const context = {document: {documentElement: root, querySelector: key => map[key] || null, querySelectorAll: key => key === '.project-card' ? (filter ? cards : []) : key === '[data-filter]' ? filters : [], createRange: () => ({selectNodeContents(n) { assert.equal(n, bibtex); }})},
    localStorage: {getItem() {if (blocked) throw Error('Denied'); return theme;}, setItem(k,v) {if (blocked) throw Error('Denied'); storage[k] = v;}},
    navigator: clipboard === 'success' ? {clipboard: {async writeText(value) {copied = value;}}} : {},
    window: {getSelection: () => ({removeAllRanges() {}, addRange() {selected = true;}}), setTimeout() {}}};
  vm.runInNewContext(asset('projects.js'), context);
  return {root, themeButton, storage, context, search, status, empty, cards, filters, copyButton, copyStatus, selected: () => selected, copied: () => copied};
}
test('theme cycle works when storage is disabled', () => {
  const s = setup({blocked: true});
  vm.runInNewContext(asset('theme.js'), s.context);
  assert.equal(s.themeButton.label.textContent, 'Auto');
  for (const mode of ['light', 'dark', 'auto']) {
    s.themeButton.handlers.click(); assert.equal(s.root.dataset.theme, mode);
  }
});
test('valid saved theme is restored before paint; unknown settings are ignored', () => {
  const s = setup({theme: 'dark'});
  vm.runInNewContext(asset('theme.js'), s.context);
  assert.equal(s.root.dataset.theme, 'dark');
  s.context.localStorage.getItem = () => 'unknown';
  s.root.dataset = {};
  vm.runInNewContext(asset('theme.js'), s.context);
  assert.equal(s.root.dataset.theme, undefined);
});
test('multiword search intersects category and supports clearing', () => {
  const s = setup({filter: true});
  s.search.value = 'compression autoencoder'; s.search.handlers.input();
  assert.deepEqual(s.cards.map(x => x.hidden), [false, true]);
  s.filters[2].handlers.click();
  assert.deepEqual(s.cards.map(x => x.hidden), [true, true]);
  assert.equal(s.empty.hidden, false); assert.equal(s.status.textContent, '0 projects');
  s.search.value = ''; s.search.handlers.input();
  assert.deepEqual(s.cards.map(x => x.hidden), [true, false]);
  s.filters[0].handlers.click();
  assert.deepEqual(s.cards.map(x => x.hidden), [false, false]);
});
test('citation copy confirms success after clipboard write', async () => {
  const s = setup({clipboard: 'success'}); await s.copyButton.handlers.click();
  assert.equal(s.copied(), '@article{test, year={2026}}');
  assert.equal(s.copyButton.label.textContent, 'Copied');
  assert.notEqual(s.copyButton.disabled, true);
  assert.equal(s.copyButton.attributes['aria-busy'], 'false');
});
test('unavailable clipboard selects the citation and explains the fallback', async () => {
  const s = setup({clipboard: 'failure'}); await s.copyButton.handlers.click();
  assert.equal(s.selected(), true); assert.equal(s.copyButton.label.textContent, 'Selected');
  assert.match(s.copyStatus.textContent, /download the BibTeX/);
  assert.notEqual(s.copyButton.disabled, true);
  assert.equal(s.copyButton.attributes['aria-busy'], 'false');
});
