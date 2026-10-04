import test from 'node:test';
import assert from 'node:assert/strict';
import {assertOutputs, dockPosition, runToHere} from '../lib/core.js';

test('printed OCaml exceptions fail despite protocol success', () => {
  assert.throws(() => assertOutputs([{outputs:[{output_type:'execute_result',data:{'text/plain':'Error: Unbound value matvec'}}]}],0,'OCaml'), /Cell 1 failed/);
  assert.throws(() => assertOutputs([{outputs:[{output_type:'execute_result',data:{'text/plain':['\n','Exception: Failure "fixture".']}}]}],0,'ocaml'), /failed/);
});
test('Python logging of a diagnostic string is not an OCaml exception', () => {
  assert.doesNotThrow(() => assertOutputs([{outputs:[{output_type:'stream',text:'Error: example of a diagnostic'}]}],0,'python'));
  assert.throws(() => assertOutputs([{outputs:[{output_type:'error'}]}],0,'python'), /failed/);
});
test('an earlier printed error prevents the selected cell from executing', async () => {
  let selected=false;
  const runner={index:3,above:async()=>true,select:()=>{},selected:async()=>{selected=true;return true;},check:()=>{throw new Error('earlier printed error');}};
  await assert.rejects(runToHere(runner), /earlier printed error/);
  assert.equal(selected,false);
});
test('changing focus during prerequisite execution preserves the captured cell', async () => {
  const events=[];
  const runner={index:5,above:async()=>{runner.index=99;events.push('above');return true;},select:i=>events.push(['select',i]),selected:async()=>{events.push('selected');return true;},check:end=>events.push(['check',end])};
  await runToHere(runner);
  assert.deepEqual(events,[['select',5],'above',['check',4],['select',5],'selected',['check',5]]);
});
test('first-cell execution does not try to execute an empty prerequisite range', async () => {
  const runner={index:0,above:()=>{throw new Error('unexpected');},select:()=>{},selected:async()=>true,check:()=>{}};
  await runToHere(runner);
});
test('keyboard shrink and Safari viewport panning keep the dock visible', () => {
  for (const viewport of [{offsetTop:0,offsetLeft:0,height:360,width:390},{offsetTop:240,offsetLeft:20,height:300,width:320},{offsetTop:0,offsetLeft:0,height:844,width:390}]) {
    const geometry=dockPosition(viewport,80);
    assert.ok(geometry.top>=viewport.offsetTop);
    assert.ok(geometry.top+80<=viewport.offsetTop+viewport.height);
    assert.ok(geometry.left+geometry.width<=viewport.offsetLeft+viewport.width);
  }
});
