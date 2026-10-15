/* One-shot overview: delayed visible autoplay, explicit controls, motion-safe fallback. */
(function () {
  'use strict';
  const SCENES = {
    network: ['Training stays on each client', 'Local data → Client updates → Shared model'],
    nnc: ['Nearest Neighbor Correction', 'Local neighbors → Label vote → Corrected label'],
    akd: ['Adaptive Knowledge Distillation', 'Detected noise → Teacher guidance + Original labels'],
    na: ['Noise-Aware Federated Averaging', 'Estimate noise once → Weight future updates']
  };
  // Returning to the network separates the three alternative interventions.
  const TIMELINE = [
    {scene: 'network', duration: 3000},
    {scene: 'network', camera: 'nnc', duration: 500},
    {scene: 'nnc', duration: 9500},
    {scene: 'network', returning: true, duration: 1500},
    {scene: 'network', camera: 'akd', duration: 500},
    {scene: 'akd', duration: 9500},
    {scene: 'network', returning: true, duration: 1500},
    {scene: 'network', camera: 'na', duration: 500},
    {scene: 'na', duration: 9500}
  ];
  const AUTOPLAY_DELAY = 1500;
  const TOTAL = TIMELINE.reduce((sum, step) => sum + step.duration, 0);
  const NNC_PHASES = [
    {name: 'sample', at: 0, text: 'Dog image · Stored label: Cat'},
    {name: 'embedding', at: 1800, text: 'Frozen encoder → Image embedding'},
    {name: 'neighbors', at: 3600, text: 'Same client · Five nearest neighbors'},
    {name: 'vote', at: 6000, text: 'Label vote · 4 Dog / 1 Cat'},
    {name: 'corrected', at: 7800, text: 'Same image · Corrected label: Dog'}
  ];
  const METHOD_LABELS = {nnc:'NNC', akd:'AKD', na:'NA-FedAvg'};
  const PHASES = {
    nnc: NNC_PHASES,
    akd: [
      {name:'example', at:0, text:'Local image + Stored label'},
      {name:'teacher', at:1800, text:'Same image → Frozen teacher → Features'},
      {name:'guidance', at:4200, text:'Detected noise → Feature matching + Label supervision'},
      {name:'update', at:7000, text:'Joint update · Labels unchanged'}
    ],
    na: [
      {name:'warmup', at:0, text:'Warm-up · Local training → Model updates'},
      {name:'scores', at:1800, text:'One scoring round · Shared model + Local model'},
      {name:'noise', at:4200, text:'Client scores → Server noise estimates'},
      {name:'aggregation', at:7000, text:'Data share × Reliability → Weighted aggregation'}
    ]
  };

  function initialize(root) {
    if (root.dataset.tourReady === 'true') return;
    const query = selector => root.querySelector(selector);
    const viewport = query('.fl-tour-viewport') || root;
    const controls = query('[data-tour-controls]');
    const toggle = query('[data-tour-toggle]');
    const toggleLabel = query('[data-tour-toggle-label]');
    const progress = query('[data-tour-progress]');
    const status = query('[data-tour-status]');
    const title = query('[data-tour-title]');
    const description = query('[data-tour-description]');
    const stages = [...root.querySelectorAll('[data-tour-stage]')];
    const panels = [...root.querySelectorAll('[data-tour-scene]')];
    const methodParts = Object.fromEntries(Object.keys(PHASES).map(name =>
      [name, [...root.querySelectorAll('[data-tour-' + name + '-part]')]]));
    const neighbors = [...root.querySelectorAll('[data-tour-neighbor]')];
    if (!controls || !toggle || panels.length !== 4) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let elapsed = 0;
    let lastTime = null;
    let frame = null;
    let playing = false;
    let finished = false;
    let manual = false;
    let activeStep = -1;
    let intersecting = true;
    let selectedMethod = null;
    let playbackStart = 0;
    let playbackEnd = TOTAL;
    let autoplayPending = true;
    let resumeWhenVisible = false;
    let autoplayTimer = null;
    let pageActive = true;
    let windowFocused = true;

    function isVisible() {
      if (document.hidden || !pageActive || !windowFocused || !root.isConnected || !intersecting) return false;
      if (root.closest('[hidden], [aria-hidden="true"]')) return false;
      if (!root.getClientRects().length || window.getComputedStyle(root).visibility === 'hidden') return false;
      const bounds = viewport.getBoundingClientRect();
      // Measure the illustration, not its controls; a sliver must not start playback.
      // Base the threshold on the smaller of diagram and viewport, including phones.
      const visibleHeight = Math.min(bounds.bottom, window.innerHeight) - Math.max(bounds.top, 0);
      const requiredHeight = Math.min(bounds.bottom - bounds.top, window.innerHeight) * 0.35;
      return visibleHeight >= requiredHeight && requiredHeight > 0 && bounds.right > 0 && bounds.left < window.innerWidth;
    }

    function updateControls() {
      root.dataset.running = String(playing);
      const subject = selectedMethod ? METHOD_LABELS[selectedMethod] : 'overview';
      const continuing = elapsed > playbackStart && !manual;
      const verb = playing || resumeWhenVisible ? 'Pause' : finished ? 'Replay' : continuing ? 'Resume' : 'Play';
      const label = playing || resumeWhenVisible || finished || continuing ? verb : selectedMethod ? 'Play animation' : 'Play overview';
      toggleLabel.textContent = label;
      toggle.setAttribute('aria-label', verb + ' ' + subject + (selectedMethod ? ' animation' : '') +
        (verb === 'Play' ? ', ' + (playbackEnd - playbackStart) / 1000 + ' seconds' : ''));
    }

    function reveal(element, visible) {
      const value = String(visible);
      if (element.dataset.visible !== value) element.dataset.visible = value;
      element.setAttribute('aria-hidden', String(!visible));
    }

    function showMethod(name, localTime = null) {
      const phases = PHASES[name];
      const complete = localTime === null;
      let phaseIndex = phases.length - 1;
      if (!complete) {
        phaseIndex = 0;
        phases.forEach((phase, i) => { if (localTime >= phase.at) phaseIndex = i; });
      }
      const phase = phases[phaseIndex];
      const state = complete ? 'complete' : phase.name;
      if (root.dataset[name + 'Phase'] !== state) {
        root.dataset[name + 'Phase'] = state;
      }
      const copy = complete ? SCENES[name][1] : phase.text;
      if (description.textContent !== copy) description.textContent = copy;
      const key = 'tour' + name[0].toUpperCase() + name.slice(1) + 'Part';
      methodParts[name].forEach(part => {
        const index = phases.findIndex(item => item.name === part.dataset[key]);
        reveal(part, complete || (index >= 0 && phaseIndex >= index));
      });
      if (name === 'nnc') {
        // Neighbors are other local images. The query is never in this set.
        neighbors.forEach((neighbor, i) => reveal(neighbor, complete || localTime >= 3600 + i * 220));
      }
    }

    function showScene(name, {camera = '', returning = false, animate = false, announce = true} = {}) {
      const changed = root.dataset.active !== name;
      root.dataset.active = name;
      root.dataset.camera = camera;
      panels.forEach(panel => {
        const active = panel.dataset.tourScene === name;
        panel.hidden = !active;
        panel.classList.toggle('is-arriving', active && changed && animate && !motion.matches);
      });
      stages.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.tourStage === name)));
      title.textContent = SCENES[name][0];
      description.textContent = returning ? 'Shared network · Alternative intervention' : SCENES[name][1];
      if (PHASES[name]) showMethod(name, manual || motion.matches ? null : 0);
      if (announce && !camera) status.textContent = returning ? 'Returning to the network. The methods are alternatives.' : SCENES[name][0] + '. ' + SCENES[name][1];
    }

    function render() {
      // Keep a single-method replay on its final scene at the end boundary.
      const renderTime = Math.min(elapsed, playbackEnd - 0.001);
      let start = 0;
      let index = TIMELINE.length - 1;
      for (let i = 0; i < TIMELINE.length; i += 1) {
        if (renderTime < start + TIMELINE[i].duration || i === TIMELINE.length - 1) { index = i; break; }
        start += TIMELINE[i].duration;
      }
      const step = TIMELINE[index];
      if (index !== activeStep) {
        activeStep = index;
        showScene(step.scene, {...step, animate: true});
      }
      if (PHASES[step.scene]) showMethod(step.scene, renderTime - start);
      progress.style.transform = 'scaleX(' + Math.min(1, (elapsed - playbackStart) / (playbackEnd - playbackStart)) + ')';
    }

    function pause(message) {
      if (frame !== null) window.cancelAnimationFrame(frame);
      frame = null;
      playing = false;
      lastTime = null;
      updateControls();
      if (message) status.textContent = message;
    }

    function tick(time) {
      if (!playing) return;
      if (!isVisible()) { visibilityChanged(); return; }
      if (lastTime !== null) elapsed += Math.max(0, time - lastTime);
      lastTime = time;
      elapsed = Math.min(elapsed, playbackEnd);
      render();
      if (elapsed >= playbackEnd) {
        finished = true;
        root.classList.remove('is-touring');
        pause(selectedMethod ? SCENES[selectedMethod][0] + ' animation complete.' : 'Overview complete. NNC, AKD, and NA-FedAvg are three alternative interventions.');
        return;
      }
      frame = window.requestAnimationFrame(tick);
    }

    function reset(method = null) {
      pause();
      selectedMethod = method;
      playbackStart = 0;
      playbackEnd = TOTAL;
      if (method) {
        for (const step of TIMELINE) {
          if (step.scene === method) { playbackEnd = playbackStart + step.duration; break; }
          playbackStart += step.duration;
        }
      }
      elapsed = playbackStart;
      activeStep = -1;
      finished = false;
      manual = false;
      root.classList.remove('is-touring');
      progress.style.transform = 'scaleX(0)';
      showScene(method || 'network', {announce: false});
      updateControls();
    }

    function play() {
      if (motion.matches || playing) return;
      cancelAutoplay();
      autoplayPending = false;
      resumeWhenVisible = false;
      if (finished || manual) reset(selectedMethod);
      if (!isVisible()) {
        resumeWhenVisible = true;
        pause('Playback will begin when the diagram is in view.');
        return;
      }
      playing = true;
      lastTime = null;
      root.classList.add('is-touring');
      updateControls();
      status.textContent = (selectedMethod ? METHOD_LABELS[selectedMethod] : 'Overview') + ' playing. Pause or select a method at any time.';
      render();
      frame = window.requestAnimationFrame(tick);
    }

    toggle.addEventListener('click', () => {
      const shouldPause = playing || resumeWhenVisible;
      takeControl();
      if (shouldPause) pause('Overview paused. Resume or select a method.');
      else play();
    });
    stages.forEach(button => button.addEventListener('click', () => {
      takeControl();
      reset(button.dataset.tourStage);
      manual = true;
      showScene(button.dataset.tourStage);
      updateControls();
    }));

    function cancelAutoplay() {
      if (autoplayTimer !== null) window.clearTimeout(autoplayTimer);
      autoplayTimer = null;
    }

    function takeControl() {
      cancelAutoplay();
      autoplayPending = false;
      resumeWhenVisible = false;
    }

    function visibilityChanged() {
      if (!isVisible()) {
        cancelAutoplay();
        if (playing) {
          resumeWhenVisible = true;
          pause('Overview paused while out of view. It will resume when visible.');
        }
        return;
      }
      if (motion.matches || playing || finished || autoplayTimer !== null ||
          (!autoplayPending && !resumeWhenVisible)) return;
      autoplayTimer = window.setTimeout(() => {
        autoplayTimer = null;
        if (isVisible() && !motion.matches && !finished && (autoplayPending || resumeWhenVisible)) play();
      }, AUTOPLAY_DELAY);
    }
    document.addEventListener('visibilitychange', visibilityChanged);
    window.addEventListener('pagehide', () => { pageActive = false; visibilityChanged(); });
    window.addEventListener('pageshow', () => { pageActive = true; visibilityChanged(); });
    window.addEventListener('blur', () => { windowFocused = false; visibilityChanged(); });
    window.addEventListener('focus', () => { windowFocused = true; visibilityChanged(); });
    // Scroll/resize also catch the viewport-relative visibility threshold for
    // tall diagrams; an intersection-ratio observer alone cannot do that.
    window.addEventListener('scroll', visibilityChanged, {passive: true});
    window.addEventListener('resize', visibilityChanged, {passive: true});
    if ('IntersectionObserver' in window) {
      const intersection = new IntersectionObserver(entries => {
        intersecting = entries[0].isIntersecting;
        visibilityChanged();
      }, {threshold: [0, 0.15, 0.35, 0.5]});
      intersection.observe(root);
    }
    if ('MutationObserver' in window) {
      const visibility = new MutationObserver(visibilityChanged);
      let ancestor = root.parentElement;
      while (ancestor) {
        visibility.observe(ancestor, {attributes: true, attributeFilter: ['hidden', 'class', 'style', 'aria-hidden']});
        ancestor = ancestor.parentElement;
      }
    }
    function motionChanged() {
      cancelAutoplay();
      if (motion.matches) takeControl();
      pause();
      root.classList.remove('is-touring');
      panels.forEach(panel => panel.classList.remove('is-arriving'));
      root.dataset.camera = '';
      toggle.hidden = motion.matches;
      if (motion.matches && PHASES[root.dataset.active]) {
        manual = true;
        showMethod(root.dataset.active);
        updateControls();
      }
      status.textContent = motion.matches ? 'Reduced motion is enabled. Select a method to explore at your own pace.' : 'Select a method or play the overview.';
      visibilityChanged();
    }
    if (motion.addEventListener) motion.addEventListener('change', motionChanged);
    else if (motion.addListener) motion.addListener(motionChanged);
    root.dataset.tourReady = 'true';
    root.classList.add('is-enhanced');
    controls.hidden = false;
    motionChanged();
  }
  function boot() { document.querySelectorAll('[data-fl-tour]').forEach(initialize); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once: true});
  else boot();
})();
