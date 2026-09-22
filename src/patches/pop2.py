# -*- coding: utf-8 -*-
"""One number for the whole life of an award, instead of two.

THE DOUBLING. The award drew its value in `#pop` for 1.15 s AND spawned a
separate `#fly` element with the same figure on it half a second later, so for
most of a second there were two `+N`s on screen saying the same thing, one
sitting still and one leaving. That is what you are seeing.

There is one element now and it does the whole job:

  1. WHILE THE TRICK RUNS it counts. A drift is scored on metres carried, and
     that number exists every frame it is running, so the figure on screen is
     the live value and it climbs as you hold the slide. Same for a jump, where
     it climbs with air time and distance covered, and for two wheels.
  2. WHEN THE TRICK ENDS it stops on the final figure and holds it for half a
     second, so you can read what you got.
  3. THEN IT SHRINKS AND DISSOLVES into the corner, and the total counts up as
     it arrives.

Instant awards -- flat out, a landmark, a feat, a completed run -- skip stage
one and start at the hold, because there is nothing to count.

`#fly` is gone entirely, along with `flyScore`.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- the second element goes
sub('<div id="fly"></div>\n', '')
sub("""  /* the award, on its way into the total */
  #fly{position:fixed;left:0;top:0;pointer-events:none;opacity:0;
       font-family:"Azeret Mono",monospace;font-weight:700;font-size:30px;
       color:var(--amber);text-shadow:0 2px 12px rgba(30,16,8,.85);
       transform:translate(-50%,-50%)}""",
"""  /* the pop is what folds into the corner, so its transform is animated and
     its own transition must not fight the one set on it in script */
  #pop{will-change:transform,opacity}""")
sub("spdN=document.getElementById('spd-n'); flyEl=document.getElementById('fly');",
    "spdN=document.getElementById('spd-n');")

sub("""/* the award, folding down into the corner it is being added to */
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
}""",
"""/* ---- the award, from the first metre of the trick to the corner ----
   One element the whole way: counting while the trick runs, holding when it
   ends, then folding into the total. Phases: 1 counting, 2 holding, 3 folding.
   There used to be a second element flying alongside it saying the same thing,
   which is the doubling you could see. */
var POP={ph:0, t:0};
function popReset(){
  popEl.style.transition='none';
  popEl.style.transform='translate(-50%,-50%) scale(1)';
  popEl.style.opacity='';
  void popEl.offsetWidth;
}
/* called every frame a trick is accruing */
function popLive(name,pts){
  if(!popEl) return;
  pts=Math.max(1,Math.round(pts*SK.chain));
  if(POP.ph!==1){ popReset(); popEl.className='on'; POP.ph=1; }
  popN.textContent=name;
  popP.textContent='+'+pts;
  POP.t=0;
}
/* called when the points are actually banked */
function popHold(name,pts){
  if(!popEl) return;
  if(POP.ph!==1) popReset();
  popEl.className='on';
  popN.textContent=name;
  popP.textContent='+'+pts;
  POP.ph=2; POP.t=0;
}
function popFold(){
  if(!popEl||!tallyN||POP.ph===3){ if(popEl) popEl.className=''; POP.ph=0; return; }
  var pr=popEl.getBoundingClientRect(), tr=tallyN.getBoundingClientRect();
  popEl.style.transition='transform .40s cubic-bezier(.36,0,.22,1),opacity .40s ease';
  popEl.style.transform='translate(-50%,-50%) translate('+
    ((tr.left+tr.width/2)-(pr.left+pr.width/2)).toFixed(0)+'px,'+
    ((tr.top+tr.height/2)-(pr.top+pr.height/2)).toFixed(0)+'px) scale(0.24)';
  popEl.style.opacity='0';
  POP.ph=3; POP.t=0;
  if(TAL_WAIT<=0) TAL_WAIT=0.26;      /* the total arrives with it */
}
function popStep(dt){
  if(!POP.ph) return;
  POP.t+=dt;
  /* a live count whose trick has stopped feeding it has been abandoned */
  if(POP.ph===1){ if(POP.t>0.35) popFold(); }
  else if(POP.ph===2){ if(POP.t>0.50) popFold(); }     /* the half second hold */
  else if(POP.ph===3){ if(POP.t>0.42){ popEl.className=''; POP.ph=0; } }
}""")

