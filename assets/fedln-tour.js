/* An opt-in, one-shot overview. Manual method views never start a timer. */
(function () {
  'use strict';
  const SCENES = {
    network: ['Training stays on each client', 'Clients learn from local data; the server combines their model updates.'],
    nnc: ['Nearest Neighbor Correction', 'Image features find local neighbors; their labels vote to correct the stored label.'],
    akd: ['Adaptive Knowledge Distillation', 'When client noise is detected, teacher features guide training alongside the original labels.'],
    na: ['Noise-Aware Federated Averaging', 'Estimate client noise once, then combine updates using data share and estimated label reliability.']
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
  const TOTAL = TIMELINE.reduce((sum, step) => sum + step.duration, 0);
  const NNC_PHASES = [
    {name: 'sample', at: 0, text: 'This dog image has the wrong stored label: “Cat”.'},
    {name: 'embedding', at: 1800, text: 'A frozen encoder maps the image content into an embedding.'},
    {name: 'neighbors', at: 3600, text: 'Find five nearest other examples in this client’s embedding space.'},
    {name: 'vote', at: 6000, text: 'Their stored labels vote: four “Dog”, one “Cat”.'},
    {name: 'corrected', at: 7800, text: 'Change the stored label to “Dog”. The image stays the same.'}
  ];
  const METHOD_LABELS = {nnc:'NNC', akd:'AKD', na:'NA-FedAvg'};
  const PHASES = {
    nnc: NNC_PHASES,
    akd: [
      {name:'example', at:0, text:'The image and its stored label feed local training. The label may be wrong.'},
      {name:'teacher', at:1800, text:'A frozen teacher extracts features from the same image, without using its label.'},
      {name:'guidance', at:4200, text:'Detected client noise activates feature matching alongside the original-label signal.'},
      {name:'update', at:7000, text:'Both signals update the local model. The stored label stays unchanged.'}
    ],
    na: [
      {name:'warmup', at:0, text:'Start with ordinary federated training: clients train locally and send model updates.'},
      {name:'scores', at:1800, text:'In one round, clients score local examples with both the shared and local models.'},
      {name:'noise', at:4200, text:'The server uses the returned scores to estimate each client’s label noise.'},
      {name:'aggregation', at:7000, text:'Weight each update by data share × estimated reliability. Reuse these noise estimates in later rounds.'}
    ]
  };

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

    function isVisible() {
      if (document.hidden || !root.isConnected || !intersecting) return false;
      if (root.closest('[hidden], [aria-hidden="true"]')) return false;
      if (!root.getClientRects().length || window.getComputedStyle(root).visibility === 'hidden') return false;
      const bounds = root.getBoundingClientRect();
      return bounds.bottom > 0 && bounds.top < window.innerHeight && bounds.right > 0 && bounds.left < window.innerWidth;
    }

    function updateControls() {
      root.dataset.running = String(playing);
      const subject = selectedMethod ? METHOD_LABELS[selectedMethod] : 'overview';
      const continuing = elapsed > playbackStart && !manual;
      const verb = playing ? 'Pause' : finished ? 'Replay' : continuing ? 'Resume' : 'Play';
      const label = playing || finished || continuing ? verb : selectedMethod ? 'Play animation' : 'Play overview';
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
      description.textContent = returning ? 'Return to the network to explore a different intervention.' : SCENES[name][1];
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
      if (!isVisible()) { pause('Overview paused while out of view. Resume when ready.'); return; }
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
      if (motion.matches) return;
      if (finished || manual) reset(selectedMethod);
      if (!isVisible()) { pause('The overview is paused while out of view.'); return; }
      playing = true;
      lastTime = null;
      root.classList.add('is-touring');
      updateControls();
      status.textContent = (selectedMethod ? METHOD_LABELS[selectedMethod] : 'Overview') + ' playing. Pause or select a method at any time.';
      render();
      frame = window.requestAnimationFrame(tick);
    }

    toggle.addEventListener('click', () => {
      if (playing) pause('Overview paused. Resume or select a method.');
      else play();
    });
    stages.forEach(button => button.addEventListener('click', () => {
      reset(button.dataset.tourStage);
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
      if (motion.matches && PHASES[root.dataset.active]) {
        manual = true;
        showMethod(root.dataset.active);
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
