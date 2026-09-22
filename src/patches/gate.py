# -*- coding: utf-8 -*-
"""Spawn on a street, and stop the desert's game running in the city.

THE SPAWN. When the street grid changed from a 58 m pitch to 96 by 64, the
city's start point was never moved with it. It sat 29 m from a street
centreline against a building line at 10 m, which is deep inside a block, so
the game opened with the truck walled in. It now starts on a centreline, and
there is a guard that walks any spawn out to the nearest street rather than
trusting a hand written coordinate to stay correct through the next change.

THE DESERT'S GAME. Segments, feats, kickers, landmarks and gates were all
defined in raw world coordinates with no map test, so every one of them was
live on city streets. The city spawn sat inside "The Washboard". The drift pan
was scored as "The Rim". The three desert jump ramps were ordinary junctions.
Landmarks could be discovered invisibly. Each of those now declares which map
it belongs to and is skipped everywhere else, and feat records are namespaced
by map the way segment records already were.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================================== the spawn
sub("{id:'city',  name:'Vantage Hill', kind:'City and pan', h:baseHCity, start:[29,-29,0.0]}",
    "{id:'city',  name:'Vantage Hill', kind:'City and pan', h:baseHCity, start:[0,-32,0.0]}")

sub("""function placeTruck(x,z,yaw){""",
"""/* A hand written coordinate goes stale the moment the grid changes, which is
   exactly how the city came to open with the truck walled inside a block. On
   the city map, walk any spawn out to the nearest carriageway. */
function safeSpot(x,z){
  if(MAP!==1) return [x,z];
  if(streetD(x,z)<=CARR-1.0) return [x,z];
  var bx=Math.round(x/PX)*PX, bz=Math.round(z/PZ)*PZ;
  return (Math.abs(x-bx)<Math.abs(z-bz)) ? [bx,z] : [x,bz];
}
function placeTruck(x,z,yaw){
  var _sp=safeSpot(x,z); x=_sp[0]; z=_sp[1];""")

# ============================================== every trigger declares its map
sub("""var SEGMENTS=[
  {id:'wash', name:'The Washboard', t:function(x,z){ return Math.abs(z+48)<26 && x>-72 && x<128; }},
  {id:'playa',name:'The Playa',     t:function(x,z){ return Math.hypot(x+96,z-96)<62; }},
  {id:'mesa', name:'Mesa Run',      t:function(x,z){ return Math.hypot(x-98,z+128)<58; }},
  {id:'rim',  name:'The Rim',       t:function(x,z){ var r=Math.hypot(x,z); return r>148 && r<194; }}
];""",
"""var SEGMENTS=[
  {id:'wash', map:0, name:'The Washboard', t:function(x,z){ return Math.abs(z+48)<26 && x>-72 && x<128; }},
  {id:'playa',map:0, name:'The Playa',     t:function(x,z){ return Math.hypot(x+96,z-96)<62; }},
  {id:'mesa', map:0, name:'Mesa Run',      t:function(x,z){ return Math.hypot(x-98,z+128)<58; }},
  {id:'rim',  map:0, name:'The Rim',       t:function(x,z){ var r=Math.hypot(x,z); return r>148 && r<194; }},
  /* and the city gets its own, so the pan stops being scored as "The Rim" */
  {id:'pan',  map:1, name:'The Pan',       t:function(x,z){ return panMask(x,z)>0.5; }},
  {id:'hill', map:1, name:'The Descent',   t:function(x,z){ return Math.abs(x)<14 && z>-200 && z<-40; }},
  {id:'core', map:1, name:'Downtown Loop', t:function(x,z){ return Math.hypot(x-30,z+34)<105; }}
];""")

sub("""  var seg=null;
  for(var i=0;i<SEGMENTS.length;i++) if(SEGMENTS[i].t(S.p.x,S.p.z)){ seg=SEGMENTS[i]; break; }""",
"""  var seg=null;
  for(var i=0;i<SEGMENTS.length;i++)
    if(SEGMENTS[i].map===MAP && SEGMENTS[i].t(S.p.x,S.p.z)){ seg=SEGMENTS[i]; break; }""")

sub("""    var b=PROG.seg[MAPS[MAP].id+':'+SEGMENTS[si].id]||0;
    if(b>0) sv+='<div><span>'+SEGMENTS[si].name+'</span><b>'+b+'</b></div>';""",
"""    if(SEGMENTS[si].map!==MAP) continue;
    var b=PROG.seg[MAPS[MAP].id+':'+SEGMENTS[si].id]||0;
    if(b>0) sv+='<div><span>'+SEGMENTS[si].name+'</span><b>'+b+'</b></div>';""")

# ---- feats: desert only, and recorded per map
sub("""var FEATS=[
  {id:'whoop', name:'Whoop skim',  pts:420},
  {id:'circle',name:'Salt circle', pts:520},
  {id:'ramps', name:'Ramp chain',  pts:680},
  {id:'rim',   name:'Rim run',     pts:600}
];""",
"""var FEATS=[
  {id:'whoop', map:0, name:'Whoop skim',  pts:420},
  {id:'circle',map:0, name:'Salt circle', pts:520},
  {id:'ramps', map:0, name:'Ramp chain',  pts:680},
  {id:'rim',   map:0, name:'Rim run',     pts:600},
  {id:'panspin', map:1, name:'Pan spin',  pts:520},
  {id:'crest',   map:1, name:'Crest jump',pts:560}
];""")

sub("""function featDone(id){
  for(var i=0;i<FEATS.length;i++) if(FEATS[i].id===id){
    var first=!PROG.feat[id];
    PROG.feat[id]=(PROG.feat[id]||0)+1;""",
"""function featDone(id){
  for(var i=0;i<FEATS.length;i++) if(FEATS[i].id===id){
    if(FEATS[i].map!==MAP) return;              /* wrong world for this one */
    var key=MAPS[MAP].id+':'+id;
    var first=!PROG.feat[key];
    PROG.feat[key]=(PROG.feat[key]||0)+1;""")

sub("""  for(var fi=0;fi<FEATS.length;fi++){
    var c=PROG.feat[FEATS[fi].id]||0;""",
"""  for(var fi=0;fi<FEATS.length;fi++){
    if(FEATS[fi].map!==MAP) continue;
    var c=PROG.feat[MAPS[MAP].id+':'+FEATS[fi].id]||0;""")

# the desert feat detectors only run in the desert
sub("""  /* ---- whoop skim: the washboard, fast, mostly airborne ---- */""",
"""  if(MAP===0){
  /* ---- whoop skim: the washboard, fast, mostly airborne ---- */""")
sub("""  }else if(FT.rimIn){ FT.rimIn=false; FT.rimLast=null; FT.rimA=0; }""",
"""  }else if(FT.rimIn){ FT.rimIn=false; FT.rimLast=null; FT.rimA=0; }
  }
  /* ---- the city's own two ---- */
  if(MAP===1){
    var onPan=panMask(S.p.x,S.p.z)>0.5;
    var sideways=Math.abs(beta)>0.22 && S.grounded>=3;
    if(onPan && sideways && sp>7){
      FT.circYaw+=Math.abs(S.w.y)*dt;
      if(FT.circYaw>6.283){ featDone('panspin'); FT.circYaw=0; }
    }else if(!onPan || sp<3.5) FT.circYaw=0;
    /* a crest jump: real air, landed clean, off one of the hills */
    if(S.grounded>=3 && S.airT===0 && S.lastLanding && S.lastLanding.air>1.05
       && S.lastLanding.flat>0.86 && !FT.crestDone){
      FT.crestDone=1; featDone('crest');
    }
    if(S.grounded<2) FT.crestDone=0;
  }""")

# ---- gates, landmarks and kickers are desert furniture
sub("""    checkGates();
    checkLandmarks();""",
"""    if(MAP===0){ checkGates(); checkLandmarks(); }""")

sub("""  if(S.grounded<2 && S.airT>0.45){
    for(var ki=0;ki<KICKERS.length;ki++){""",
"""  if(MAP===0 && S.grounded<2 && S.airT>0.45){
    for(var ki=0;ki<KICKERS.length;ki++){""")

# and the explored map is per world, not one plane shared by both
sub("           score:0, best:0, top:0, seg:{}, feat:{}, mapv:new Uint8Array(MAPN*MAPN) };",
    "           score:0, best:0, top:0, seg:{}, feat:{},\n           mapv:new Uint8Array(MAPN*MAPN), mapc:new Uint8Array(MAPN*MAPN) };")
sub("""function markMap(x,z){
  var i=Math.floor((x+HALF)/WORLD*MAPN), j=Math.floor((z+HALF)/WORLD*MAPN);
  if(i<0||j<0||i>=MAPN||j>=MAPN) return;
  var k=j*MAPN+i;
  if(PROG.mapv[k]<255) PROG.mapv[k]=Math.min(255,PROG.mapv[k]+60);
}""",
"""function markMap(x,z){
  var i=Math.floor((x+HALF)/WORLD*MAPN), j=Math.floor((z+HALF)/WORLD*MAPN);
  if(i<0||j<0||i>=MAPN||j>=MAPN) return;
  var k=j*MAPN+i;
  var plane=(MAP===1?PROG.mapc:PROG.mapv);
  if(plane[k]<255) plane[k]=Math.min(255,plane[k]+60);
}""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
