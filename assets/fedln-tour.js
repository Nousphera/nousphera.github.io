/* An opt-in, one-shot overview. Manual method views never start a timer. */
(function () {
  'use strict';
  const SCENES = {
    network: ['Training stays on each client', 'Clients learn from local data; the server combines their model updates.'],
    nnc: ['Nearest Neighbor Correction', 'Image features find local neighbors; their labels vote to correct the stored label.'],
    akd: ['Adaptive Knowledge Distillation', 'Estimated local noise gates the teacher loss alongside the supervised loss.'],
    na: ['Noise-Aware Federated Averaging', 'After warm-up, estimate client noise once and reduce the weight of noisier updates.']
  };
  // Returning to the network separates the three alternative interventions.
  const TIMELINE = [
    {scene: 'network', duration: 3000},
    {scene: 'network', camera: 'nnc', duration: 500},
    {scene: 'nnc', duration: 9500},
    {scene: 'network', returning: true, duration: 1500},
    {scene: 'network', camera: 'akd', duration: 500},
    {scene: 'akd', duration: 5500},
    {scene: 'network', returning: true, duration: 1500},
    {scene: 'network', camera: 'na', duration: 500},
    {scene: 'na', duration: 5500}
  ];
  const TOTAL = TIMELINE.reduce((sum, step) => sum + step.duration, 0);
  const NNC_PHASES = [
    {name: 'sample', at: 0, text: 'This dog image has the wrong stored label: “Cat”.'},
    {name: 'embedding', at: 1800, text: 'A frozen encoder maps the image content into an embedding.'},
    {name: 'neighbors', at: 3600, text: 'Find five nearest other examples in this client’s embedding space.'},
    {name: 'vote', at: 6000, text: 'Their stored labels vote: four “Dog”, one “Cat”.'},
    {name: 'corrected', at: 7800, text: 'Change the stored label to “Dog”. The image stays the same.'}
  ];

  function initialize(root) {
    if (root.dataset.tourReady === 'true') return;
    const query = selector => root.querySelector(selector);
    const controls = query('[data-tour-controls]');
    const toggle = query('[data-tour-toggle]');
    const toggleLabel = query('[data-tour-toggle-label]');
    const progress = query('[data-tour-progress]');
    const status = query('[data-tour-status]');
    const title = query('[data-tour-title]');
    const description = query('[data-tour-description]');
    const stages = [...root.querySelectorAll('[data-tour-stage]')];
    const panels = [...root.querySelectorAll('[data-tour-scene]')];
    const nncParts = [...root.querySelectorAll('[data-tour-nnc-part]')];
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

    function isVisible() {
      if (document.hidden || !root.isConnected || !intersecting) return false;
      if (root.closest('[hidden], [aria-hidden="true"]')) return false;
      if (!root.getClientRects().length || window.getComputedStyle(root).visibility === 'hidden') return false;
      const bounds = root.getBoundingClientRect();
      return bounds.bottom > 0 && bounds.top < window.innerHeight && bounds.right > 0 && bounds.left < window.innerWidth;
    }

    function updateControls() {
      root.dataset.running = String(playing);
      const label = playing ? 'Pause' : finished ? 'Replay overview' : elapsed > 0 && !manual ? 'Resume overview' : 'Play overview';
      toggleLabel.textContent = label;
      toggle.setAttribute('aria-label', playing ? 'Pause the overview' : label + (label === 'Play overview' ? ', 28 seconds' : ''));
    }

    function reveal(element, visible) {
      const value = String(visible);
      if (element.dataset.visible !== value) element.dataset.visible = value;
      element.setAttribute('aria-hidden', String(!visible));
    }

    function showNnc(localTime = null) {
      const complete = localTime === null;
      let phaseIndex = NNC_PHASES.length - 1;
      if (!complete) {
        phaseIndex = 0;
        NNC_PHASES.forEach((phase, i) => { if (localTime >= phase.at) phaseIndex = i; });
      }
      const phase = NNC_PHASES[phaseIndex];
      const name = complete ? 'complete' : phase.name;
      if (root.dataset.nncPhase !== name) {
        root.dataset.nncPhase = name;
        description.textContent = complete ? SCENES.nnc[1] : phase.text;
      }
      const order = {embedding: 1, neighbors: 2, vote: 3, corrected: 4};
      nncParts.forEach(part => reveal(part, complete || phaseIndex >= order[part.dataset.tourNncPart]));
      // Neighbors are other local images. The query is never in this set.
      neighbors.forEach((neighbor, i) => reveal(neighbor, complete || localTime >= 3600 + i * 220));
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
      description.textContent = returning ? 'Return to the network to explore a different intervention.' : SCENES[name][1];
      if (name === 'nnc') showNnc(manual || motion.matches ? null : 0);
      if (announce && !camera) status.textContent = returning ? 'Returning to the network. The methods are alternatives.' : SCENES[name][0] + '. ' + SCENES[name][1];
    }

    function render() {
      let start = 0;
      let index = TIMELINE.length - 1;
      for (let i = 0; i < TIMELINE.length; i += 1) {
        if (elapsed < start + TIMELINE[i].duration || i === TIMELINE.length - 1) { index = i; break; }
        start += TIMELINE[i].duration;
      }
      const step = TIMELINE[index];
      if (index !== activeStep) {
        activeStep = index;
        showScene(step.scene, {...step, animate: true});
      }
      if (step.scene === 'nnc') showNnc(elapsed - start);
      progress.style.transform = 'scaleX(' + Math.min(1, elapsed / TOTAL) + ')';
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
      if (!isVisible()) { pause('Overview paused while out of view. Resume when ready.'); return; }
      if (lastTime !== null) elapsed += Math.max(0, time - lastTime);
      lastTime = time;
      elapsed = Math.min(elapsed, TOTAL);
      render();
      if (elapsed >= TOTAL) {
        finished = true;
        root.classList.remove('is-touring');
        pause('Overview complete. NNC, AKD, and NA-FedAvg are three alternative interventions.');
        return;
      }
      frame = window.requestAnimationFrame(tick);
    }

    function reset() {
      pause();
      elapsed = 0;
      activeStep = -1;
      finished = false;
      manual = false;
      root.classList.remove('is-touring');
      progress.style.transform = 'scaleX(0)';
      showScene('network', {announce: false});
      updateControls();
    }

    function play() {
      if (motion.matches) return;
      if (finished || manual) reset();
      if (!isVisible()) { pause('The overview is paused while out of view.'); return; }
      playing = true;
      lastTime = null;
      root.classList.add('is-touring');
      updateControls();
      status.textContent = 'Overview playing. Pause or select a method at any time.';
      render();
      frame = window.requestAnimationFrame(tick);
    }

    toggle.addEventListener('click', () => {
      if (playing) pause('Overview paused. Resume or select a method.');
      else play();
    });
    stages.forEach(button => button.addEventListener('click', () => {
      reset();
      manual = true;
      showScene(button.dataset.tourStage);
      updateControls();
    }));

    function visibilityChanged() {
      if (playing && !isVisible()) pause('Overview paused while out of view. Resume when ready.');
    }
    document.addEventListener('visibilitychange', visibilityChanged);
    window.addEventListener('pagehide', () => pause());
    if ('IntersectionObserver' in window) {
      const intersection = new IntersectionObserver(entries => {
        intersecting = entries[0].isIntersecting;
        visibilityChanged();
      }, {threshold: 0});
      intersection.observe(root);
    } else {
      window.addEventListener('scroll', visibilityChanged, {passive: true});
      window.addEventListener('resize', visibilityChanged, {passive: true});
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
      pause();
      root.classList.remove('is-touring');
      panels.forEach(panel => panel.classList.remove('is-arriving'));
      root.dataset.camera = '';
      toggle.hidden = motion.matches;
      if (motion.matches && root.dataset.active === 'nnc') {
        manual = true;
        showNnc();
        updateControls();
      }
      status.textContent = motion.matches ? 'Reduced motion is enabled. Select a method to explore at your own pace.' : 'Select a method or play the overview.';
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
