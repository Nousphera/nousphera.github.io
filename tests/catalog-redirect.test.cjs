const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
test('legacy catalog redirects without dropping shared queries or year anchors', () => {
  const script = fs.readFileSync(path.join(__dirname,'../assets/catalog-redirect.js'),'utf8');
  for (const [search, hash, expected] of [
    ['', '', '/#collection'],
    ['?area=privacy&q=enc', '', '/?area=privacy&q=enc#collection'],
    ['?q=audio', '#year-2023', '/?q=audio#year-2023'],
  ]) {
    let destination;
    vm.runInNewContext(script,{window:{location:{search,hash,replace(value){destination=value;}}}});
    assert.equal(destination,expected);
  }
});
