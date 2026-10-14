const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const writing = require('../assets/hero-writing.js');

class Target {
  constructor() { this.listeners = new Map(); }
  addEventListener(name, callback) {
    if (!this.listeners.has(name)) this.listeners.set(name, new Set());
    this.listeners.get(name).add(callback);
  }
  removeEventListener(name, callback) { this.listeners.get(name)?.delete(callback); }
  emit(name) { for (const callback of this.listeners.get(name) || []) callback({ type: name }); }
}

function setup(options = {}) {
  let now = 0, nextId = 0;
  const timers = new Map();
  const scheduler = {
    now: () => now,
    setTimeout(callback, delay) { const id = ++nextId; timers.set(id, { callback, at: now + delay }); return id; },
    clearTimeout(id) { timers.delete(id); }
  };
  const advance = ms => {
    const end = now + ms;
    for (;;) {
      const next = [...timers].sort((a, b) => a[1].at - b[1].at)[0];
      if (!next || next[1].at > end) break;
      now = next[1].at;
      timers.delete(next[0]);
      next[1].callback();
    }
    now = end;
  };
  const text = { textContent: options.initial || 'learns together.' };
  const label = { textContent: 'Pause' };
  const toggle = new Target();
  toggle.hidden = true;
  toggle.attributes = {};
  toggle.setAttribute = (name, value) => { toggle.attributes[name] = value; };
  const root = new Target();
  root.dataset = { phrases: options.rawPhrases ?? JSON.stringify(options.phrases || ['learns together.', 'adapts efficiently.', 'acts at the edge.']) };
  root.isConnected = true;
  root.rect = options.rect || { top: 100, bottom: 450, left: 0, right: 600 };
  root.getBoundingClientRect = () => root.rect;
  root.getClientRects = () => root.displayNone ? [] : [root.rect];
  root.closest = () => root.ancestorHidden ? {} : null;
  root.querySelector = selector => ({ '[data-writing-text]': text, '[data-writing-toggle]': options.noControls ? null : toggle, '[data-writing-label]': options.noControls ? null : label })[selector];
  const document = new Target();
  document.hidden = options.hidden || false;
  document.focused = options.focused ?? true;
  document.hasFocus = () => document.focused;
  document.readyState = options.readyState || 'complete';
  document.querySelectorAll = () => [root];
  const window = new Target();
  window.innerWidth = 1000;
  window.innerHeight = 900;
  window.getComputedStyle = () => ({ visibility: root.invisible ? 'hidden' : 'visible', opacity: '1' });
  window.setTimeout = scheduler.setTimeout;
  window.clearTimeout = scheduler.clearTimeout;
  window.performance = { now: scheduler.now };
  const motion = new Target();
  motion.matches = options.reduced || false;
  if (options.legacyMotion) {
    motion.addListener = callback => Target.prototype.addEventListener.call(motion, 'change', callback);
    motion.removeListener = callback => Target.prototype.removeEventListener.call(motion, 'change', callback);
    motion.addEventListener = undefined;
    motion.removeEventListener = undefined;
  }
  window.matchMedia = () => motion;
  const observers = [];
  if (!options.noObserver) {
    window.IntersectionObserver = class {
      constructor(callback) { this.callback = callback; observers.push(this); }
      observe() {}
      disconnect() {}
    };
  }
  const environment = { window, document, scheduler };
  const controller = options.defer ? null : writing.initialize(root, environment);
  return { root, text, label, toggle, document, window, motion, timers, observers, environment, controller, advance };
}

test('keeps the initial phrase readable, erases faster, types gradually, then holds', () => {
  const t = setup({ phrases: ['ab', 'cd'], initial: 'ab', noControls: true });
  t.advance(1499);
  assert.equal(t.text.textContent, 'ab');
  t.advance(1);
  assert.equal(t.text.textContent, 'a');
  t.advance(32);
  assert.equal(t.text.textContent, '');
  t.advance(240);
  assert.equal(t.text.textContent, 'c');
  t.advance(68);
  assert.equal(t.text.textContent, 'cd');
  t.advance(2399);
  assert.equal(t.text.textContent, 'cd');
  t.advance(1);
  assert.equal(t.text.textContent, 'c');
  t.advance(32 + 240 + 68);
  assert.equal(t.text.textContent, 'ab', 'the last phrase loops back to the first');
});

