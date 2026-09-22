# -*- coding: utf-8 -*-
"""Skill scoring, chains, named feats and named segments.

The Forza Horizon idea, with the one part that would break your rules taken
out. Their skill chain runs on a decaying bar, and a bar that empties is a
countdown wearing a different hat. Here the chain breaks on an EVENT instead:
you stop, or you cover 260 m without doing anything worth points. So it still
rewards keeping it flowing, and nothing on screen is ever counting down at you.

Same reasoning on drifts. A drift is scored by the DISTANCE you carried it, not
the seconds, because distance counts up and seconds do not. Segments record
your best POINTS on a pass rather than a time, which is the Strava idea without
the stopwatch.

Everything is awarded at the moment of the act and nothing waits for the end of
a run, because a results screen is the thing that made the last game feel like
it was judging you.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- save fields
sub("var PROG={ odo:0, air:0, gates:0, found:{}, jump:[0,0,0], jumpAt:[null,null,null],\n           mapv:new Uint8Array(MAPN*MAPN) };",
    "var PROG={ odo:0, air:0, gates:0, found:{}, jump:[0,0,0], jumpAt:[null,null,null],\n           score:0, best:0, top:0, seg:{}, mapv:new Uint8Array(MAPN*MAPN) };")
sub("""    PROG.gates=o.gates||0;""",
    """    PROG.gates=o.gates||0;
    PROG.score=o.score||0; PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};""")
sub("""      odo:PROG.odo, air:PROG.air, gates:PROG.gates, found:PROG.found,
      jump:PROG.jump, jumpAt:PROG.jumpAt, map:btoa(str)}));""",
    """      odo:PROG.odo, air:PROG.air, gates:PROG.gates, found:PROG.found,
      jump:PROG.jump, jumpAt:PROG.jumpAt,
      score:PROG.score, best:PROG.best, top:PROG.top, seg:PROG.seg, map:btoa(str)}));""")

# ---------------------------------------------------------------- the system
sub("""/* ================= vehicle state ================= */""",
"""/* ================= skill scoring ================= */
/* Named stretches. Each records your best points on a single pass, which is
   the Strava idea with the stopwatch taken out. */
var SEGMENTS=[
  {id:'wash', name:'The Washboard', t:function(x,z){ return Math.abs(z+48)<26 && x>-72 && x<128; }},
  {id:'playa',name:'The Playa',     t:function(x,z){ return Math.hypot(x+96,z-96)<62; }},
  {id:'mesa', name:'Mesa Run',      t:function(x,z){ return Math.hypot(x-98,z+128)<58; }},
  {id:'rim',  name:'The Rim',       t:function(x,z){ var r=Math.hypot(x,z); return r>148 && r<194; }}
];

var SK={ chain:1, run:0, since:0, seg:null, segPts:0, fastFlag:false,
         drift:{on:false,dist:0,peak:0}, two:{on:false,dist:0} };
var _sf=new THREE.Vector3(), _sr2=new THREE.Vector3(), _su2=new THREE.Vector3();
var popEl,popN,popP,chnEl, popT=0;

function airName(air,dist){
  if(air>=2.0||dist>=52) return 'Moonshot';
  if(air>=1.4||dist>=36) return 'Huge air';
  if(air>=0.95) return 'Big air';
  return 'Air';
}
function driftName(d){
  if(d>=150) return 'Endless drift';
  if(d>=85)  return 'Long drift';
  if(d>=42)  return 'Drift';
  return 'Slide';
}

function award(name,pts){
  pts=Math.max(1,Math.round(pts*SK.chain));
  SK.run+=pts;
  PROG.score+=pts;
  if(SK.run>PROG.best) PROG.best=SK.run;
  SK.chain=Math.min(12,SK.chain+1);
  SK.since=0;
  if(SK.seg) SK.segPts+=pts;
  if(popN){
    popN.textContent=name;
    popP.textContent='+'+pts;
    popEl.className='on'; popT=1.15;
  }
  if(chnEl) chnEl.textContent=SK.chain>1?('x'+SK.chain):'';
  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);
}

