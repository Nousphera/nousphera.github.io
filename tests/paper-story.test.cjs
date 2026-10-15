const fs=require('fs');const path=require('path');const vm=require('vm');const assert=require('assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../assets/paper-story.js'),'utf8');
function setup({reduced=false,hidden=false,durations=[]}={}){
 class El{
  constructor(dataset={}){this.dataset=dataset;this.attrs={};this.events={};this.hidden=false;this.isConnected=true;this.textContent='Step';this.style={setProperty(k,v){this[k]=v;}};this.classList={add(){}};}
  setAttribute(k,v){this.attrs[k]=v;}addEventListener(k,cb){(this.events[k]||=[]).push(cb);}click(){(this.events.click||[]).forEach(cb=>cb());}
  getClientRects(){return [{}];}getBoundingClientRect(){return this.bounds||{top:100,bottom:500,left:0,right:800};}
  closest(){return this.parentElement?.hidden?this.parentElement:null;}
 }
 const root=new El();root.parentElement=new El();root.parentElement.hidden=hidden;
 const nodes=Object.fromEntries(['controls','toggle','toggle-label','progress','status','prev','next','counter'].map(k=>[k,new El()]));
 const viewport=new El();const parts=Array.from({length:4},()=>[new El({reveal:'0'}),new El({reveal:'1800'}),new El({reveal:'3600'})]);
 const panels=parts.map((p,i)=>{const e=new El({storyScene:String(i),storyDuration:durations[i]});e.querySelectorAll=()=>p;return e;});
 const steps=panels.map((p,i)=>new El({storyStep:String(i)}));
 root.querySelector=s=>s==='.story-viewport'?viewport:nodes[s.slice(12,-1)];
 root.querySelectorAll=s=>s==='[data-story-scene]'?panels:steps;
 const document=new El();document.readyState='complete';document.querySelectorAll=()=>[root];document.hidden=false;
 let id=0,now=0;const frames=new Map(),timers=new Map(),observers=[];
 const window=new El();window.innerHeight=900;window.innerWidth=1000;window.getComputedStyle=()=>({visibility:'visible'});
 const motion={matches:reduced,addEventListener(k,cb){this.change=cb;}};window.matchMedia=()=>motion;
 window.requestAnimationFrame=cb=>{frames.set(++id,cb);return id;};window.cancelAnimationFrame=i=>frames.delete(i);
 window.setTimeout=(cb,delay)=>{timers.set(++id,{cb,at:now+delay});return id;};window.clearTimeout=i=>timers.delete(i);
 class Observer{constructor(cb){this.callback=cb;observers.push(this);}observe(){}}
 window.IntersectionObserver=Observer;window.MutationObserver=Observer;
 vm.runInNewContext(source,{window,document,IntersectionObserver:Observer,MutationObserver:Observer});
 return {root,nodes,viewport,parts,panels,steps,document,window,motion,frames,timers,observers,
 advance(ms){now+=ms;for(const[i,t]of [...timers])if(t.at<=now){timers.delete(i);t.cb();}},
 tick(t){const cbs=[...frames.values()];frames.clear();cbs.forEach(cb=>cb(t));},
 event(target,name){(target.events[name]||[]).forEach(cb=>cb());}};
}
{
 const t=setup();assert.equal(t.frames.size,0);t.advance(1499);assert.equal(t.frames.size,0);t.advance(1);assert.equal(t.frames.size,1);
 t.tick(0);assert.equal(t.parts[0][2].dataset.revealed,'false');t.tick(2000);assert.equal(t.parts[0][1].dataset.revealed,'true');assert.equal(t.parts[0][2].dataset.revealed,'false');
 t.tick(4000);assert.equal(t.parts[0][2].dataset.revealed,'true');t.tick(6500);assert.equal(t.root.dataset.active,'1');
 t.nodes.toggle.click();const saved=t.nodes.progress.style.transform;t.tick(100000);assert.equal(t.nodes.progress.style.transform,saved);assert.equal(t.frames.size,0);
 t.event(t.window,'scroll');t.advance(5000);assert.equal(t.frames.size,0,'Manual pause overrides autoplay');
 t.nodes.toggle.click();t.tick(110000);t.tick(111000);assert.equal(t.root.dataset.active,'1','Resume excludes paused wall time');
 t.tick(130000);assert.equal(t.root.dataset.active,'3');assert.equal(t.nodes['toggle-label'].textContent,'Replay overview');assert.equal(t.frames.size,0);
 t.event(t.window,'scroll');t.advance(5000);assert.equal(t.frames.size,0,'No automatic loop');t.nodes.toggle.click();assert.equal(t.root.dataset.active,'0');
}
for(const reason of ['scroll','tab','hidden','blur','pagehide']){
 const t=setup();t.advance(1500);t.tick(0);t.tick(2200);
 if(reason==='scroll'){t.viewport.bounds={top:899,bottom:1300,left:0,right:800};t.event(t.window,'scroll');}
 if(reason==='tab'){t.root.parentElement.hidden=true;t.observers[1].callback();}
 if(reason==='hidden'){t.document.hidden=true;t.event(t.document,'visibilitychange');}
 if(reason==='blur')t.event(t.window,'blur');if(reason==='pagehide')t.event(t.window,'pagehide');
 assert.equal(t.frames.size,0,reason+' must pause');
 t.viewport.bounds=null;t.root.parentElement.hidden=false;t.document.hidden=false;
 t.event(t.window,'focus');t.event(t.window,'pageshow');t.event(t.document,'visibilitychange');t.event(t.window,'scroll');
 assert.equal(t.frames.size,0);assert.equal(t.timers.size,1,'Exactly one delayed resume');t.advance(1500);assert.equal(t.frames.size,1);t.tick(30000);assert.equal(t.root.dataset.active,'0','Time outside viewport is not consumed');
}
{
 const t=setup({hidden:true});t.advance(5000);assert.equal(t.frames.size,0);t.root.parentElement.hidden=false;t.observers[1].callback();t.advance(1500);assert.equal(t.frames.size,1);
 t.steps[2].click();assert.equal(t.frames.size,0);assert.ok(t.parts[2].every(p=>p.dataset.revealed==='true'));assert.equal(t.panels.filter(p=>!p.hidden).length,1);t.event(t.window,'scroll');t.advance(5000);assert.equal(t.frames.size,0);t.nodes.toggle.click();assert.equal(t.root.dataset.active,'2');assert.equal(t.parts[2][2].dataset.revealed,'false');
 t.motion.matches=true;t.motion.change();assert.equal(t.frames.size,0);assert.equal(t.nodes.toggle.hidden,true);assert.ok(t.parts[2].every(p=>p.dataset.revealed==='true'));
}
{
 const t=setup({reduced:true});t.advance(9000);assert.equal(t.frames.size,0);assert.equal(t.nodes.toggle.hidden,true);t.steps[3].click();assert.ok(t.parts[3].every(p=>p.dataset.revealed==='true'));
}
{
 const t=setup();t.viewport.bounds={top:895,bottom:1300,left:0,right:800};t.event(t.window,'scroll');t.advance(5000);assert.equal(t.frames.size,0,'A sliver of artwork must not trigger autoplay');
}
console.log('Paper stories: bounded playback, reveals, pause/resume, manual override, visibility, reduced motion passed.');

{
 const t=setup({durations:[7000,8000,11000,6000]});t.advance(1500);t.tick(0);t.tick(6500);
 assert.equal(t.root.dataset.active,'0','Longer scenes must not cut off at the old six-second boundary');
 t.tick(7500);assert.equal(t.root.dataset.active,'1');
 t.nodes.next.click();assert.equal(t.root.dataset.active,'2');assert.equal(t.frames.size,0);
 assert.equal(t.nodes.counter.textContent,'3 / 4');
 t.nodes.prev.click();assert.equal(t.root.dataset.active,'1');
 t.nodes.toggle.click();t.tick(20000);t.tick(27999);assert.equal(t.root.dataset.active,'1');
 t.tick(28001);assert.equal(t.root.dataset.active,'2');
}
