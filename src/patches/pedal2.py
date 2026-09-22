# -*- coding: utf-8 -*-
"""Three pedal modes, and a gauge that shows you what your thumb is doing.

TWO is still the default because you said you prefer it. ONE is the single
control: press for a light throttle, slide up for more, and slide down past a
marked point for ever more brake. ARCADE is the old way, all or nothing on
press, for when you just want to hold it flat.

The part that was missing from all of them is feedback. You could not see how
much foot you had in it, and nothing on screen said which direction on the
screen bought you more. So every analogue ring now carries a gauge:

  a marker that sits exactly where your thumb is on the axis
  a fill that grows from the neutral line toward the marker
  green when that fill is throttle, maroon when it is brake
  a neutral line, and a faint band showing the dead part below it

In one pedal mode the neutral line sits across the middle of the ring, so up is
visibly throttle and down is visibly brake, and the dead band between them is
drawn rather than guessed at.

Also: the roof light bar was floating 26.5 cm above the roof attached to
nothing. It has legs now.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:100].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------------------------- markup
sub("""  <button class="ring" id="brake" aria-label="Brake"></button>
  <button class="ring" id="gas" aria-label="Gas"></button>""",
"""  <button class="ring" id="brake" aria-label="Brake"><span class="gf"></span><span class="gz"></span><span class="gm"></span></button>
  <button class="ring" id="gas" aria-label="Gas"><span class="gd"></span><span class="gf"></span><span class="gz"></span><span class="gm"></span></button>""")

sub("""    <button class="go ghost" id="b-tilt">Tilt steering: off</button>""",
    """    <button class="go ghost" id="b-tilt">Tilt steering: off</button>
    <button class="go ghost" id="b-pedal">Pedals: two</button>""")

# ---------------------------------------------------------------------- css
sub("""  .ring.on{border-color:rgba(244,235,221,.78);background:rgba(244,235,221,.12);transform:scale(.965)}""",
"""  .ring.on{border-color:rgba(244,235,221,.78);transform:scale(.965)}

  /* the gauge inside a ring. Clipped to the circle, so the fill reads as a
     level in a round window rather than as a rectangle sitting on top. */
  .ring{overflow:hidden}
  .ring>span{position:absolute;left:0;right:0;display:block;pointer-events:none}
  .gd{top:0;bottom:0;opacity:0}                       /* the dead band */
  .gf{height:0;bottom:0;opacity:0;transition:opacity .10s}   /* the fill */
  .gz{height:1px;top:50%;background:rgba(244,235,221,.42);opacity:0}
  .gm{height:2px;top:0;opacity:0;background:rgba(255,246,232,.95);
      box-shadow:0 0 6px rgba(255,246,232,.55)}
  .ring.on .gf,.ring.on .gm{opacity:1}
  #gas.two .gz{opacity:0}
  #gas.one.on .gz{opacity:1}
  #gas.one.on .gd{opacity:1}""")

# a green and a maroon that sit in this palette rather than fighting it
sub("""  #brake.slide{border-color:rgba(255,180,84,.85)}""",
"""  #brake.slide{border-color:rgba(255,180,84,.85)}
  :root{--go:#4f9d68;--stop:#9b3040}""")

