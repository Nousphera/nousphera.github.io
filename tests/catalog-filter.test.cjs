const test = require('node:test');
const assert = require('node:assert/strict');
const catalog = require('../assets/catalog-filter.js');
const records = [
  {year:2026, areas:['foundation','decentralized'], search:'AE-PSL autoencoder activation compression'},
  {year:2025, areas:['foundation','privacy','decentralized'], search:'EncCluster functional encryption'},
  {year:2024, areas:['reliable','decentralized'], search:'FedLN nearest neighbor correction NNC noisy labels café'},
  {year:2023, areas:['reliable'], search:'PLiX prototype few-shot audio keyword spotting'},
];
test('topics overlap; multiple search terms intersect within the selected topic', () => {
  assert.equal(catalog.matches(records[1], {area:'privacy',query:'func encrypt'}), true);
  assert.equal(catalog.matches(records[1], {area:'foundation',query:'func encrypt'}), true);
  assert.equal(catalog.matches(records[1], {area:'reliable',query:''}), false);
  assert.equal(catalog.matches(records[3], {area:'decentralized',query:''}), false);
});
test('accent, punctuation and method-acronym searches work', () => {
  for (const query of ['NNC','CAFÉ','noisy labels','Fed LN']) assert.ok(catalog.matches(records[2],{area:'all',query}));
  assert.ok(catalog.matches(records[0],{area:'all',query:'AEPSL'}));
  assert.ok(catalog.matches(records[3],{area:'all',query:'few shot'}));
  assert.equal(catalog.matches(records[2],{area:'all',query:'noise encryption'}),false);
});
test('year groups contain only visible records; empty results contain no stale year', () => {
  assert.deepEqual(catalog.filterRecords(records,{area:'reliable',query:''}).years, {2024:1,2023:1});
  assert.deepEqual(catalog.filterRecords(records,{area:'reliable',query:'nonexistent'}),{visible:[],years:{}});
  assert.equal(catalog.filterRecords(records,{area:'all',query:''}).visible.length,4);
});
test('shareable state preserves unrelated parameters and supports old topic links', () => {
  const areas=['all','foundation','reliable','privacy','decentralized'];
  assert.deepEqual(catalog.readState('?topic=privacy&q=Enc',areas),{area:'privacy',query:'Enc'});
  assert.deepEqual(catalog.readState('?area=unknown&q=FedLN',areas),{area:'all',query:'FedLN'});
  assert.equal(catalog.writeState('?ref=profile&area=privacy&q=old',{area:'all',query:''}),'?ref=profile');
  const state={area:'reliable',query:'few shot'};
  assert.deepEqual(catalog.readState(catalog.writeState('',state),areas),state);
});
