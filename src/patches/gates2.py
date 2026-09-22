# -*- coding: utf-8 -*-
"""The gates were worth nothing. They are the circuit now.

WHAT THEY ACTUALLY DID. Twelve gates stand in a loop around the basin and only
the next one's beam lights, so they are findable and clearly meant to be a
course. Driving through one awarded **30 points** -- against roughly 336 for an
ordinary drift and 1,000 for an open run -- incremented `PROG.gates`, which is
saved and **displayed nowhere**, and turned the bar teal. Completing all twelve
did nothing whatsoever: they silently reset and you got another 30 points.

So: about a tenth of a mediocre drift, and a counter no one can see. That is
the correct answer to your question and it is not a good one.

WHAT THEY ARE NOW. The circuit. It is the "Strava segment" idea applied to the
one part of the map that is already laid out as a course:

  - The first gate starts a clock. Each gate after it must be reached within
    twenty-two seconds or the run lapses and you start again.
  - Gates escalate: the first is worth 40, the twelfth 194, because the last
    one is the hard one to still be on for.
  - Finishing all twelve banks a completion bonus that is larger the faster you
    went, and records the time.
  - That time is a **personal best you can see**, in the pause screen next to
    the segment records, which is what makes it worth going round again.

The gate pop now reads "Gate 7/12" with the running clock, so you always know
where you are in a lap without any new furniture on the HUD.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- the record carries over
sub("           score:0, career:0, best:0, top:0, seg:{}, feat:{},",
    "           score:0, career:0, best:0, top:0, lap:0, seg:{}, feat:{},")
sub("    PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};",
    "    PROG.best=o.best||0; PROG.top=o.top||0; PROG.lap=o.lap||0; PROG.seg=o.seg||{};")
sub("      career:PROG.career, best:PROG.best, top:PROG.top, seg:PROG.seg,",
    "      career:PROG.career, best:PROG.best, top:PROG.top, lap:PROG.lap, seg:PROG.seg,")

# ---- the run itself
sub("function checkGates(){",
"""/* ---- the circuit ----
   The twelve gates are a lap, not twelve unrelated 30 point pickups. A clock
   starts on the first, each gate has to be reached within the window, and
   finishing the set is worth doing quickly. */
var GRUN={on:false, t:0, since:0, n:0};
var GATE_WINDOW=22;
function gateClock(){
  var m=Math.floor(GRUN.t/60), sec=GRUN.t-m*60;
  return m+':'+(sec<10?'0':'')+sec.toFixed(1);
}
function gateLapse(){
  if(!GRUN.on) return;
  GRUN.on=false; GRUN.n=0; GRUN.t=0;
  popHold('Circuit lost','gate '+(S.next+1)+' timed out'); POP.t=-0.5;
  S.next=0;
  GATES.forEach(function(x){
    x.done=false;
    x.g.children.forEach(function(ch){
      if(ch.userData.baseHex!==undefined) ch.material.color.setHex(ch.userData.baseHex);
    });
  });
  blip(150,0.22,'sawtooth',0.05);
}
function stepGates(dt){
  if(MAP!==0 || !GRUN.on) return;
  GRUN.t+=dt; GRUN.since+=dt;
  if(GRUN.since>GATE_WINDOW) gateLapse();
}

function checkGates(){""")

sub("""    PROG.gates=(PROG.gates||0)+1;
    award(SK.chain>3?'Gate run':'Gate', 30);
    saveProg(); buzz(25);""",
"""    PROG.gates=(PROG.gates||0)+1;
    if(!GRUN.on){ GRUN.on=true; GRUN.t=0; GRUN.n=0; }
    GRUN.n++; GRUN.since=0;
    /* the twelfth gate is the hard one to still be on for, so it pays most */
    award('Gate '+GRUN.n+'/'+GATES.length+'  '+gateClock(), 40+(GRUN.n-1)*14);
    if(GRUN.n>=GATES.length){
      /* faster is worth more, and there is a floor so a slow lap still pays */
      var bonus=Math.round(900+Math.max(0,150-GRUN.t)*16);
      var first=(PROG.lap===0), beat=(!first && GRUN.t<PROG.lap);
      if(first||beat) PROG.lap=GRUN.t;
      award('Circuit complete  '+gateClock(), bonus);
      popHold(beat?'Circuit record':'Circuit complete', gateClock()); POP.t=-1.4;
      chime(); buzz([12,40,12,40]);
      GRUN.on=false; GRUN.n=0; GRUN.t=0;
    }
    saveProg(); buzz(25);""")

# ---- step it, in both the real loop and the harness
sub("    if(MAP===0){ checkGates(); checkLandmarks(); }",
    "    if(MAP===0){ checkGates(); checkLandmarks(); stepGates(dt); }")
sub("        readInput(dt); step(dt); checkGates(); checkLandmarks(); skills(dt); stepRuns(dt);",
    "        readInput(dt); step(dt); checkGates(); checkLandmarks(); stepGates(dt); skills(dt); stepRuns(dt);")

# ---- and it shows, which the gate counter never did
sub("""      <div><div class="lbl">Driven</div><div class="num" id="m-odo">0.0 km</div></div>
      <div><div class="lbl">Found</div><div class="num" id="m-found">0</div></div>
      <div><div class="lbl">Best jump</div><div class="num" id="m-air">0 m</div></div>""",
"""      <div><div class="lbl">Driven</div><div class="num" id="m-odo">0.0 km</div></div>
      <div><div class="lbl">Circuit</div><div class="num" id="m-lap">--</div></div>
      <div><div class="lbl">Best jump</div><div class="num" id="m-air">0 m</div></div>""")

sub("""  document.getElementById('m-found').textContent=Object.keys(PROG.found).length;""",
"""  var ml=document.getElementById('m-lap');
  if(ml) ml.textContent = PROG.lap>0
    ? (Math.floor(PROG.lap/60)+':'+((PROG.lap%60)<10?'0':'')+(PROG.lap%60).toFixed(1))
    : '--';""")

# a run in progress should not survive leaving the map or parking up
sub("""  breakChain();
  resetRuns();""",
"""  breakChain();
  GRUN.on=false; GRUN.n=0; GRUN.t=0;
  resetRuns();""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
