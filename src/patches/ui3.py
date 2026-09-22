# -*- coding: utf-8 -*-
"""A speedometer, points that land in the total, and a garage you can see past.

THE SPEEDOMETER. The HUD's rule has been that everything happens in the world
and the screen stays almost empty: a score top left, a menu top right, two
rings for your thumbs. Speed is the one number that belongs on the glass, so it
takes the empty third slot, top centre, and completes that row rather than
starting a new element somewhere. Same monospace face and tabular figures as
the score, cream on the scrim, a small unit label under it in the label style
used everywhere else. No dial, no needle, no chrome: this HUD does not have any
and one would look imported from another game.

POINTS THAT GO SOMEWHERE. The award appeared in the middle of the screen and
the total in the corner changed at the same instant, so there was nothing
joining them and the tally read as a separate number that happened to move. The
award now holds for half a second, folds down into the corner, and the total
counts up to meet it rather than jumping. Same points, but you can see where
they went.

THE GARAGE CARD SAT ON THE CAR. `#garage` sets `align-items:flex-end` to keep
the card low, and `.sheet>.card{margin:auto}` -- which exists so a tall menu
centres when it fits and scrolls when it does not -- overrode it and put the
card back in the middle of the screen, over the vehicle you are choosing. It is
pinned to the bottom now, the bars are in two columns so it is half as tall,
and the turntable aims below the car so the car sits in the clear space above
the card instead of behind it.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ============================================================ the markup
sub("""<div id="tally"><b id="t-score">0</b><i id="t-chain"></i></div>""",
"""<div id="tally"><b id="t-score">0</b><i id="t-chain"></i></div>
<div id="spd"><b id="spd-n">0</b><i>km/h</i></div>
<div id="fly"></div>""")

# ============================================================ the styling
sub("""  #hud.idle ~ #tally{opacity:.55}""",
"""  #hud.idle ~ #tally{opacity:.55}

  /* Speed takes the empty third slot of the top row: score left, speed centre,
     menu right. No dial and no needle, because nothing else here has one. */
  #spd{position:fixed;left:50%;top:11px;transform:translateX(-50%);
       text-align:center;pointer-events:none;
       font-family:"Azeret Mono",monospace;font-variant-numeric:tabular-nums;
       transition:opacity .3s}
  #spd b{display:block;font-weight:700;font-size:38px;line-height:.9;
         color:var(--cream);text-shadow:0 2px 12px rgba(20,10,6,.92)}
  #spd i{font-style:normal;font-family:"Chakra Petch",sans-serif;font-weight:600;
         font-size:10px;letter-spacing:.22em;text-transform:uppercase;
         color:var(--mute);text-shadow:0 2px 8px rgba(20,10,6,.9)}
  #hud.idle ~ #spd{opacity:.5}
  @media (max-height:520px){ #spd b{font-size:30px} }

  /* the award, on its way into the total */
  #fly{position:fixed;left:0;top:0;pointer-events:none;opacity:0;
       font-family:"Azeret Mono",monospace;font-weight:700;font-size:30px;
       color:var(--amber);text-shadow:0 2px 12px rgba(30,16,8,.85);
       transform:translate(-50%,-50%)}""")

# the garage card, pinned low, in two columns
sub("""  #garage .card{max-width:360px;margin-bottom:6px}""",
"""  /* margin:auto on .sheet>.card was centring this over the car, which is the
     one thing this sheet exists to show. Pinned to the bottom instead. */
  #garage .card{max-width:396px;margin:auto auto 8px;padding:15px 17px 13px}
  #garage .bars{display:grid;grid-template-columns:1fr 1fr;gap:6px 16px;margin:8px 0 10px}
  #garage .gname{font-size:27px}
  #garage .rule{margin:8px 0 10px}
  @media (max-height:560px){
    #garage .gkind{display:none}
    #garage .gname{font-size:22px}
  }""")

# ============================================================ the behaviour
sub("""tallyN=document.getElementById('t-score'); tallyC=document.getElementById('t-chain');""",
"""tallyN=document.getElementById('t-score'); tallyC=document.getElementById('t-chain');
spdN=document.getElementById('spd-n'); flyEl=document.getElementById('fly');""")

