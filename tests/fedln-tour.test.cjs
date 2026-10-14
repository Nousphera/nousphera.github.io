// Run with: node tests/fedln-tour.test.cjs
// Real controller, controlled frame clock. Visual layout is checked in-browser.
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
  const root = new El({active:'network', running:'false', nncPhase:'complete'});
  root.parentElement = new El();
  const nodes = Object.fromEntries(['controls','toggle','toggle-label','play-icon','progress','status','title','description'].map(s => [s,new El()]));
  const stages = ['nnc','akd','na'].map(name => new El({tourStage:name}));
  const panels = ['network','nnc','akd','na'].map(name => new El({tourScene:name}));
  const parts = ['embedding','neighbors','vote','corrected'].map(name => new El({tourNncPart:name,visible:'true'}));
  const neighbors = Array.from({length:5}, (_, i) => new El({tourNeighbor:String(i+1),visible:'true'}));
  root.querySelector = selector => nodes[selector.slice(11,-1)];
  root.querySelectorAll = selector => ({'[data-tour-stage]':stages,'[data-tour-scene]':panels,'[data-tour-nnc-part]':parts,'[data-tour-neighbor]':neighbors})[selector] || [];
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
  return {root,nodes,stages,panels,parts,neighbors,frames,document,window,motion,observers,
    tick(time) { const list = [...frames.values()]; frames.clear(); list.forEach(callback => callback(time)); },
    event(target,name) { for (const cb of target.events[name] || []) cb(); }};
}
{
 const t = setup();
 assert.equal(t.frames.size,0,'Initial view must not autoplay');
 assert.equal(t.root.dataset.active,'network');
 assert.equal(t.nodes['toggle-label'].textContent,'Play overview');
 t.nodes.toggle.click(); t.tick(0); t.tick(3100);
 assert.equal(t.root.dataset.camera,'nnc','Tour focuses the first client before opening NNC');
 t.tick(3600);
 assert.equal(t.root.dataset.active,'nnc');
 assert.equal(t.root.dataset.nncPhase,'sample','NNC starts with the wrong label, not the correction');
 assert.equal(t.parts.find(p=>p.dataset.tourNncPart==='corrected').attrs['aria-hidden'],'true');
 const announcement = t.nodes.status.textContent;
 t.tick(5400); assert.equal(t.root.dataset.nncPhase,'embedding');
 t.tick(7200); assert.equal(t.root.dataset.nncPhase,'neighbors');
 t.tick(8500); assert.equal(t.neighbors.filter(n=>n.dataset.visible==='true').length,5,'Five OTHER examples are shown before voting');
 t.tick(9600); assert.equal(t.root.dataset.nncPhase,'vote');
 assert.equal(t.nodes.status.textContent,announcement,'Subphases do not repeatedly interrupt screen readers');
 t.nodes.toggle.click(); const saved = t.nodes.progress.style.transform;
 assert.equal(t.frames.size,0,'Pause cancels the frame loop');
 t.tick(20000); assert.equal(t.nodes.progress.style.transform,saved,'Pause freezes progress and label state');
 assert.equal(t.root.dataset.nncPhase,'vote');
 t.nodes.toggle.click(); t.tick(21000); t.tick(23000);
 assert.equal(t.root.dataset.nncPhase,'corrected');
 assert.equal(t.parts.find(p=>p.dataset.tourNncPart==='corrected').attrs['aria-hidden'],'false');
 t.tick(24500); assert.equal(t.root.dataset.active,'network','Return to the network separates alternatives');
 t.tick(26600); assert.equal(t.root.dataset.active,'akd');
 t.tick(32100); assert.equal(t.root.dataset.active,'network');
 t.tick(34100); assert.equal(t.root.dataset.active,'na');
 t.tick(40000);
 assert.equal(t.frames.size,0,'Tour stops after one bounded run');
 assert.equal(t.root.dataset.running,'false');
 assert.equal(t.nodes['toggle-label'].textContent,'Replay overview');
 t.nodes.toggle.click();
 assert.equal(t.root.dataset.active,'network','The single playback button also replays');
 assert.equal(t.frames.size,1,'Replay creates only one frame loop');
 t.stages[0].click();
 assert.equal(t.root.dataset.active,'nnc'); assert.equal(t.frames.size,0,'Method selection stops timed playback');
 assert.equal(t.root.dataset.nncPhase,'complete','Manual NNC shows the full explanation');
 assert.ok(t.parts.every(p=>p.dataset.visible==='true' && p.attrs['aria-hidden']==='false'));
 assert.equal(t.panels.filter(p => !p.hidden).length,1);
 assert.equal(t.stages.filter(p=>p.attrs['aria-pressed']==='true').length,1);
 t.nodes.toggle.click(); assert.equal(t.root.dataset.active,'network','Play after manual exploration starts at the overview');
}
for (const reason of ['document','intersection','ancestor','removed']) {
 const t = setup(); t.nodes.toggle.click(); t.tick(0); t.tick(4000);
 if (reason === 'document') { t.document.hidden = true; t.event(t.document,'visibilitychange'); }
 if (reason === 'intersection') t.observers[0].callback([{isIntersecting:false}]);
 if (reason === 'ancestor') { t.root.parentElement.hidden = true; t.observers[1].callback([]); }
 if (reason === 'removed') { t.root.isConnected = false; t.tick(4100); }
 assert.equal(t.frames.size,0,reason+' hiding must cancel animation');
 assert.equal(t.root.dataset.running,'false');
 t.document.hidden = false; t.root.parentElement.hidden = false; t.root.isConnected = true;
 t.observers[0].callback([{isIntersecting:true}]);
 assert.equal(t.frames.size,0,'Returning to view must not auto-resume');
}
{
 const t = setup(true);
 assert.equal(t.nodes.toggle.hidden,true,'Reduced motion has no timed Play control');
 assert.equal(t.frames.size,0);
 for (const [i,name] of ['nnc','akd','na'].entries()) {
   t.stages[i].click(); assert.equal(t.root.dataset.active,name); assert.equal(t.frames.size,0);
 }
 t.stages[0].click(); assert.equal(t.root.dataset.nncPhase,'complete');
}
{
 const t = setup(); t.nodes.toggle.click(); t.tick(0); t.tick(4000);
 t.motion.matches = true; t.motion.handler();
 assert.equal(t.frames.size,0,'A live reduced-motion preference change stops playback');
 assert.equal(t.root.dataset.nncPhase,'complete','Reduced motion exposes a complete static explanation');
 t.motion.matches = false; t.motion.handler();
 assert.equal(t.frames.size,0,'Changing preferences never starts playback');
}
console.log('PASS: opt-in playback, camera focus, NNC progressive explanation, pause/resume, alternatives, one-shot replay, manual views, visibility lifecycle, reduced motion.');