# ------------------------------------------------------------- the gauge fn
sub("""/* the ring fills as you push, so pedal pressure is visible without looking */
function pedalFill(el,v){
  el.style.background = v>0
    ? 'rgba(244,235,221,'+(0.05+0.26*v).toFixed(3)+')'
    : '';
}""",
"""/* Draw the gauge. `axis` is where the thumb sits on the control, 0 at the
   bottom of the ring and 1 at the top. `zero` is where no input lives. The
   fill runs between the two, and its colour says which side of neutral you
   are on, so the direction that buys more is never in doubt. */
function pedalGauge(el,gas,brake,axis,zero,deadLo,deadHi){
  var f=el.querySelector('.gf'), m=el.querySelector('.gm'),
      z=el.querySelector('.gz'), d=el.querySelector('.gd');
  if(!f) return;
  var lo=Math.min(axis,zero), hi=Math.max(axis,zero);
  f.style.bottom=(lo*100).toFixed(1)+'%';
  f.style.height=Math.max(0,(hi-lo)*100).toFixed(1)+'%';
  f.style.background = (brake>0.001) ? 'var(--stop)' : 'var(--go)';
  f.style.opacity = (gas>0.001||brake>0.001) ? '0.62' : '0.16';
  m.style.top=((1-axis)*100).toFixed(1)+'%';
  if(z) z.style.top=((1-zero)*100).toFixed(1)+'%';
  if(d && deadHi>deadLo){
    d.style.bottom=(deadLo*100).toFixed(1)+'%';
    d.style.top=((1-deadHi)*100).toFixed(1)+'%';
    d.style.background='rgba(244,235,221,.10)';
  }
  el.style.background = (gas>0.001||brake>0.001)
    ? 'rgba(244,235,221,'+(0.04+0.10*Math.max(gas,brake)).toFixed(3)+')' : '';
}
function pedalClear(el){
  var f=el.querySelector('.gf'), m=el.querySelector('.gm');
  if(f){ f.style.height='0%'; f.style.opacity='0'; }
  if(m) m.style.opacity='';
  el.style.background='';
}""")

# ------------------------------------------------------- mode + touch logic
sub("""var IN={gas:0,brake:0,hand:0,steer:0,revHold:0};""",
"""var IN={gas:0,brake:0,hand:0,steer:0,revHold:0};
/* 0 two pedals, 1 one pedal, 2 arcade */
var PEDAL_MODE=0;
var PEDAL_NAMES=['two','one','arcade'];
/* one pedal geometry, all in ring fractions so the gauge and the input agree
   by construction rather than by me keeping two numbers in step */
var P1_ZERO=0.42, P1_DEAD=0.07, P1_TRAVEL=170;""")

sub("""    var br=brakeEl.getBoundingClientRect();            /* brake sits inside the gas zone */
    if(x>br.left-12 && x<br.right+12 && y>br.top-12 && y<br.bottom+12) return 'brake';""",
"""    if(PEDAL_MODE!==1){
      var br=brakeEl.getBoundingClientRect();          /* brake sits inside the gas zone */
      if(x>br.left-12 && x<br.right+12 && y>br.top-12 && y<br.bottom+12) return 'brake';
    }""")

sub("""    /* a press gives you the middle of the pedal, not all of it */
    if(kind==='gas'){ IN.gas=0.60; gasEl.classList.add('on'); pedalFill(gasEl,0.60); }
    if(kind==='brake'){ IN.brake=0.50; IN.revHold=0; brakeEl.classList.add('on'); pedalFill(brakeEl,0.50); }""",
"""    if(kind==='gas'){
      gasEl.classList.add('on');
      if(PEDAL_MODE===2){ IN.gas=1; IN.brake=0; pedalGauge(gasEl,1,0,1,0,0,0); }
      else if(PEDAL_MODE===1){ applyOnePedal(0); }
      else { IN.gas=0.60; pedalGauge(gasEl,0.60,0,0.60,0,0,0); }
    }
    if(kind==='brake'){
      brakeEl.classList.add('on'); IN.revHold=0;
      if(PEDAL_MODE===2){ IN.brake=1; pedalGauge(brakeEl,0,1,1,0,0,0); }
      else { IN.brake=0.50; pedalGauge(brakeEl,0,0.50,0.50,0,0,0); }
    }""")

sub("""    if(t && t.kind==='gas'){
      /* slide up for more throttle, down for less */
      IN.gas=Math.max(0.08,Math.min(1,0.60-(e.clientY-t.oy)/160));
      pedalFill(gasEl,IN.gas);
      return;
    }
    if(t && t.kind==='brake'){
      /* push the pedal down: sliding down is more brake */
      IN.brake=Math.max(0.08,Math.min(1,0.50+(e.clientY-t.oy)/160));
      pedalFill(brakeEl,IN.brake);
      return;
    }""",
"""    if(t && t.kind==='gas'){
      if(PEDAL_MODE===2) return;                       /* arcade does not modulate */
      if(PEDAL_MODE===1){ applyOnePedal(e.clientY-t.oy); return; }
      /* slide up for more throttle, down for less */
      IN.gas=Math.max(0.08,Math.min(1,0.60-(e.clientY-t.oy)/160));
      pedalGauge(gasEl,IN.gas,0,IN.gas,0,0,0);
      return;
    }
    if(t && t.kind==='brake'){
      if(PEDAL_MODE===2) return;
      /* push the pedal down: sliding down is more brake */
      IN.brake=Math.max(0.08,Math.min(1,0.50+(e.clientY-t.oy)/160));
      pedalGauge(brakeEl,0,IN.brake,IN.brake,0,0,0);
      return;
    }""")