sub("var toastT=0;",
"""/* The running total counts up to whatever has been scored rather than
   snapping, and an award waits half a second before it is folded in, so the
   number that flies into the corner arrives with the count. */
var TAL_SHOWN=0, TAL_TARGET=0, TAL_WAIT=0;
function setTally(v,snap){
  TAL_TARGET=v;
  if(snap){ TAL_SHOWN=v; TAL_WAIT=0; if(tallyN) tallyN.textContent=v; }
}
function tallyTick(dt){
  if(TAL_WAIT>0){ TAL_WAIT-=dt; if(TAL_WAIT<=0) TAL_TARGET=PROG.score; }
  if(TAL_SHOWN===TAL_TARGET) return;
  var d=TAL_TARGET-TAL_SHOWN;
  var step=Math.max(1,Math.ceil(Math.abs(d)*Math.min(1,dt*6.5)));
  TAL_SHOWN += (d>0? step : -step);
  if((d>0&&TAL_SHOWN>TAL_TARGET)||(d<0&&TAL_SHOWN<TAL_TARGET)) TAL_SHOWN=TAL_TARGET;
  if(tallyN) tallyN.textContent=TAL_SHOWN;
}
/* the award, folding down into the corner it is being added to */
function flyScore(pts){
  if(!flyEl||!popEl||!tallyN) return;
  var pr=popEl.getBoundingClientRect(), tr=tallyN.getBoundingClientRect();
  var x0=pr.left+pr.width/2, y0=pr.top+pr.height*0.80;
  flyEl.textContent='+'+pts;
  flyEl.style.transition='none';
  flyEl.style.left=x0+'px'; flyEl.style.top=y0+'px';
  flyEl.style.transform='translate(-50%,-50%) scale(1)';
  flyEl.style.opacity='0';
  void flyEl.offsetWidth;                       /* commit the start state */
  flyEl.style.transition='opacity .12s ease';
  flyEl.style.opacity='1';
  setTimeout(function(){
    flyEl.style.transition='transform .44s cubic-bezier(.36,0,.2,1),opacity .44s ease';
    flyEl.style.transform='translate(-50%,-50%) translate('+
      ((tr.left+tr.width/2)-x0).toFixed(0)+'px,'+
      ((tr.top+tr.height/2)-y0).toFixed(0)+'px) scale(0.34)';
    flyEl.style.opacity='0';
  },420);
}

var toastT=0;""")

sub("""  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);
  checkUnlocks();""",
"""  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);
  flyScore(pts); TAL_WAIT=0.62;
  checkUnlocks();""")

# the tally used to be written directly in four places; route them all
sub("""  if(chnEl) chnEl.textContent=SK.chain>1?('x'+SK.chain):'';
  if(tallyN) tallyN.textContent=PROG.score;""",
    "  if(chnEl) chnEl.textContent=SK.chain>1?('x'+SK.chain):'';")
sub("""  if(tallyN) tallyN.textContent=PROG.score;
  S.running=true; last=performance.now(); acc=0;
}""",
"""  setTally(PROG.score,true);
  S.running=true; last=performance.now(); acc=0;
}""")
sub("""  var tn=document.getElementById('t-score'); if(tn) tn.textContent=PROG.score;""",
    """  setTally(PROG.score,true);""")
sub("""  var tn=document.getElementById('t-score'); if(tn) tn.textContent=PROG.score;""",
    """  setTally(PROG.score,true);""") if s.count("var tn=document.getElementById('t-score')") else None

# ---- and the per frame work
sub("""  var slow=S.v.lengthSq()<4;
  hudEl.classList.toggle('idle', idleT>4 && !slow);
}""",
"""  var slow=S.v.lengthSq()<4;
  hudEl.classList.toggle('idle', idleT>4 && !slow);
  if(spdN){
    var kmh=Math.round(S.v.length()*3.6);
    if(kmh!==lastKmh){ spdN.textContent=kmh; lastKmh=kmh; }
  }
  tallyTick(dt);
}
var lastKmh=-1;""")

sub("var tallyN=null, tallyC=null", "var spdN=null, flyEl=null;\nvar tallyN=null, tallyC=null") \
    if "var tallyN=null, tallyC=null" in s else None

# ============================================================ the turntable
sub("""    GARAGE.ang+=dt*0.34;
    var R=9.6, hh=2.4;
    camera.position.set(S.p.x+Math.sin(GARAGE.ang)*R, S.p.y+hh, S.p.z+Math.cos(GARAGE.ang)*R);
    /* set, do not lerp: a lerp leaves the car off frame for the first second
       because the target is still travelling from wherever the chase cam was */
    camLook.copy(S.p).setY(S.p.y+0.10);""",
"""    GARAGE.ang+=dt*0.34;
    var R=10.4, hh=2.1;
    camera.position.set(S.p.x+Math.sin(GARAGE.ang)*R, S.p.y+hh, S.p.z+Math.cos(GARAGE.ang)*R);
    /* set, do not lerp: a lerp leaves the car off frame for the first second
       because the target is still travelling from wherever the chase cam was.
       Aim BELOW the car, which lifts it into the clear space above the card. */
    camLook.copy(S.p).setY(S.p.y-1.35);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
