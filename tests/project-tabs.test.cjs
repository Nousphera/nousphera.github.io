const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
function setup(hash = '') {
  const ids = ['overview', 'method', 'findings', 'citation'];
  const events = {}, documentEvents = {}, history = [];
  function element(id) { return {id, hidden:false, attributes:{}, handlers:{}, focused:false, tabIndex:0,
    setAttribute(k,v) {this.attributes[k]=v;}, addEventListener(k,fn) {this.handlers[k]=fn;}, focus(options){this.focused=true;this.focusOptions=options;},
    scrollIntoView(){this.scrolled=true;}, closest(){return this;} }; }
  const panels=ids.map(element);
  panels.forEach(p=>p.getBoundingClientRect=()=>({top:85}));
  const tabs=ids.map(id => {const e=element('');e.getAttribute=()=> '#'+id;return e;});
  const tabList=element('tabs');tabList.querySelectorAll=()=>tabs;
  tabList.classList={add(c){this.value=c;}};tabList.getBoundingClientRect=()=>({top:25,height:60,bottom:85});
  const child=element('result-1');child.closest=()=>panels[2];
  const context={document:{querySelector:()=>tabList,querySelectorAll:()=>panels,getElementById:id=>panels.find(p=>p.id===id)||(id==='result-1'?child:null),addEventListener(k,fn){documentEvents[k]=fn;}},
    window:{location:{hash},scrollY:100,history:{pushState(a,b,url){context.window.location.hash=url;history.push(url);}},scrollTo(args){this.scroll=args;},addEventListener(k,fn){events[k]=fn;}}};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../assets/project-tabs.js'),'utf8'),context);
  function click(i,extra={}) {const event={target:tabs[i],button:0,preventDefault(){this.prevented=true;},...extra};documentEvents.click(event);return event;}
  function key(i,key) {let prevented=false;tabs[i].handlers.keydown({key,preventDefault(){prevented=true;}});return prevented;}
  return {panels,tabs,tabList,events,history,context,click,key,child};
}
test('direct result links select one section and set accessible tab semantics',()=>{
  const s=setup('#findings');
  assert.deepEqual(s.panels.map(p=>p.hidden),[true,true,false,true]);
  assert.equal(s.tabs[2].attributes['aria-selected'],'true');
  assert.equal(s.tabs[2].attributes['aria-controls'],'findings');
  assert.equal(s.panels[2].attributes['aria-labelledby'],'tab-findings');
  assert.equal(s.panels[2].attributes.role,'tabpanel');
  assert.deepEqual(s.tabs.map(t=>t.tabIndex),[-1,-1,0,-1]);
});
test('clicking a tab updates history, focus and compact panel visibility',()=>{
  const s=setup(); assert.equal(s.click(3).prevented,true);
  assert.deepEqual(s.panels.map(p=>p.hidden),[true,true,true,false]);
  assert.deepEqual(s.history,['#citation']); assert.equal(s.tabs[3].focused,true);
  assert.equal(s.context.window.scroll,undefined, 'normal tab switches must not move the document');
  assert.equal(s.tabs[3].focusOptions.preventScroll,true);
});
test('keyboard arrows wrap and Home/End move between sections',()=>{
  const s=setup(); assert.equal(s.key(0,'ArrowLeft'),true);
  assert.equal(s.panels[3].hidden,false);
  s.key(3,'Home'); assert.equal(s.panels[0].hidden,false);
  s.key(0,'End'); assert.equal(s.panels[3].hidden,false);
  s.key(3,'ArrowRight'); assert.equal(s.panels[0].hidden,false);
  assert.equal(s.key(0,'Tab'),false);
});
test('browser history, nested anchors and malformed fragments remain usable',()=>{
  const s=setup('#result-1'); assert.equal(s.panels[2].hidden,false);assert.equal(s.child.scrolled,true);
  s.context.window.location.hash='#method';s.events.popstate();assert.equal(s.panels[1].hidden,false);
  s.context.window.location.hash='#%invalid';s.events.hashchange();assert.equal(s.panels[0].hidden,false);
});
test('modified clicks keep native behavior and printing exposes every section',()=>{
  const s=setup('#method'); assert.notEqual(s.click(3,{metaKey:true}).prevented,true);
  assert.equal(s.panels[1].hidden,false);
  s.events.beforeprint();assert.ok(s.panels.every(p=>!p.hidden));
  s.events.afterprint();assert.deepEqual(s.panels.map(p=>p.hidden),[true,false,true,true]);
});

test('switching after a deep scroll returns to the selected panel start',()=>{
  const s=setup('#findings');
  s.context.window.scrollY=2400;
  s.tabList.getBoundingClientRect=()=>({top:0,height:60,bottom:60});
  s.panels[2].getBoundingClientRect=()=>({top:-1740});
  s.click(0);
  assert.equal(s.context.window.scroll.top,600);
});

test('reselecting a tab leaves scroll and history unchanged',()=>{
  const s=setup('#overview');
  s.context.window.scrollY=2400;
  s.panels[0].getBoundingClientRect=()=>({top:-1740});
  s.click(0);
  assert.equal(s.context.window.scroll,undefined);
  assert.deepEqual(s.history,[]);
});

test('keyboard switching at the top keeps the reading position',()=>{
  const s=setup();
  s.key(0,'ArrowRight');
  assert.equal(s.context.window.scroll,undefined);
  assert.equal(s.tabs[1].focusOptions.preventScroll,true);
});