test('pure model steps do not mutate state and never split Unicode code points', () => {
  const phrases = ['A😀', 'B'];
  const initial = writing.createState(phrases);
  const next = writing.stepState(initial, phrases);
  assert.equal(writing.stateText(initial, phrases), 'A😀');
  assert.equal(writing.stateText(next, phrases), 'A');
  assert.ok(writing.delayFor(next) < writing.delayFor({ ...next, phase: 'typing' }));
});

test('manual pause completes a partial phrase and survives automatic resume events', () => {
  const t = setup();
  t.advance(1600);
  assert.notEqual(t.text.textContent, 'learns together.');
  t.toggle.emit('click');
  assert.equal(t.text.textContent, 'learns together.');
  assert.equal(t.root.dataset.paused, 'true');
  assert.match(t.toggle.attributes['aria-label'], /resume/i);
  for (const name of ['scroll', 'resize', 'focus', 'pageshow']) t.window.emit(name);
  t.document.emit('visibilitychange');
  t.advance(60000);
  assert.equal(t.timers.size, 0);
  assert.equal(t.text.textContent, 'learns together.');
  t.toggle.emit('click');
  assert.equal(t.timers.size, 1);
  t.advance(2399);
  assert.equal(t.text.textContent, 'learns together.');
  t.advance(1);
  assert.equal(t.text.textContent, 'learns together');
});

for (const reason of ['viewport', 'hidden', 'blur', 'pagehide', 'ancestor', 'display', 'detached']) {
  test(`${reason} pauses without consuming time and resumes with one timer`, () => {
    const t = setup();
    t.advance(1490);
    if (reason === 'viewport') t.root.rect = { top: 901, bottom: 1200, left: 0, right: 600 };
    if (reason === 'hidden') t.document.hidden = true;
    if (reason === 'ancestor') t.root.ancestorHidden = true;
    if (reason === 'display') t.root.displayNone = true;
    if (reason === 'detached') t.root.isConnected = false;
    if (reason === 'blur') { t.document.focused = false; t.window.emit('blur'); }
    else if (reason === 'pagehide') t.window.emit('pagehide');
    else if (reason === 'hidden') t.document.emit('visibilitychange');
    else t.window.emit('scroll');
    assert.equal(t.timers.size, 0);
    t.advance(100000);
    assert.equal(t.text.textContent, 'learns together.');
    t.root.rect = { top: 100, bottom: 450, left: 0, right: 600 };
    t.root.ancestorHidden = false;
    t.root.displayNone = false;
    t.root.isConnected = true;
    t.document.hidden = false;
    t.document.focused = true;
    t.window.emit('focus');
    t.window.emit('pageshow');
    t.document.emit('visibilitychange');
    t.window.emit('scroll');
    assert.equal(t.timers.size, 1);
    t.advance(9);
    assert.equal(t.text.textContent, 'learns together.');
    t.advance(1);
    assert.equal(t.text.textContent, 'learns together');
  });
}

test('starts only with sufficient visible area, including without IntersectionObserver', () => {
  const t = setup({ noObserver: true, rect: { top: 895, bottom: 1200, left: 0, right: 600 } });
  t.advance(10000);
  assert.equal(t.timers.size, 0);
  t.root.rect = { top: 500, bottom: 800, left: 0, right: 600 };
  t.window.emit('scroll');
  t.advance(1499);
  assert.equal(t.text.textContent, 'learns together.');
  t.advance(1);
  assert.equal(t.text.textContent, 'learns together');
});

test('IntersectionObserver suspends playback and duplicate observations do not multiply timers', () => {
  const t = setup();
  t.observers[0].callback([{ target: t.root, isIntersecting: false }]);
  assert.equal(t.timers.size, 0);
  t.advance(20000);
  for (let i = 0; i < 5; i++) t.observers[0].callback([{ target: t.root, isIntersecting: true }]);
  assert.equal(t.timers.size, 1);
  t.advance(1500);
  assert.equal(t.text.textContent, 'learns together');
});