sub("""    if(t.kind==='gas'){ IN.gas=0; gasEl.classList.remove('on'); pedalFill(gasEl,0); }
    if(t.kind==='brake'){ IN.brake=0; IN.revHold=0; brakeEl.classList.remove('on'); pedalFill(brakeEl,0); }""",
"""    if(t.kind==='gas'){
      IN.gas=0; if(PEDAL_MODE===1){ IN.brake=0; IN.revHold=0; }
      gasEl.classList.remove('on'); pedalClear(gasEl);
    }
    if(t.kind==='brake'){ IN.brake=0; IN.revHold=0; brakeEl.classList.remove('on'); pedalClear(brakeEl); }""")

sub("""    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    pedalFill(gasEl,0); pedalFill(brakeEl,0);""",
"""    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    pedalClear(gasEl); pedalClear(brakeEl);""")

# the one pedal law, next to the touch code that uses it
sub("""  var t0y=0;
  function down(e){""",
"""  /* One pedal. Press lands a little above neutral so you set off gently.
     Sliding up is throttle. Sliding down crosses neutral, then a dead band you
     can see on the gauge, then brake, which deepens the further you go. */
  window.applyOnePedal=function(dy){
    var v=P1_ZERO-dy/P1_TRAVEL;
    v=Math.max(-0.35,Math.min(1.02,v));
    var thr=Math.max(0,Math.min(1,v));
    var brk=Math.max(0,Math.min(1,(-v-P1_DEAD)/0.28));
    IN.gas=thr; IN.brake=brk;
    if(brk<=0) IN.revHold=0;
    /* axis is the thumb's place on the ring: neutral maps to the zero line */
    var axis = v>=0 ? (0.5+v*0.5) : (0.5+v*0.5);
    axis=Math.max(0.02,Math.min(0.98,axis));
    pedalGauge(gasEl,thr,brk,axis,0.5,0.5-(P1_DEAD*0.5)-0.001,0.5);
  };

  var t0y=0;
  function down(e){""")

# ---------------------------------------------------------------- the option
sub("""document.getElementById('b-tilt').addEventListener('click',function(){""",
"""function setPedalMode(m){
  PEDAL_MODE=m;
  var b=document.getElementById('b-pedal');
  if(b) b.textContent='Pedals: '+PEDAL_NAMES[m];
  gasEl.classList.toggle('one',m===1);
  gasEl.classList.toggle('two',m!==1);
  brakeEl.style.display=(m===1)?'none':'';
  IN.gas=IN.brake=0; IN.revHold=0;
  gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
  pedalClear(gasEl); pedalClear(brakeEl);
  try{ localStorage.setItem('coilover.pedal',String(m)); }catch(_){}
}
document.getElementById('b-pedal').addEventListener('click',function(){
  setPedalMode((PEDAL_MODE+1)%3);
});

document.getElementById('b-tilt').addEventListener('click',function(){""")

sub("""/* ================= go ================= */
resize();""",
"""/* ================= go ================= */
(function(){
  var m=0; try{ m=parseInt(localStorage.getItem('coilover.pedal')||'0',10)||0; }catch(_){}
  setPedalMode(Math.max(0,Math.min(2,m)));
})();
resize();""")

# ------------------------------------------------- the light bar gets legs
sub("""  box(1.10,0.13,0.17, trim, 0, 1.82, 0.02, false);    /* roof light bar */""",
"""  /* it was floating 26.5 cm above the roof attached to nothing */
  [[-0.42],[0.42]].forEach(function(pp){
    box(0.06,0.28,0.06, trim, pp[0],1.63,0.02, false);
  });
  box(1.10,0.13,0.17, trim, 0, 1.82, 0.02, false);    /* roof light bar */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
