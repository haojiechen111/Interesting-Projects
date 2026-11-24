#!/usr/bin/env python3
"""抽取 slot-machine.html 的脚本体，套上 DOM 存根，在 JavaScriptCore 里跑无界面战斗。"""
import re, subprocess, sys

src = open('slot-machine.html', encoding='utf-8').read()
body = re.search(r'<script>(.*)</script>', src, re.S).group(1)

stub = r'''
var LOG=[];function out(m){LOG.push(String(m));}
function node(id){
  var el={_id:id,_cls:{},textContent:'',innerHTML:'',style:{setProperty:function(){},removeProperty:function(){},getPropertyValue:function(){return '';}},title:'',disabled:false,open:false,offsetWidth:1,value:'',type:''};
  el.classList={add:function(c){el._cls[c]=1;},remove:function(c){delete el._cls[c];},contains:function(c){return !!el._cls[c];},toggle:function(c,on){if(on)el._cls[c]=1;else delete el._cls[c];}};
  el.setAttribute=function(){};el.getAttribute=function(){return '';};el.removeAttribute=function(){};
  el.querySelector=function(){return node('q');};el.querySelectorAll=function(){return [];};
  el.append=function(){};el.appendChild=function(){};el.remove=function(){};el.replaceWith=function(){};
  el.replaceChildren=function(){};el.prepend=function(){};el.insertAdjacentHTML=function(){};el.cloneNode=function(){return node(id+'-clone');};
  el.animate=function(){return {cancel:function(){},finished:{then:function(){}}};};el.getAnimations=function(){return [];};
  el.dispatchEvent=function(){return true;};el.scrollIntoView=function(){};el.setPointerCapture=function(){};el.releasePointerCapture=function(){};
  el.addEventListener=function(){};el.removeEventListener=function(){};el.focus=function(){};el.blur=function(){};
  el.closest=function(sel){return node('closest'+(sel||''));};el.matches=function(){return false;};el.contains=function(){return false;};
  el.getBoundingClientRect=function(){return {left:0,top:0,width:10,height:10};};
  el.showModal=function(){el.open=true;};el.close=function(){el.open=false;};
  el.getContext=function(){return ctx2d;};el.scrollTo=function(){};el.insertBefore=function(){};
  el.dataset={};el.children=[];el.parentNode=null;el.firstChild=null;
  return el;
}
var ctx2d=new Proxy({},{get:function(t,k){if(k==='canvas')return node('canvas');if(k==='createLinearGradient'||k==='createRadialGradient')return function(){return {addColorStop:function(){}};};if(k==='measureText')return function(){return {width:10};};return function(){};},set:function(){return true;}});
var nodes={};
var document={
  getElementById:function(id){if(!nodes[id])nodes[id]=node(id);return nodes[id];},
  createElement:function(){return node('new');},
  createElementNS:function(){return node('ns');},
  querySelector:function(){return node('q');},
  querySelectorAll:function(){return [];},
  addEventListener:function(){},removeEventListener:function(){},
  hidden:false,body:node('body'),documentElement:node('html'),head:node('head'),activeElement:null
};
var localStorage={getItem:function(){return null;},setItem:function(){},removeItem:function(){}};
var performanceClock=0;
var performance={now:function(){return performanceClock;}};
var window={matchMedia:function(){return {matches:false,addEventListener:function(){},addListener:function(){}};},requestAnimationFrame:function(){return 0;},localStorage:localStorage,devicePixelRatio:1,addEventListener:function(){},innerWidth:1280,innerHeight:800};
window.document=document;
function requestAnimationFrame(){return 0;}
function cancelAnimationFrame(){}
function setTimeout(){return 0;}
function clearTimeout(){}
function setInterval(){return 0;}
function clearInterval(){}
function getComputedStyle(){return {getPropertyValue:function(){return '';}};}
var navigator={userAgent:'sim'};
var crypto={getRandomValues:function(arr){for(var i=0;i<arr.length;i++)arr[i]=Math.floor(Math.random()*4294967295);return arr;},randomUUID:function(){return 'sim-uuid-'+Math.random().toString(16).slice(2);}};
window.crypto=crypto;
function ResizeObserver(cb){this.observe=function(){};this.unobserve=function(){};this.disconnect=function(){};}
function IntersectionObserver(cb){this.observe=function(){};this.unobserve=function(){};this.disconnect=function(){};}
function MutationObserver(cb){this.observe=function(){};this.disconnect=function(){};this.takeRecords=function(){return [];};}
window.ResizeObserver=ResizeObserver;window.IntersectionObserver=IntersectionObserver;window.MutationObserver=MutationObserver;
'''

driver = r'''
function recruit(symbol,rank){totalPeople++;var p=rebuildRecruit({symbol:symbol,rank:rank,branch:0,exp:0,id:totalPeople});people.push(p);return p;}
function playLevel(target,roster){
  people.length=0;totalPeople=0;
  for(var i=0;i<formation.length;i++)formation[i]=null;
  for(var i=0;i<roster.length;i++)formation[i]=recruit(roster[i][0],roster[i][1]).id;
  level=target;startCombat();
  var guard=0;
  while(combat&&!combat.done&&guard<120000){updateCombat(1/60);guard++;}
  if(!combat)return {ok:false,note:'combat lost'};
  var c=combat,frames=0;
  while(combatOutroActive(c)&&frames<600){updateCombatOutro(c,1/60*(c.slow||1));frames++;}
  if(!c.outroShown){c.outroShown=true;showCombatResult(c);}
  var bar=document.getElementById('combatResult').classList.contains('visible');
  var res={level:target,won:c.won,time:Number(c.time.toFixed(2)),slow:c.slow,outroFrames:frames,bar:bar,text:document.getElementById('combatResultText').textContent,gold:balance,diamonds:diamonds,next:level};
  stopCombat();fighting=false;
  return res;
}
var roster=[[0,2],[1,2],[2,2],[3,2],[4,2],[5,2],[0,2],[1,2]];
var report=[];
for(var lv=1;lv<=10;lv++)report.push(playLevel(lv,roster));
var sfxNames=Object.keys(combatSfx).sort().join(',');
out('sfx: '+sfxNames);
for(var i=0;i<report.length;i++){var r=report[i];
  out('L'+r.level+' won='+r.won+' t='+r.time+' slow='+r.slow+' outroFrames='+r.outroFrames+' bar='+r.bar+' | '+r.text);}
var boss=report[7];
out('boss slowmo ok: '+(boss.slow===0.45));
out('normal slowmo ok: '+(report[0].slow===1));
out('all bars shown: '+report.every(function(r){return r.bar;}));
return LOG.join('\n');
'''

open('/tmp/slot_sim.js', 'w', encoding='utf-8').write(stub + '(function(){\n' + body + driver + '\n})()')
res = subprocess.run(['osascript', '-l', 'JavaScript', '/tmp/slot_sim.js'], capture_output=True, text=True)
print(res.stdout.strip())
if res.returncode:
    print('STDERR:', res.stderr.strip()[:2000], file=sys.stderr)
    sys.exit(res.returncode)