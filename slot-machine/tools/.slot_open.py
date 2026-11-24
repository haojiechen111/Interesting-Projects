#!/usr/bin/env python3
"""开局难度探针：用无界面战斗跑「第一关 + 少量黄铜兵」各种组合，并统计 1000 金币能抽到几个兵。"""
import importlib.util, re, subprocess, sys

spec = importlib.util.spec_from_file_location('slot_sim_stub', 'tools/.slot_sim.py')
# 不执行 .slot_sim.py（它会自己跑一遍），直接读源码取 stub 文本。
stub = re.search(r"stub = r'''(.*?)'''", open('tools/.slot_sim.py', encoding='utf-8').read(), re.S).group(1)

src = open('slot-machine.html', encoding='utf-8').read()
body = re.search(r'<script>(.*)</script>', src, re.S).group(1)

driver = r'''
function recruit(symbol,rank){totalPeople++;var p=rebuildRecruit({symbol:symbol,rank:rank,branch:0,exp:0,id:totalPeople});people.push(p);return p;}
function run(target,roster){
  people.length=0;totalPeople=0;
  for(var i=0;i<formation.length;i++)formation[i]=null;
  for(var i=0;i<roster.length;i++)formation[i]=recruit(roster[i][0],roster[i][1]).id;
  level=target;startCombat();
  var guard=0;
  while(combat&&!combat.done&&guard<120000){updateCombat(1/60);guard++;}
  var c=combat,alive=0,hp=0;
  if(c)c.units.forEach(function(u){if(!u.enemy&&u.hp>0){alive++;hp+=u.hp;}});
  var left=c?c.units.filter(function(u){return u.enemy&&u.hp>0;}).length:0;
  var leftHp=0;if(c)c.units.forEach(function(u){if(u.enemy&&u.hp>0)leftHp+=u.hp;});
  var res={won:c?c.won:false,time:c?Number(c.time.toFixed(1)):0,alive:alive,hp:Math.round(hp),enemiesLeft:left,enemyHp:Math.round(leftHp)};
  stopCombat();fighting=false;return res;
}
// 一、第 1 关：每个兵种单独一个黄铜兵
out('== 第1关 · 单个黄铜兵 ==');
for(var s=0;s<6;s++){
  var r=run(1,[[s,0]]);
  out(roleNames[s]+' x1: won='+r.won+' t='+r.time+'s 残敌='+r.enemiesLeft+' 敌剩HP='+r.enemyHp);
}
// 二、第 1 关：同兵种 2/3 个黄铜兵
out('== 第1关 · 多个黄铜兵 ==');
for(var n=2;n<=4;n++){
  var line=[];
  for(var s=0;s<6;s++){
    var roster=[];for(var k=0;k<n;k++)roster.push([s,0]);
    var r=run(1,roster);
    line.push(roleNames[s]+(r.won?'胜'+r.time+'s':'败(敌剩'+r.enemyHp+')'));
  }
  out(n+'人同兵种: '+line.join(' | '));
}
// 三、第 1 关：混编黄铜
out('== 第1关 · 混编黄铜 ==');
var mixes=[[[0,0],[1,0]],[[0,0],[2,0]],[[1,0],[2,0]],[[0,0],[1,0],[2,0]],[[0,0],[0,0],[1,0]]];
for(var m=0;m<mixes.length;m++){
  var names=mixes[m].map(function(x){return roleNames[x[0]];}).join('+');
  var r=run(1,mixes[m]);
  out(names+': won='+r.won+' t='+r.time+'s 存活='+r.alive+' 敌剩HP='+r.enemyHp);
}
// 四、第 1 关敌人总量
var stage=stageFor(1),foes=stageEnemies(1,stage);
out('== 第1关敌人 ==');
out('数量='+foes.length+' 总HP='+foes.reduce(function(a,z){return a+z.hp;},0)+' 总攻='+foes.reduce(function(a,z){return a+z.attack;},0));
// 五、开局经济：1000 金币抽 5 把，统计兵数分布
out('== 开局招募模拟(10000 次) ==');
var dist={},total=0;
for(var t=0;t<10000;t++){
  missedSpins=0;var got=0;
  for(var spin=0;spin<Math.floor(initialGold/recruitCost);spin++){
    var b=recruitmentBoard().board;
    var n=settle(b).count;
    missedSpins=n?0:missedSpins+1;
    got+=n;
  }
  dist[got]=(dist[got]||0)+1;total+=got;
}
var keys=Object.keys(dist).map(Number).sort(function(a,b){return a-b;});
out(keys.map(function(k){return k+'兵:'+(dist[k]/100).toFixed(1)+'%';}).join(' '));
out('平均兵数='+(total/10000).toFixed(2));
return LOG.join('\n');
'''

open('/tmp/slot_open.js', 'w', encoding='utf-8').write(stub + '(function(){\n' + body + driver + '\n})()')
res = subprocess.run(['osascript', '-l', 'JavaScript', '/tmp/slot_open.js'], capture_output=True, text=True)
print(res.stdout.strip())
if res.returncode:
    print('STDERR:', res.stderr.strip()[:2000], file=sys.stderr)
    sys.exit(res.returncode)