for (const legacyMotion of [false, true]) {
  test(`reduced motion stays static, handles runtime changes, and preserves manual pause (${legacyMotion ? 'legacy' : 'modern'})`, () => {
    const t = setup({ reduced: true, legacyMotion });
    t.advance(10000);
    assert.equal(t.timers.size, 0);
    assert.equal(t.toggle.hidden, true);
    assert.equal(t.text.textContent, 'learns together.');
    t.motion.matches = false;
    t.motion.emit('change');
    assert.equal(t.toggle.hidden, false);
    t.advance(2400);
    assert.notEqual(t.text.textContent, 'learns together.');
    t.motion.matches = true;
    t.motion.emit('change');
    assert.equal(t.text.textContent, 'learns together.');
    assert.equal(t.timers.size, 0);
    t.motion.matches = false;
    t.motion.emit('change');
    t.toggle.emit('click');
    t.motion.matches = true;
    t.motion.emit('change');
    t.motion.matches = false;
    t.motion.emit('change');
    assert.equal(t.timers.size, 0, 'a preference change cannot override manual pause');
  });
}

test('stale queued callbacks cannot advance text or replace the resumed timer', () => {
  const t = setup();
  const stale = [...t.timers.values()][0].callback;
  t.window.emit('blur');
  t.window.emit('focus');
  stale();
  assert.equal(t.text.textContent, 'learns together.');
  assert.equal(t.timers.size, 1);
  t.advance(1500);
  assert.equal(t.text.textContent, 'learns together');
});

test('boot and repeated initialization are idempotent', () => {
  const t = setup();
  assert.equal(writing.initialize(t.root, t.environment), t.controller);
  writing.boot(t.document, t.window);
  assert.equal(t.timers.size, 1);
  t.toggle.emit('click');
  assert.equal(t.timers.size, 0, 'a duplicate handler would immediately resume');
});

test('cleanup leaves a complete static phrase and allows clean initialization again', () => {
  const t = setup();
  t.advance(1600);
  const stale = [...t.timers.values()][0].callback;
  t.controller.destroy();
  assert.equal(t.text.textContent, 'learns together.');
  assert.equal(t.timers.size, 0);
  assert.equal(t.toggle.hidden, true);
  t.window.emit('focus');
  t.toggle.emit('click');
  stale();
  assert.equal(t.timers.size, 0);
  writing.initialize(t.root, t.environment);
  assert.equal(t.toggle.hidden, false);
  t.advance(1500);
  assert.equal(t.text.textContent, 'learns together');
});

test('an initially unfocused document waits for focus and supports missing matchMedia', () => {
  const t = setup({ defer: true, focused: false });
  delete t.window.matchMedia;
  writing.initialize(t.root, t.environment);
  t.advance(10000);
  assert.equal(t.text.textContent, 'learns together.');
  assert.equal(t.timers.size, 0);
  t.window.emit('focus');
  t.advance(1500);
  assert.equal(t.text.textContent, 'learns together');
});

test('the initial phrase can be any configured phrase and phrase text is never interpreted as markup', () => {
  const t = setup({ phrases: ['<b>one</b>', 'two'], initial: 'two' });
  t.toggle.emit('click');
  assert.equal(t.text.textContent, 'two');
  t.toggle.emit('click');
  t.advance(2400 + 64 + 240 + 9 * 68);
  assert.equal(t.text.textContent, '<b>one</b>');
});

test('invalid phrase data and incomplete markup leave the static fallback untouched', () => {
  for (const rawPhrases of ['broken', '{}', '[]', '[null, 1, ""]']) {
    const t = setup({ rawPhrases });
    assert.equal(t.controller, null);
    assert.equal(t.text.textContent, 'learns together.');
    assert.equal(t.toggle.hidden, true);
    assert.equal(t.timers.size, 0);
  }
  const t = setup({ defer: true });
  t.root.querySelector = () => null;
  assert.equal(writing.initialize(t.root, t.environment), null);
  assert.equal(t.timers.size, 0);
});

test('browser entry waits for DOMContentLoaded and also supports defer/loaded documents', () => {
  const source = fs.readFileSync(path.join(__dirname, '../assets/hero-writing.js'), 'utf8');
  for (const readyState of ['loading', 'complete']) {
    const t = setup({ defer: true, readyState });
    vm.runInNewContext(source, { window: t.window, document: t.document });
    if (readyState === 'loading') {
      assert.equal(t.toggle.hidden, true);
      t.document.emit('DOMContentLoaded');
    }
    assert.equal(t.toggle.hidden, false);
    assert.equal(t.timers.size, 1);
    t.advance(1500);
    assert.equal(t.text.textContent, 'learns together');
  }
});