function breakChain(){
  if(SK.chain>1 && chnEl) chnEl.textContent='';
  SK.chain=1; SK.run=0; SK.since=0; SK.fastFlag=false;
}

function skills(dt){
  var sp=S.v.length(), d=sp*dt;
  SK.since+=d;

  /* The chain ends on an event, never on a clock: you stopped, or you have
     covered a long way without doing anything. */
  if(sp<2.0 || SK.since>260) breakChain();

  _sf.set(0,0,1).applyQuaternion(S.q);
  _sr2.set(1,0,0).applyQuaternion(S.q);
  _su2.set(0,1,0).applyQuaternion(S.q);

  /* flat out, once per chain */
  if(!SK.fastFlag && sp>33 && S.grounded>0){ SK.fastFlag=true; award('Flat out',55); }
  if(sp>PROG.top) PROG.top=sp;

  /* drift, measured in metres carried */
  var beta=Math.atan2(S.v.dot(_sr2),Math.abs(S.v.dot(_sf))+0.5);
  if(S.grounded>=3 && sp>8 && Math.abs(beta)>0.22){
    SK.drift.on=true; SK.drift.dist+=d;
    SK.drift.peak=Math.max(SK.drift.peak,Math.abs(beta));
  }else if(SK.drift.on){
    if(SK.drift.dist>16) award(driftName(SK.drift.dist), SK.drift.dist*1.15*(1+SK.drift.peak));
    SK.drift.on=false; SK.drift.dist=0; SK.drift.peak=0;
  }

  /* two wheels */
  var lft=(corners[0].contact?1:0)+(corners[2].contact?1:0);
  var rgt=(corners[1].contact?1:0)+(corners[3].contact?1:0);
  var lean=Math.acos(Math.max(-1,Math.min(1,_su2.y)));
  if(((lft===2&&rgt===0)||(rgt===2&&lft===0)) && lean>0.34 && sp>5){
    SK.two.on=true; SK.two.dist+=d;
  }else if(SK.two.on){
    if(SK.two.dist>9) award('Two wheels', SK.two.dist*2.2);
    SK.two.on=false; SK.two.dist=0;
  }

  /* named segments */
  var seg=null;
  for(var i=0;i<SEGMENTS.length;i++) if(SEGMENTS[i].t(S.p.x,S.p.z)){ seg=SEGMENTS[i]; break; }
  if(seg!==SK.seg){
    if(SK.seg && SK.segPts>0){
      var prev=PROG.seg[SK.seg.id]||0;
      if(SK.segPts>prev){
        PROG.seg[SK.seg.id]=SK.segPts;
        if(popN){ popN.textContent=SK.seg.name; popP.textContent='best '+SK.segPts;
                  popEl.className='on'; popT=1.4; }
        chime(); saveProg();
      }
    }
    SK.seg=seg; SK.segPts=0;
  }
}

