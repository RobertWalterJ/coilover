# -*- coding: utf-8 -*-
"""Make the things that exist findable, and show the score while driving.

Everything here already worked. None of it was reachable.

The garage was the ninth button down a flat stack of nine, behind a menu
control that is an unlabelled eight pixel dot in the corner. The pedal modes
were the eighth. The points, the best run, the top speed and the segment bests
were all tracked and saved and only ever shown on the pause card, so while you
were actually driving there was no way to know you had scored anything beyond a
popup that leaves after a second.

That came from over applying your note that the HUD was too busy. Minimal was
the right call for the driving controls. It was the wrong call for finding your
cars and for knowing your score.

So: the menu is now three doors, DRIVE, GARAGE and SETTINGS, rather than a
stack. Every control option moved into Settings. The menu dot got a size and a
visible ring so it reads as a control. And there is a small running score in
the corner while you drive, with the chain multiplier beside it when one is
building, which is the thing you actually asked for.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------------------- the pause card
sub("""    <button class="go" id="b-resume">Drive</button>
    <button class="go ghost" id="b-flip">Upright the truck</button>
    <button class="go ghost" id="b-cam">Camera</button>
    <button class="go ghost" id="b-time">Light: Golden</button>
    <button class="go ghost" id="b-drift">Let it drift: off</button>
    <button class="go ghost" id="b-sound">Sound: on</button>
    <button class="go ghost" id="b-tilt">Tilt steering: off</button>
    <button class="go ghost" id="b-pedal">Pedals: two</button>
    <button class="go ghost" id="b-garage">Garage</button>""",
"""    <button class="go" id="b-resume">Drive</button>
    <div class="two">
      <button class="go ghost" id="b-garage">Garage</button>
      <button class="go ghost" id="b-settings">Settings</button>
    </div>
    <button class="go ghost" id="b-flip">Upright the truck</button>""")

# ------------------------------------------------------------- settings sheet
sub("""<div class="sheet" id="garage" hidden>""",
"""<div class="sheet" id="settings" hidden>
  <div class="card">
    <h1>Settings</h1>
    <div class="rule"></div>
    <div class="grp">Controls</div>
    <button class="go ghost" id="b-pedal">Pedals: two</button>
    <button class="go ghost" id="b-tilt">Tilt steering: off</button>
    <button class="go ghost" id="b-drift">Let it drift: off</button>
    <div class="grp">View and sound</div>
    <button class="go ghost" id="b-cam">Camera</button>
    <button class="go ghost" id="b-time">Light: Golden</button>
    <button class="go ghost" id="b-sound">Sound: on</button>
    <button class="go" id="b-setback">Back</button>
  </div>
</div>