# ---- award hands over to the hold, and stops spawning a second element
sub("""  if(popN){
    popN.textContent=name;
    popP.textContent='+'+pts;
    popEl.className='on'; popT=1.15;
  }""",
"""  popHold(name,pts);""")
sub("""  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);
  flyScore(pts); if(TAL_WAIT<=0) TAL_WAIT=0.62;
  checkUnlocks();""",
"""  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);
  checkUnlocks();""")

# ---- the other places that drove the pop by hand
sub("""      if(popN){ popN.textContent='Run complete';
                popP.textContent='+'+r.pts; popEl.className='on'; popT=2.0; }
      chime(); buzz(38); flyScore(r.pts); if(TAL_WAIT<=0) TAL_WAIT=0.62;""",
"""      popHold('Run complete','+'+commas(r.pts));
      chime(); buzz(38);""")
sub("""      if(popN){ popN.textContent=label+' unlocked';
                popP.textContent=o.name; popEl.className='on'; popT=2.4; }""",
"""      popHold(label+' unlocked',o.name); POP.t=-1.6;   /* this one lingers */""")
sub("""        if(popN){ popN.textContent=SK.seg.name; popP.textContent='best '+SK.segPts;
                  popEl.className='on'; popT=1.4; }""",
"""        popHold(SK.seg.name,'best '+commas(SK.segPts)); POP.t=-0.7;""")

# popHold prefixes a plus; these three pass their own text, so strip it there
sub("""  popN.textContent=name;
  popP.textContent='+'+pts;
  POP.ph=2; POP.t=0;""",
"""  popN.textContent=name;
  popP.textContent=(typeof pts==='number')? ('+'+pts) : pts;
  POP.ph=2; POP.t=0;""")

# ---- run the phase machine instead of the old countdown
sub("    if(popT>0){ popT-=dt; if(popT<=0 && popEl) popEl.className=''; }",
    "    popStep(dt);")
sub("        if(window.__fa>=1/60){ sync(1/60); updateLightPool(); updateCam(1/60); revs(1/60); hud(1/60); audioTick(1/60); window.__fa-=1/60; }",
    "        if(window.__fa>=1/60){ sync(1/60); updateLightPool(); updateCam(1/60); revs(1/60); hud(1/60); popStep(1/60); audioTick(1/60); window.__fa-=1/60; }")

# ================================================= the live counts themselves
sub("""  if(S.grounded>=3 && sp>8 && Math.abs(beta)>0.22){
    SK.drift.on=true; SK.drift.dist+=d;
    SK.drift.peak=Math.max(SK.drift.peak,Math.abs(beta));
  }else if(SK.drift.on){""",
"""  if(S.grounded>=3 && sp>8 && Math.abs(beta)>0.22){
    SK.drift.on=true; SK.drift.dist+=d;
    SK.drift.peak=Math.max(SK.drift.peak,Math.abs(beta));
    /* the same figure the award will bank, shown as it accrues */
    if(SK.drift.dist>16)
      popLive(driftName(SK.drift.dist), SK.drift.dist*1.15*(1+SK.drift.peak));
  }else if(SK.drift.on){""")

sub("""  if(((lft===2&&rgt===0)||(rgt===2&&lft===0)) && lean>0.34 && sp>5){
    SK.two.on=true; SK.two.dist+=d;
  }else if(SK.two.on){""",
"""  if(((lft===2&&rgt===0)||(rgt===2&&lft===0)) && lean>0.34 && sp>5){
    SK.two.on=true; SK.two.dist+=d;
    if(SK.two.dist>9) popLive('Two wheels', SK.two.dist*2.2);
  }else if(SK.two.on){""")

# and the jump, which climbs with air time and ground covered
sub("""  if(!SK.fastFlag && sp>33 && S.grounded>0){ SK.fastFlag=true; award('Flat out',55); }""",
"""  if(!SK.fastFlag && sp>33 && S.grounded>0){ SK.fastFlag=true; award('Flat out',55); }
  /* a jump is worth air time plus ground covered, and both are known while
     you are still in the air, so it counts on the way over */
  if(S.grounded===0 && S.airT>0.45 && S.airFrom){
    var adist=Math.hypot(S.p.x-S.airFrom.x, S.p.z-S.airFrom.z);
    popLive(airName(S.airT,adist), 26*S.airT + 2.6*adist);
  }""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