/* ================= vehicle state ================= */""")

# ---------------------------------------------------------------- hook it up
sub("""    checkGates();
    checkLandmarks();""",
    """    checkGates();
    checkLandmarks();
    skills(dt);
    if(popT>0){ popT-=dt; if(popT<=0 && popEl) popEl.className=''; }""")

# air is awarded from the landing that already exists
sub("""      S.lastLanding={dist:dist,up:_bup.y,flat:flat,nearKicker:nearK,air:S.airT};
      if(flat>0.88){""",
"""      S.lastLanding={dist:dist,up:_bup.y,flat:flat,nearKicker:nearK,air:S.airT};
      award(airName(S.airT,dist), 26*S.airT + 2.6*dist);
      if(flat>0.88){
        if(dist>18) award('Stuck it',34);""")

# gates feed the chain
sub("""    PROG.gates=(PROG.gates||0)+1; saveProg();
    chime(); buzz(25);""",
"""    PROG.gates=(PROG.gates||0)+1;
    award(SK.chain>3?'Gate run':'Gate', 30);
    saveProg(); buzz(25);""")

# ---------------------------------------------------------------- hud
sub("""<div id="arc"></div><div id="arcdot"></div>""",
"""<div id="arc"></div><div id="arcdot"></div>
<div id="pop"><div class="pn" id="popn"></div><div class="pp" id="popp"></div></div>
<div id="chn"></div>""")

sub("""  /* a scrim so anything drawn over a bright sky still reads */""",
"""  /* skill feedback: appears at the moment of the act, leaves on its own */
  #pop{position:fixed;left:50%;top:31%;transform:translate(-50%,-50%);text-align:center;
       pointer-events:none;opacity:0;transition:opacity .18s}
  #pop.on{opacity:1}
  #pop .pn{font-weight:700;text-transform:uppercase;letter-spacing:.14em;font-size:17px;
           color:var(--cream);text-shadow:0 2px 12px rgba(30,16,8,.85)}
  #pop .pp{font-family:"Azeret Mono",monospace;font-weight:700;font-size:30px;
           color:var(--amber);text-shadow:0 2px 12px rgba(30,16,8,.85);margin-top:2px}
  #chn{position:fixed;left:50%;top:calc(31% + 46px);transform:translateX(-50%);
       font-family:"Azeret Mono",monospace;font-weight:700;font-size:15px;
       color:var(--teal);text-shadow:0 2px 10px rgba(30,16,8,.85);pointer-events:none}

  /* a scrim so anything drawn over a bright sky still reads */""")

sub("""var hudEl=document.getElementById('hud');""",
"""var hudEl=document.getElementById('hud');
popEl=document.getElementById('pop'); popN=document.getElementById('popn');
popP=document.getElementById('popp'); chnEl=document.getElementById('chn');""")

# ---------------------------------------------------------------- pause card
sub("""      <div><div class="lbl">Driven</div><div class="num" id="m-odo">0.0 km</div></div>
      <div><div class="lbl">Found</div><div class="num" id="m-found">0</div></div>
      <div><div class="lbl">Best jump</div><div class="num" id="m-air">0 m</div></div>
    </div>""",
"""      <div><div class="lbl">Points</div><div class="num" id="m-score">0</div></div>
      <div><div class="lbl">Best run</div><div class="num" id="m-best">0</div></div>
      <div><div class="lbl">Top</div><div class="num" id="m-top">0</div></div>
    </div>
    <div class="tally3">
      <div><div class="lbl">Driven</div><div class="num" id="m-odo">0.0 km</div></div>
      <div><div class="lbl">Found</div><div class="num" id="m-found">0</div></div>
      <div><div class="lbl">Best jump</div><div class="num" id="m-air">0 m</div></div>
    </div>
    <div id="segs"></div>""")

sub("""  #mapwrap{margin:10px 0 2px;""",
"""  #segs{margin:9px 0 0;display:flex;flex-direction:column;gap:5px}
  #segs div{display:flex;justify-content:space-between;align-items:baseline;
            font-size:14px;color:#ded2d8}
  #segs b{font-family:"Azeret Mono",monospace;font-weight:700;color:var(--amber);font-size:14px}
  #mapwrap{margin:10px 0 2px;""")

sub("""  document.getElementById('m-odo').textContent=(PROG.odo/1000).toFixed(1)+' km';""",
"""  document.getElementById('m-score').textContent=PROG.score;
  document.getElementById('m-best').textContent=PROG.best;
  document.getElementById('m-top').textContent=Math.round(PROG.top*3.6);
  var sv='';
  for(var si=0;si<SEGMENTS.length;si++){
    var b=PROG.seg[SEGMENTS[si].id]||0;
    if(b>0) sv+='<div><span>'+SEGMENTS[si].name+'</span><b>'+b+'</b></div>';
  }
  document.getElementById('segs').innerHTML=sv;
  document.getElementById('m-odo').textContent=(PROG.odo/1000).toFixed(1)+' km';""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
