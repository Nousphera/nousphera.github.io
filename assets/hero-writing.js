/* A decorative headline: its complete, accessible equivalent lives in the HTML. */
(function (factory) {
  'use strict';
  const writing = factory();
  if (typeof module === 'object' && module.exports) module.exports = writing;
  else if (typeof document !== 'undefined' && typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => writing.boot(document, window), { once: true });
    } else writing.boot(document, window);
  }
})(function () {
  'use strict';
  const INITIAL_DELAY = 1500;
  const HOLD_DELAY = 2400;
  const TYPE_DELAY = 68;
  const DELETE_DELAY = 32;
  const EMPTY_DELAY = 240;
  const controllers = new WeakMap();
  const characters = phrase => Array.from(phrase);

  function parsePhrases(value) {
    try {
      const phrases = JSON.parse(value);
      return Array.isArray(phrases)
        ? phrases.filter(phrase => typeof phrase === 'string' && phrase.trim()).map(phrase => phrase.trim())
        : [];
    } catch (_) { return []; }
  }

  function createState(phrases, index = 0) {
    return { index, count: characters(phrases[index]).length, phase: 'holding' };
  }

  function stateText(state, phrases) {
    return characters(phrases[state.index]).slice(0, state.count).join('');
  }

  function stepState(state, phrases) {
    if (state.phase === 'holding' || state.phase === 'deleting') {
      const count = Math.max(0, state.count - 1);
      return { index: state.index, count, phase: count ? 'deleting' : 'empty' };
    }
    const index = state.phase === 'empty' ? (state.index + 1) % phrases.length : state.index;
    const length = characters(phrases[index]).length;
    const count = state.phase === 'empty' ? 1 : Math.min(length, state.count + 1);
    return { index, count, phase: count === length ? 'holding' : 'typing' };
  }

  function delayFor(state) {
    if (state.phase === 'holding') return HOLD_DELAY;
    if (state.phase === 'empty') return EMPTY_DELAY;
    return state.phase === 'deleting' ? DELETE_DELAY : TYPE_DELAY;
  }

  function initialize(root, environment = {}) {
    if (controllers.has(root)) return controllers.get(root);
    const win = environment.window || window;
    const doc = environment.document || document;
    const text = root.querySelector('[data-writing-text]');
    const toggle = root.querySelector('[data-writing-toggle]');
    const label = root.querySelector('[data-writing-label]');
    const phrases = parsePhrases(root.dataset.phrases);
    if (!text || !toggle || !label || !phrases.length) return null;

    const scheduler = environment.scheduler || {
      now: () => win.performance ? win.performance.now() : Date.now(),
      setTimeout: (callback, delay) => win.setTimeout(callback, delay),
      clearTimeout: id => win.clearTimeout(id)
    };
    const motion = win.matchMedia ? win.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
    let state = createState(phrases, Math.max(0, phrases.indexOf(text.textContent.trim())));
    let remaining = INITIAL_DELAY, deadline = 0, timer = null, generation = 0;
    let manualPaused = false, pageActive = true, intersecting = true, destroyed = false;
    let focused = typeof doc.hasFocus === 'function' ? doc.hasFocus() : true;
    const cleanups = [];

    function listen(target, event, callback, options) {
      target.addEventListener(event, callback, options);
      cleanups.push(() => target.removeEventListener(event, callback, options));
    }

    function visible() {
      if (doc.hidden || !pageActive || !focused || !intersecting || !root.isConnected) return false;
      if (root.closest('[hidden], [aria-hidden="true"], [inert]') || !root.getClientRects().length) return false;
      const style = win.getComputedStyle(root);
      if (style.visibility === 'hidden' || style.visibility === 'collapse' || style.opacity === '0') return false;
      const rect = root.getBoundingClientRect();
      const visibleHeight = Math.min(rect.bottom, win.innerHeight) - Math.max(rect.top, 0);
      const requiredHeight = Math.min(rect.bottom - rect.top, win.innerHeight) * 0.2;
      return requiredHeight > 0 && visibleHeight >= requiredHeight && rect.right > 0 && rect.left < win.innerWidth;
    }

    function canRun() {
      return !destroyed && !manualPaused && !motion.matches && visible();
    }

    function render() { text.textContent = stateText(state, phrases); }

    function suspend() {
      if (timer === null) return;
      remaining = Math.max(0, deadline - scheduler.now());
      scheduler.clearTimeout(timer);
      timer = null;
      generation += 1; // A callback already queued before cancellation must remain inert.
    }

    function sync() {
      if (destroyed) return;
      const running = canRun();
      root.dataset.paused = String(!running);
      toggle.hidden = motion.matches;
      label.textContent = manualPaused ? 'Resume' : 'Pause';
      toggle.setAttribute('aria-label', (manualPaused ? 'Resume' : 'Pause') + ' headline animation');
      if (!running) { suspend(); return; }
      if (timer !== null) return;
      const ticket = ++generation;
      deadline = scheduler.now() + remaining;
      timer = scheduler.setTimeout(() => {
        if (ticket !== generation || destroyed) return;
        timer = null;
        remaining = 0;
        // Check again: a page can leave view between an event and this callback.
        if (!canRun()) { sync(); return; }
        state = stepState(state, phrases);
        render();
        remaining = delayFor(state);
        sync();
      }, remaining);
    }

    function completePhrase() {
      suspend();
      state = createState(phrases, state.index);
      remaining = HOLD_DELAY;
      render();
    }

    function pause() { manualPaused = true; completePhrase(); sync(); }
    function resume() { manualPaused = false; sync(); }
    function motionChanged() {
      if (motion.matches) completePhrase();
      sync();
    }

    listen(toggle, 'click', () => { if (manualPaused) resume(); else pause(); });
    listen(doc, 'visibilitychange', () => {
      if (!doc.hidden && typeof doc.hasFocus === 'function') focused = doc.hasFocus();
      sync();
    });
    // These also provide the visibility fallback when IntersectionObserver is unavailable.
    listen(win, 'scroll', sync, { passive: true });
    listen(win, 'resize', sync, { passive: true });
    listen(win, 'blur', () => { focused = false; sync(); });
    listen(win, 'focus', () => { focused = true; sync(); });
    listen(win, 'pagehide', () => { pageActive = false; sync(); });
    listen(win, 'pageshow', () => {
      pageActive = true;
      focused = typeof doc.hasFocus === 'function' ? doc.hasFocus() : true;
      sync();
    });
    if (win.IntersectionObserver) {
      const observer = new win.IntersectionObserver(entries => {
        const entry = entries.find(item => item.target === root);
        if (entry) { intersecting = entry.isIntersecting; sync(); }
      }, { threshold: [0, 0.2, 0.5] });
      observer.observe(root);
      cleanups.push(() => observer.disconnect());
    }
    if (win.MutationObserver) {
      const observer = new win.MutationObserver(sync);
      for (let ancestor = root; ancestor; ancestor = ancestor.parentElement) {
        observer.observe(ancestor, { attributes: true, attributeFilter: ['hidden', 'aria-hidden', 'inert', 'class', 'style'] });
      }
      cleanups.push(() => observer.disconnect());
    }
    if (motion.addEventListener) listen(motion, 'change', motionChanged);
    else if (motion.addListener) {
      motion.addListener(motionChanged);
      cleanups.push(() => motion.removeListener(motionChanged));
    }

    const controller = {
      pause,
      resume,
      destroy() {
        completePhrase();
        destroyed = true;
        cleanups.forEach(cleanup => cleanup());
        toggle.hidden = true;
        root.dataset.paused = 'true';
        delete root.dataset.writingReady;
        controllers.delete(root);
      }
    };
    controllers.set(root, controller);
    root.dataset.writingReady = 'true';
    render();
    motionChanged();
    return controller;
  }

  function boot(doc, win) {
    doc.querySelectorAll('[data-writing-hero]').forEach(root => initialize(root, { document: doc, window: win }));
  }

  return { parsePhrases, createState, stateText, stepState, delayFor, initialize, boot };
});