<div class="sheet" id="garage" hidden>""")

# ------------------------------------------------------- the running score
sub("""<div id="chn"></div>""",
"""<div id="chn"></div>
<div id="tally"><b id="t-score">0</b><i id="t-chain"></i></div>""")

# ---------------------------------------------------------------------- css
sub("""  #b-menu::after{content:"";position:absolute;left:50%;top:50%;width:8px;height:8px;
                 margin:-4px 0 0 -4px;border-radius:50%;background:rgba(244,235,221,.40)}""",
"""  /* it was an eight pixel dot with no affordance, so nobody found the menu */
  #b-menu::after{content:"";position:absolute;left:50%;top:50%;width:26px;height:26px;
                 margin:-13px 0 0 -13px;border-radius:50%;
                 border:2px solid rgba(244,235,221,.42);
                 background:rgba(24,16,26,.30)}
  #b-menu::before{content:"";position:absolute;left:50%;top:50%;width:12px;height:2px;
                  margin:-1px 0 0 -6px;border-radius:1px;background:rgba(244,235,221,.72);
                  box-shadow:0 -5px 0 rgba(244,235,221,.72),0 5px 0 rgba(244,235,221,.72)}""")

sub("""  /* skill feedback: appears at the moment of the act, leaves on its own */""",
"""  /* the running score. Small, in the corner, and it is the only number on
     screen while driving, because the pedals are the rest of the HUD. */
  #tally{position:fixed;top:calc(11px + env(safe-area-inset-top));
         left:calc(13px + env(safe-area-inset-left));pointer-events:none;
         display:flex;align-items:baseline;gap:7px}
  #tally b{font-family:"Azeret Mono",monospace;font-weight:700;font-size:19px;
           color:var(--cream);text-shadow:0 2px 10px rgba(20,10,6,.9);
           font-variant-numeric:tabular-nums}
  #tally i{font-family:"Azeret Mono",monospace;font-style:normal;font-weight:700;
           font-size:13px;color:var(--amber);text-shadow:0 2px 8px rgba(20,10,6,.9)}
  #hud.idle ~ #tally{opacity:.55}

  .two{display:flex;gap:7px}
  .two .go{margin-top:7px}
  .grp{font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:.16em;
       color:var(--mute);margin:12px 0 2px}

  /* skill feedback: appears at the moment of the act, leaves on its own */""")

# --------------------------------------------------------------- wire it up
sub("""popEl=document.getElementById('pop'); popN=document.getElementById('popn');""",
"""tallyN=document.getElementById('t-score'); tallyC=document.getElementById('t-chain');
popEl=document.getElementById('pop'); popN=document.getElementById('popn');""")
sub("""var popEl,popN,popP,chnEl, popT=0;""",
    """var popEl,popN,popP,chnEl,tallyN,tallyC, popT=0;""")

# the score readout updates where the score changes, so it can never drift
sub("""  if(chnEl) chnEl.textContent=SK.chain>1?('x'+SK.chain):'';""",
"""  if(chnEl) chnEl.textContent=SK.chain>1?('x'+SK.chain):'';
  if(tallyN) tallyN.textContent=PROG.score;
  if(tallyC) tallyC.textContent=SK.chain>1?('x'+SK.chain):'';""")
sub("""  SK.chain=1; SK.run=0; SK.since=0; SK.fastFlag=false;""",
"""  SK.chain=1; SK.run=0; SK.since=0; SK.fastFlag=false;
  if(tallyC) tallyC.textContent='';""")

# ----------------------------------------------------------------- handlers
sub("""document.getElementById('b-garage').addEventListener('click',openGarage);""",
"""document.getElementById('b-garage').addEventListener('click',openGarage);
document.getElementById('b-settings').addEventListener('click',function(){
  show('menu',false); show('settings',true);
});
document.getElementById('b-setback').addEventListener('click',function(){
  show('settings',false); show('menu',true);
});""")

# the garage should come back to the menu, not straight to driving, so you can
# look at more than one car without restarting
sub("""function closeGarage(){
  GARAGE.on=false;
  camera.fov=54; camera.updateProjectionMatrix();
  show('garage',false);
  placeTruck(0,0,0.4);
  S.running=true; last=performance.now(); acc=0;
}""",
"""function closeGarage(){
  GARAGE.on=false;
  camera.fov=54; camera.updateProjectionMatrix();
  show('garage',false);
  placeTruck(0,0,0.4);
  if(tallyN) tallyN.textContent=PROG.score;
  S.running=true; last=performance.now(); acc=0;
}""")

# and show the score straight away rather than after the first point
sub("""  setPedalMode(Math.max(0,Math.min(2,m)));""",
"""  setPedalMode(Math.max(0,Math.min(2,m)));
  var tn=document.getElementById('t-score'); if(tn) tn.textContent=PROG.score;""")

# ------------------------------------------------------- more grain at dusk
sub("  uGrainAmt  :{value:1.05},", "  uGrainAmt  :{value:1.05},   /* per time, see TIMES */")
sub("""  STYLE_U.uBandLo.value=LF(A.bLo,B.bLo);""",
"""  STYLE_U.uBandLo.value=LF(A.bLo,B.bLo);
  STYLE_U.uGrainAmt.value=LF(A.grain,B.grain);
  STYLE_U.uGrainPost.value=LF(A.gpost,B.gpost);""")
for a, b in [("con:0.14, piv:0.30, shad:0x8090ca,", "con:0.14, piv:0.30, shad:0x8090ca, grain:1.10, gpost:0.50,"),
             ("con:0.10, piv:0.42, shad:0xa2b0dc,", "con:0.10, piv:0.42, shad:0xa2b0dc, grain:0.95, gpost:0.42,"),
             ("con:0.15, piv:0.32, shad:0x8f8cb8,", "con:0.15, piv:0.32, shad:0x8f8cb8, grain:1.05, gpost:0.46,"),
             ("con:0.18, piv:0.26, shad:0x5f78ca,", "con:0.18, piv:0.26, shad:0x5f78ca, grain:1.62, gpost:0.78,"),
             ("con:0.16, piv:0.21, shad:0x3f5cbc,", "con:0.16, piv:0.21, shad:0x3f5cbc, grain:1.48, gpost:0.70,")]:
    sub(a, b)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
