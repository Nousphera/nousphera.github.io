/* Bounded, visible-only method stories. Full static artwork is the fallback. */
(function () {
  'use strict';
  const DELAY = 1500;
  const STEP_MS = 6000;
  function initialize(root) {
    if (root.dataset.storyReady === 'true') return;
    const q = s => root.querySelector(s);
    const panels = [...root.querySelectorAll('[data-story-scene]')];
    const steps = [...root.querySelectorAll('[data-story-step]')];
    const controls = q('[data-story-controls]');
    const toggle = q('[data-story-toggle]');
    const toggleLabel = q('[data-story-toggle-label]');
    const viewport = q('.story-viewport');
    const progress = q('[data-story-progress]');
    const status = q('[data-story-status]');
    if (!panels.length || panels.length !== steps.length || !toggle || !controls || !viewport) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const parts = panels.map(panel => [...panel.querySelectorAll('[data-reveal]')]);
    const durations = panels.map(panel => {
      const value=Number(panel.dataset.storyDuration);
      return Number.isFinite(value) && value>=5000 && value<=20000 ? value : STEP_MS;
    });
    const starts=[];
    const total=durations.reduce((sum,duration) => {starts.push(sum);return sum+duration;},0);
    const previous=q('[data-story-prev]'), next=q('[data-story-next]'), counter=q('[data-story-counter]');
    let elapsed = 0, last = null, frame = null, timer = null, active = -1;
    let playing = false, complete = false, pending = true, resume = false;
    let intersecting = true, pageActive = true, focused = true, selected = false;

    function visible() {
      if (document.hidden || !pageActive || !focused || !root.isConnected || !intersecting || root.closest('[hidden], [aria-hidden="true"]')) return false;
      if (!root.getClientRects().length || window.getComputedStyle(root).visibility === 'hidden') return false;
      const b = viewport.getBoundingClientRect();
      const height = Math.min(b.bottom, window.innerHeight) - Math.max(b.top, 0);
      const required = Math.min(b.bottom-b.top,window.innerHeight)*.35;
      return required>0 && height>=required && b.right>0 && b.left<window.innerWidth;
    }
    function cancelTimer() { if (timer !== null) window.clearTimeout(timer); timer = null; }
    function updateControls() {
      root.dataset.running = String(playing);
      const label = playing ? 'Pause' : complete ? 'Replay overview' : selected ? 'Play from here' : elapsed>0 ? 'Resume' : 'Play overview';
      toggleLabel.textContent = label;
      toggle.setAttribute('aria-label', label + (playing ? ' overview' : ''));
    }
    function reveal(index,time=null) {
      parts[index].forEach(part => {
        const on = time===null || time>=Number(part.dataset.reveal);
        part.dataset.revealed = String(on);
        part.setAttribute('aria-hidden',String(!on));
      });
    }
    function show(index, time=null, announce=false) {
      if (active !== index) {
        active = index;
        root.dataset.active = String(index);
        panels.forEach((panel,i) => { panel.hidden=i!==index; });
        steps.forEach((step,i) => { step.setAttribute('aria-pressed',String(i===index)); });
        if (previous) previous.disabled=index===0;
        if (next) next.disabled=index===panels.length-1;
        if (counter) counter.textContent=(index+1)+' / '+panels.length;
        // Scroll only the horizontal control strip, never the document.
        const button=steps[index];
        if (controls.scrollWidth>controls.clientWidth) {
          const left=button.offsetLeft-controls.offsetLeft;
          if (left<controls.scrollLeft) controls.scrollLeft=left;
          else if (left+button.offsetWidth>controls.scrollLeft+controls.clientWidth) controls.scrollLeft=left+button.offsetWidth-controls.clientWidth;
        }
        if (announce) status.textContent='Step '+(index+1)+' of '+panels.length+': '+steps[index].textContent.trim();
      }
      reveal(index,time);
      progress.style.transform='scaleX('+Math.min(1,elapsed/total)+')';
    }
    function render() {
      let index=starts.findIndex((start,i) => elapsed<start+durations[i]);
      if (index===-1) index=panels.length-1;
      show(index,elapsed-starts[index],true);
    }
    function pause() {
      if (frame!==null) window.cancelAnimationFrame(frame);
      frame=null; last=null; playing=false; updateControls();
    }
    function tick(time) {
      if (!playing) return;
      if (!visible()) { visibilityChanged(); return; }
      if (last!==null) elapsed+=Math.max(0,time-last);
      last=time; elapsed=Math.min(elapsed,total); render();
      if (elapsed>=total) {
        complete=true; resume=false; reveal(panels.length-1); pause();
        status.textContent='Overview complete. Select any step to explore it again.';
        return;
      }
      frame=window.requestAnimationFrame(tick);
    }
    function play() {
      if (playing || motion.matches) return;
      cancelTimer(); pending=false; resume=false;
      if (!visible()) return;
      if (complete) { elapsed=0; complete=false; active=-1; }
      selected=false; playing=true; last=null; updateControls(); render();
      frame=window.requestAnimationFrame(tick);
    }
    function takeControl() { cancelTimer();pending=false;resume=false; }
    function visibilityChanged() {
      if (!visible()) {
        cancelTimer();
        if (playing) { resume=true; pause(); }
        return;
      }
      if (motion.matches || playing || complete || timer!==null || (!pending && !resume)) return;
      timer=window.setTimeout(() => {
        timer=null;
        if (visible() && !motion.matches && !complete && (pending||resume)) play();
      },DELAY);
    }
    const expand=q('[data-story-expand]');
    const dialog=q('[data-story-dialog]');
    if (expand && dialog && typeof dialog.showModal==='function') {
      expand.hidden=false;
      expand.addEventListener('click',() => {
        takeControl();pause();
        const picture=panels[active].querySelector('.story-art').cloneNode(true);
        picture.querySelectorAll('[data-reveal]').forEach(part => {part.dataset.revealed='true';part.setAttribute('aria-hidden','false');});
        q('[data-story-expanded]').replaceChildren(picture);
        q('[data-story-expanded-caption]').textContent=[...panels[active].querySelector('figcaption').children].map(node=>node.textContent).join(' — ');
        dialog.showModal();
      });
      q('[data-story-close]').addEventListener('click',() => dialog.close());
    }
    toggle.addEventListener('click',() => { takeControl(); if (playing) pause(); else play(); });
    function select(index) {
      if (index<0 || index>=panels.length) return;
      takeControl();pause();elapsed=starts[index];complete=false;selected=true;
      show(index,null,true);updateControls();
    }
    steps.forEach((button,index) => button.addEventListener('click',() => select(index)));
    if (previous) previous.addEventListener('click',() => select(active-1));
    if (next) next.addEventListener('click',() => select(active+1));
    const navigation=q('[data-story-navigation]');
    if (navigation) navigation.hidden=false;
    document.addEventListener('visibilitychange',visibilityChanged);
    window.addEventListener('scroll',visibilityChanged,{passive:true});
    window.addEventListener('resize',visibilityChanged,{passive:true});
    window.addEventListener('pagehide',() => {pageActive=false;visibilityChanged();});
    window.addEventListener('pageshow',() => {pageActive=true;visibilityChanged();});
    window.addEventListener('blur',() => {focused=false;visibilityChanged();});
    window.addEventListener('focus',() => {focused=true;visibilityChanged();});
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {intersecting=entries[0].isIntersecting;visibilityChanged();},{threshold:[0,.15,.35,.5]}).observe(root);
    }
    if ('MutationObserver' in window) {
      const observer=new MutationObserver(visibilityChanged);
      let ancestor=root.parentElement;
      while (ancestor) {observer.observe(ancestor,{attributes:true,attributeFilter:['hidden','aria-hidden','class','style']});ancestor=ancestor.parentElement;}
    }
    function motionChanged() {
      if (motion.matches) {takeControl();pause();show(Math.max(0,active));}
      toggle.hidden=motion.matches;
      visibilityChanged();
    }
    if (motion.addEventListener) motion.addEventListener('change',motionChanged);
    else if (motion.addListener) motion.addListener(motionChanged);
    root.dataset.storyReady='true';root.classList.add('is-enhanced');
    root.style.setProperty('--story-count',String(steps.length));
    controls.hidden=false;toggle.hidden=motion.matches;show(0);updateControls();motionChanged();
  }
  function boot() {document.querySelectorAll('[data-paper-story]').forEach(initialize);}
  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot,{once:true});
  else boot();
})();
