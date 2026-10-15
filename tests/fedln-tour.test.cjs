// Run with: node tests/fedln-tour.test.cjs
// Real controller, controlled frame clock. Visual layout is checked in-browser.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const source = fs.readFileSync(path.join(__dirname, '..', 'assets', 'fedln-tour.js'), 'utf8');
function setup(reduced = false, options = {}) {
  class El {
    constructor(dataset = {}) { this.dataset = dataset; this.hidden = false; this.style = {}; this.attrs = {}; this.textContent = ''; this.events = {}; this.isConnected = true; this.parentElement = null; const values = new Set(); this.classList = {add: c => values.add(c), remove: c => values.delete(c), contains: c => values.has(c), toggle: (c, on) => on ? values.add(c) : values.delete(c)}; }
    setAttribute(name, value) { this.attrs[name] = value; }
    addEventListener(name, handler) { (this.events[name] ||= []).push(handler); }
    click() { for (const handler of this.events.click || []) handler({}); }
    getClientRects() { return this.displayNone ? [] : [{}]; }
    getBoundingClientRect() { return this.bounds || {top:100,bottom:650,left:10,right:900}; }
    closest() { let n = this; while (n) { if (n.hidden || n.attrs['aria-hidden'] === 'true') return n; n = n.parentElement; } return null; }
  }
  const root = new El({active:'network', running:'false', nncPhase:'complete', akdPhase:'complete', naPhase:'complete'});
  root.parentElement = new El();
  root.parentElement.hidden = Boolean(options.hidden);
  root.bounds = options.bounds;
  const viewport = new El(); viewport.getBoundingClientRect = () => viewport.bounds || root.getBoundingClientRect();
  const nodes = Object.fromEntries(['controls','toggle','toggle-label','play-icon','progress','status','title','description'].map(s => [s,new El()]));
  const stages = ['nnc','akd','na'].map(name => new El({tourStage:name}));
  const panels = ['network','nnc','akd','na'].map(name => new El({tourScene:name}));
  const parts = ['embedding','neighbors','vote','corrected'].map(name => new El({tourNncPart:name,visible:'true'}));
  const akdParts = ['teacher','guidance','update'].map(name => new El({tourAkdPart:name,visible:'true'}));
  const naParts = ['scores','noise','aggregation'].map(name => new El({tourNaPart:name,visible:'true'}));
  const neighbors = Array.from({length:5}, (_, i) => new El({tourNeighbor:String(i+1),visible:'true'}));
  root.querySelector = selector => selector === '.fl-tour-viewport' ? viewport : nodes[selector.slice(11,-1)];
  root.querySelectorAll = selector => ({'[data-tour-stage]':stages,'[data-tour-scene]':panels,'[data-tour-nnc-part]':parts,'[data-tour-akd-part]':akdParts,'[data-tour-na-part]':naParts,'[data-tour-neighbor]':neighbors})[selector] || [];
  const document = new El(); document.hidden = false; document.readyState = 'complete'; document.querySelectorAll = () => [root];
  let id = 0; let now = 0; const frames = new Map(); const timers = new Map(); const observers = [];
  const motion = {matches:reduced,addEventListener(name,handler){this.handler = handler;}};
  const window = new El(); window.innerHeight = 1000; window.innerWidth = 1200;
  window.matchMedia = () => motion; window.getComputedStyle = el => ({visibility:el.visibility || 'visible'});
  window.requestAnimationFrame = callback => { frames.set(++id,callback); return id; };
  window.cancelAnimationFrame = key => frames.delete(key);
  window.setTimeout = (callback,delay) => { timers.set(++id,{callback,at:now+delay}); return id; };
  window.clearTimeout = key => timers.delete(key);
  class IntersectionObserver { constructor(callback) { this.callback = callback; observers.push(this); } observe() {} }
  class MutationObserver { constructor(callback) { this.callback = callback; observers.push(this); } observe() {} }
  if (!options.noIntersection) window.IntersectionObserver = IntersectionObserver; window.MutationObserver = MutationObserver;
  vm.runInNewContext(source,{window,document,IntersectionObserver,MutationObserver});
  return {root,viewport,nodes,stages,panels,parts,akdParts,naParts,neighbors,frames,timers,document,window,motion,observers,
    advance(ms) { now += ms; for (const [key,timer] of [...timers]) { if (timer.at<=now) { timers.delete(key); timer.callback(); } } },
    tick(time) { const list = [...frames.values()]; frames.clear(); list.forEach(callback => callback(time)); },
    event(target,name) { for (const cb of target.events[name] || []) cb(); }};
}
{
 const t = setup();
 assert.equal(t.frames.size,0,'Playback must wait for the visibility delay');
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
 t.tick(36100); assert.equal(t.root.dataset.active,'network');
 t.tick(38100); assert.equal(t.root.dataset.active,'na');
 t.tick(48000);
 assert.equal(t.frames.size,0,'Tour stops after one bounded run');
 assert.equal(t.root.dataset.running,'false');
 assert.equal(t.nodes.toggle.attrs['aria-label'],'Replay overview');
 t.nodes.toggle.click();
 assert.equal(t.root.dataset.active,'network','The single playback button also replays');
 assert.equal(t.frames.size,1,'Replay creates only one frame loop');
 t.stages[0].click();
 assert.equal(t.root.dataset.active,'nnc'); assert.equal(t.frames.size,0,'Method selection stops timed playback');
 assert.equal(t.root.dataset.nncPhase,'complete','Manual NNC shows the full explanation');
 assert.ok(t.parts.every(p=>p.dataset.visible==='true' && p.attrs['aria-hidden']==='false'));
 assert.equal(t.panels.filter(p => !p.hidden).length,1);
 assert.equal(t.stages.filter(p=>p.attrs['aria-pressed']==='true').length,1);
 t.nodes.toggle.click(); assert.equal(t.root.dataset.active,'nnc','Play after choosing a method animates that method directly');
}
// Omitting phase reveals or resetting to the network would make these fail.
for (const [name,stageIndex,partKey,phaseKey,firstPhase] of [
 ['akd',1,'akdParts','akdPhase','example'],
 ['na',2,'naParts','naPhase','warmup']
]) {
 const t = setup();
 t.stages[stageIndex].click();
 assert.ok(t[partKey].every(p=>p.dataset.visible==='true'),'Manual exploration shows the complete method');
 t.nodes.toggle.click(); t.tick(0);
 assert.equal(t.root.dataset.active,name,'Method playback stays in the selected method');
 assert.equal(t.root.dataset[phaseKey],firstPhase);
 assert.ok(t[partKey].every(p=>p.attrs['aria-hidden']==='true'),'The outcome is withheld until its explanation');
 t.tick(2100);
 assert.equal(t[partKey][0].attrs['aria-hidden'],'false');
 assert.equal(t[partKey][2].attrs['aria-hidden'],'true');
 t.tick(4600);
 assert.equal(t[partKey][1].attrs['aria-hidden'],'false');
 assert.equal(t[partKey][2].attrs['aria-hidden'],'true');
 t.tick(7400);
 assert.ok(t[partKey].every(p=>p.attrs['aria-hidden']==='false'));
 t.tick(10000);
 assert.equal(t.root.dataset.active,name,'Single-method playback does not move to another alternative');
 assert.equal(t.root.dataset.running,'false');assert.equal(t.frames.size,0);
 t.nodes.toggle.click(); t.tick(11000);
 assert.equal(t.root.dataset[phaseKey],firstPhase,'Replay restarts this method at its first step');
 t.motion.matches=true;t.motion.handler();
 assert.equal(t.root.dataset[phaseKey],'complete');
 assert.ok(t[partKey].every(p=>p.attrs['aria-hidden']==='false'),'Reduced motion reveals the entire active method');
 assert.equal(t.frames.size,0);
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
 assert.equal(t.frames.size,0,'Returning to view waits before resuming');
 t.advance(1500); assert.equal(t.frames.size,1,'Visibility-paused playback resumes after the delay');
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

// The reader must actually have time to see the diagram, not just pass over it.
{
 const t = setup();
 assert.equal(t.timers.size,1,'One delayed start is armed for a visible overview');
 t.advance(1499); assert.equal(t.frames.size,0);
 t.advance(1); assert.equal(t.frames.size,1,'Autoplay starts after 1.5 seconds');
 t.tick(0); t.tick(4000); const saved = t.nodes.progress.style.transform;
 t.root.bounds={top:-540,bottom:10,left:10,right:900};
 t.event(t.window,'scroll');
 assert.equal(t.frames.size,0,'A tiny remaining sliver is not in focus');
 t.tick(30000); assert.equal(t.nodes.progress.style.transform,saved);
 t.root.bounds=undefined;t.event(t.window,'scroll');
 t.event(t.window,'resize'); t.observers[0].callback([{isIntersecting:true}]);
 assert.equal(t.timers.size,1,'Repeated observer and scroll events do not duplicate the timer');
 t.advance(1500); t.tick(30001); assert.equal(t.nodes.progress.style.transform,saved,'No time jump on return');
 t.tick(31001); assert.notEqual(t.nodes.progress.style.transform,saved);
 t.nodes.toggle.click(); t.event(t.window,'scroll'); t.advance(5000);
 assert.equal(t.frames.size,0,'Manual pause suppresses automatic resumption');
}
for (const noIntersection of [false,true]) {
 const t = setup(false,{noIntersection}); t.advance(900);
 t.root.bounds={top:1100,bottom:1650,left:10,right:900};t.event(t.window,'scroll');
 assert.equal(t.timers.size,0,'Leaving before the delay cancels autoplay');t.advance(3000);
 assert.equal(t.frames.size,0);
 t.root.bounds=undefined;t.event(t.window,'scroll');t.advance(1499);
 assert.equal(t.frames.size,0,'Returning requires a new uninterrupted delay');
 t.advance(1);assert.equal(t.frames.size,1,'Scroll fallback also starts autoplay');
}
{
 const t = setup(false,{hidden:true});t.advance(5000);
 assert.equal(t.timers.size,0);assert.equal(t.frames.size,0,'Deep links into other panels must not autoplay');
 t.root.parentElement.hidden=false;t.observers[1].callback([]);t.advance(1500);
 assert.equal(t.frames.size,1);
 t.tick(0);t.tick(40000);t.event(t.window,'scroll');t.advance(5000);
 assert.equal(t.frames.size,0,'Finished tours do not restart automatically');
}
{
 const t = setup();t.advance(700);t.stages[1].click();t.advance(5000);
 assert.equal(t.frames.size,0,'Selecting a method cancels pending autoplay');
 assert.equal(t.root.dataset.akdPhase,'complete');
}
for (const [out,back] of [['blur','focus'],['pagehide','pageshow']]) {
 const t=setup();t.advance(1500);t.tick(0);t.tick(2000);
 t.event(t.window,out);assert.equal(t.frames.size,0);
 t.event(t.window,back);t.advance(1500);assert.equal(t.frames.size,1);
}
{
 const t=setup(true);t.advance(5000);
 assert.equal(t.timers.size,0);assert.equal(t.frames.size,0,'Reduced motion never autoplays');
 const p=setup();p.advance(700);p.motion.matches=true;p.motion.handler();p.advance(5000);
 assert.equal(p.frames.size,0,'Reduced motion also cancels a pending start');
 p.motion.matches=false;p.motion.handler();p.advance(5000);
 assert.equal(p.frames.size,0,'Removing reduced motion does not unexpectedly start a tour');
}

{
 const t=setup();t.viewport.bounds={top:1000,bottom:1400,left:10,right:900};
 t.event(t.window,'scroll');t.advance(5000);
 assert.equal(t.frames.size,0,'Visible controls alone must not start an offscreen illustration');
 t.viewport.bounds={top:300,bottom:700,left:10,right:900};t.event(t.window,'scroll');t.advance(1500);
 assert.equal(t.frames.size,1);
}
console.log('PASS: delayed visible autoplay, camera focus, three progressive explanations, selected-method playback, pause/resume, alternatives, one-shot replay, manual views, visibility lifecycle, reduced motion.');
{
 const t=setup();t.stages[0].click();
 t.viewport.bounds={top:995,bottom:1600,left:10,right:900};
 t.nodes.toggle.click();assert.equal(t.frames.size,0);
 t.viewport.bounds=null;t.event(t.window,'scroll');t.advance(1500);
 assert.equal(t.frames.size,1,'Remember explicit Play until the selected method is visible');
}
{
 const t=setup();t.stages[0].click();
 t.viewport.bounds={top:995,bottom:1600,left:10,right:900};
 t.nodes.toggle.click();t.nodes.toggle.click();
 t.viewport.bounds=null;t.event(t.window,'scroll');t.advance(2000);
 assert.equal(t.frames.size,0,'Cancel an explicit queued play request');
}
