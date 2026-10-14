// Run with: node tests/fedln-tour.test.cjs
// Exercise the real browser controller with a controlled DOM and frame clock.
// This harness covers lifecycle behavior; rendered layout is checked in-browser.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const source = fs.readFileSync(path.join(__dirname, '..', 'assets', 'fedln-tour.js'), 'utf8');
function setup(reduced = false) {
  class El {
    constructor(dataset = {}) { this.dataset = dataset; this.hidden = false; this.style = {}; this.attrs = {}; this.textContent = ''; this.events = {}; this.isConnected = true; this.parentElement = null; const values = new Set(); this.classList = {add: c => values.add(c), remove: c => values.delete(c), contains: c => values.has(c), toggle: (c, on) => on ? values.add(c) : values.delete(c)}; }
    setAttribute(name, value) { this.attrs[name] = value; }
    addEventListener(name, handler) { (this.events[name] ||= []).push(handler); }
    click() { for (const handler of this.events.click || []) handler({}); }
    getClientRects() { return this.displayNone ? [] : [{}]; }
    getBoundingClientRect() { return this.bounds || {top:100,bottom:650,left:10,right:900}; }
    closest() { let n = this; while (n) { if (n.hidden || n.attrs['aria-hidden'] === 'true') return n; n = n.parentElement; } return null; }
  }
  const root = new El({active:'network', running:'false'});
  root.parentElement = new El();
  const selectors = ['controls','toggle','toggle-label','play-icon','replay','replay-label','duration','progress','status','title','description','kicker'];
  const nodes = Object.fromEntries(selectors.map(s => [s,new El()]));
  const stages = ['network','nnc','akd','na'].map(name => new El({tourStage:name}));
  const panels = ['network','nnc','akd','na'].map(name => new El({tourScene:name}));
  root.querySelector = selector => nodes[selector.slice(11,-1)];
  root.querySelectorAll = selector => selector === '[data-tour-stage]' ? stages : panels;
  const document = new El(); document.hidden = false; document.readyState = 'complete'; document.querySelectorAll = () => [root];
  let id = 0; const frames = new Map(); const observers = [];
  const motion = {matches:reduced,addEventListener(name,handler){this.handler = handler;}};
  const window = new El(); window.innerHeight = 1000; window.innerWidth = 1200;
  window.matchMedia = () => motion; window.getComputedStyle = el => ({visibility:el.visibility || 'visible'});
  window.requestAnimationFrame = callback => { frames.set(++id,callback); return id; };
  window.cancelAnimationFrame = key => frames.delete(key);
  class IntersectionObserver { constructor(callback) { this.callback = callback; observers.push(this); } observe() {} }
  class MutationObserver { constructor(callback) { this.callback = callback; observers.push(this); } observe() {} }
  window.IntersectionObserver = IntersectionObserver; window.MutationObserver = MutationObserver;
  vm.runInNewContext(source,{window,document,IntersectionObserver,MutationObserver});
  return {root,nodes,stages,panels,frames,document,window,motion,observers,
    tick(time) { const list = [...frames.values()]; frames.clear(); list.forEach(callback => callback(time)); },
    event(target,name) { for (const cb of target.events[name] || []) cb(); }};
}
{
 const t = setup();
 assert.equal(t.frames.size,0,'Initial view must not autoplay');
 assert.equal(t.root.dataset.active,'network');
 assert.equal(t.nodes['toggle-label'].textContent,'Play tour');
 t.nodes.toggle.click(); t.tick(0); t.tick(3451);
 assert.equal(t.root.dataset.active,'nnc','First method must be NNC');
 t.nodes.toggle.click(); const saved = t.nodes.progress.style.transform;
 assert.equal(t.frames.size,0,'Pause cancels the frame loop');
 assert.equal(t.root.dataset.running,'false');
 t.nodes.toggle.click(); t.tick(4000); t.tick(10000);
 assert.equal(t.root.dataset.active,'network','Tour returns to network between alternatives');
 assert.notEqual(t.nodes.progress.style.transform,saved);
 t.tick(12251); assert.equal(t.root.dataset.active,'akd');
 t.tick(18251); assert.equal(t.root.dataset.active,'network');
 t.tick(20501); assert.equal(t.root.dataset.active,'na');
 t.tick(40000);
 assert.equal(t.frames.size,0,'Tour stops after one bounded run');
 assert.equal(t.root.dataset.running,'false');
 assert.equal(t.nodes['toggle-label'].textContent,'Replay tour');
 assert.match(t.nodes.status.textContent,/Tour complete/);
 t.stages[1].click();
 assert.equal(t.root.dataset.active,'nnc'); assert.equal(t.frames.size,0,'Stage selection is manual');
 assert.equal(t.panels.filter(p => !p.hidden).length,1);
}
for (const reason of ['document','intersection','ancestor']) {
 const t = setup(); t.nodes.toggle.click(); t.tick(0); t.tick(4000);
 if (reason === 'document') { t.document.hidden = true; t.event(t.document,'visibilitychange'); }
 if (reason === 'intersection') t.observers[0].callback([{isIntersecting:false}]);
 if (reason === 'ancestor') { t.root.parentElement.hidden = true; t.observers[1].callback([]); }
 assert.equal(t.frames.size,0,reason+' hiding must cancel animation');
 assert.equal(t.root.dataset.running,'false');
 t.document.hidden = false; t.root.parentElement.hidden = false;
 t.observers[0].callback([{isIntersecting:true}]);
 assert.equal(t.frames.size,0,'Returning to view must not auto-resume');
}
{
 const t = setup(true);
 assert.equal(t.nodes.toggle.hidden,true,'Reduced motion has no timed Play control');
 assert.equal(t.frames.size,0);
 t.stages[2].click(); assert.equal(t.root.dataset.active,'akd'); assert.equal(t.frames.size,0);
 t.nodes.replay.click(); assert.equal(t.root.dataset.active,'network'); assert.equal(t.frames.size,0);
}
{
 const t = setup(); t.nodes.toggle.click(); t.tick(0); t.tick(4000);
 t.motion.matches = true; t.motion.handler();
 assert.equal(t.frames.size,0,'A live reduced-motion preference change stops playback');
 assert.equal(t.root.dataset.running,'false');
}
{
 const t = setup(); t.nodes.toggle.click(); t.tick(0); t.tick(4000);
 t.nodes.replay.click();
 assert.equal(t.root.dataset.active,'network','Replay returns to the overview');
 assert.equal(t.frames.size,1,'Replay replaces the previous frame loop');
 t.tick(5000); t.nodes.toggle.click();
 assert.equal(t.frames.size,0);
}
console.log('PASS: manual initial state, sequence/returns, pause/resume, one-shot completion, stage selection, hidden/offscreen stops, no auto-resume, reduced motion.');
