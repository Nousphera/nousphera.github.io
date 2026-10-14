/* A bounded, opt-in tour. Stage buttons remain fully manual. */
(function () {
  'use strict';
  const SCENES = {
    network: ['Federated learning', 'Training stays on each client', 'Clients learn from local data; the server combines their model updates.'],
    nnc: ['NNC · initialization', 'Let nearby examples correct a label', 'A local pre-trained embedding space supplies neighbors whose labels vote.'],
    akd: ['AKD · local training', 'Add a teacher when labels are noisy', 'Estimated local noise gates the teacher loss alongside the supervised loss.'],
    na: ['NA-FedAvg · server aggregation', 'Reduce the influence of noisy updates', 'After warm-up, estimate client noise once and adjust the aggregation weights.']
  };
  // Network returns separate the alternatives; this is not a combined pipeline.
  const TIMELINE = [
    {scene: 'network', duration: 3000},
    {scene: 'network', camera: 'nnc', duration: 450},
    {scene: 'nnc', duration: 6000},
    {scene: 'network', returning: true, duration: 1800},
    {scene: 'network', camera: 'akd', duration: 450},
    {scene: 'akd', duration: 6000},
    {scene: 'network', returning: true, duration: 1800},
    {scene: 'network', camera: 'na', duration: 450},
    {scene: 'na', duration: 6000}
  ];
  const TOTAL = TIMELINE.reduce((sum, step) => sum + step.duration, 0);

  function initialize(root) {
    if (root.dataset.tourReady === 'true') return;
    const query = selector => root.querySelector(selector);
    const controls = query('[data-tour-controls]');
    const toggle = query('[data-tour-toggle]');
    const toggleLabel = query('[data-tour-toggle-label]');
    const playIcon = query('[data-tour-play-icon]');
    const replay = query('[data-tour-replay]');
    const replayLabel = query('[data-tour-replay-label]');
    const duration = query('[data-tour-duration]');
    const progress = query('[data-tour-progress]');
    const status = query('[data-tour-status]');
    const title = query('[data-tour-title]');
    const description = query('[data-tour-description]');
    const kicker = query('[data-tour-kicker]');
    const stages = [...root.querySelectorAll('[data-tour-stage]')];
    const panels = [...root.querySelectorAll('[data-tour-scene]')];
    if (!controls || !toggle || !replay || panels.length !== 4) return;
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
      toggleLabel.textContent = playing ? 'Pause' : finished ? 'Replay tour' : elapsed > 0 && !manual ? 'Resume' : 'Play tour';
      playIcon.textContent = playing ? 'Ⅱ' : '▶';
      toggle.setAttribute('aria-label', playing ? 'Pause the method tour' : finished ? 'Replay the method tour from the overview' : elapsed > 0 && !manual ? 'Resume the method tour' : 'Play the 26-second method tour');
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
      const copy = SCENES[name];
      kicker.textContent = returning ? 'Another alternative' : copy[0];
      title.textContent = returning ? 'Back to the shared network' : copy[1];
      description.textContent = returning ? 'Now explore a different intervention point; the methods are alternatives.' : copy[2];
      if (announce && !camera) status.textContent = returning ? 'Returning to the network to explore another alternative.' : copy[0] + '. ' + copy[2];
    }

    function render() {
      let boundary = 0;
      let index = TIMELINE.length - 1;
      for (let i = 0; i < TIMELINE.length; i += 1) {
        boundary += TIMELINE[i].duration;
        if (elapsed < boundary) { index = i; break; }
      }
      if (index !== activeStep) {
        activeStep = index;
        const step = TIMELINE[index];
        showScene(step.scene, {...step, animate: true});
      }
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
      if (!isVisible()) { pause('Tour paused while out of view. Resume when ready.'); return; }
      if (lastTime !== null) elapsed += Math.max(0, time - lastTime);
      lastTime = time;
      elapsed = Math.min(elapsed, TOTAL);
      render();
      if (elapsed >= TOTAL) {
        finished = true;
        root.classList.remove('is-touring');
        pause('Tour complete. NNC, AKD, and NA-FedAvg are three alternative interventions.');
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

    function play({restart = false} = {}) {
      if (motion.matches) {
        status.textContent = 'Reduced motion is enabled. Select a stage to explore at your own pace.';
        return;
      }
      if (restart || finished || manual) reset();
      if (!isVisible()) { pause('The tour is paused while out of view.'); return; }
      playing = true;
      lastTime = null;
      root.classList.add('is-touring');
      updateControls();
      status.textContent = 'Tour playing. You can pause or select a stage at any time.';
      render();
      frame = window.requestAnimationFrame(tick);
    }

    toggle.addEventListener('click', () => {
      if (playing) pause('Tour paused. Resume or select a stage.');
      else play();
    });
    replay.addEventListener('click', () => {
      if (motion.matches) { reset(); status.textContent = 'Network overview. Select a stage to explore.'; }
      else play({restart: true});
    });
    stages.forEach(button => button.addEventListener('click', () => {
      reset();
      manual = true;
      showScene(button.dataset.tourStage);
      status.textContent = SCENES[button.dataset.tourStage][0] + '. Static view; select another stage to continue.';
    }));

    function visibilityChanged() {
      if (playing && !isVisible()) pause('Tour paused while out of view. Resume when ready.');
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
    // Observe actual ancestors, so Overview tab visibility pauses immediately.
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
      duration.textContent = motion.matches ? 'Reduced motion · explore manually' : '26 seconds · plays once';
      replayLabel.textContent = motion.matches ? 'Overview' : 'Replay';
      replay.setAttribute('aria-label', motion.matches ? 'Return to the network overview' : 'Replay the tour from the network overview');
      status.textContent = motion.matches ? 'Reduced motion is enabled. Select a stage to explore at your own pace.' : 'Select a method or play the guided tour.';
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
