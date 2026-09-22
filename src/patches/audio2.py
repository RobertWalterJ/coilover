# -*- coding: utf-8 -*-
"""A meatier engine with rally bangs, and a tyre that stops tripping on pebbles.

ENGINE. It was pitched as a V8 at four firing pulses per revolution, which put
the fundamental up around 150 Hz where it reads thin and buzzy. Dropped to two
and a half pulses so the note sits low, with two sub octaves under it and more
level, so it has weight.

BANGS. Real anti lag crackle is not the gentle burble it had. Lifting off the
throttle at revs now fires a burst of three to seven sharp cracks over about
half a second, brighter and louder than the idle burble, plus a dump valve
chirp. There is a turbo whistle that rises with load underneath it all.

CONTACT PATCH. A single downward ray sees a one centimetre pebble as a one
centimetre step and launches the truck off it. A real tyre bridges it. Each
wheel now samples five points across its own footprint and takes a weighted
blend of the highest and the mean, which is the standard fix and is most of
why raycast vehicles feel skittish without it.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- contact patch
sub("""var _n1=new THREE.Vector3();
function normalAt(x,z,out){""",
"""var _n1=new THREE.Vector3();

/* Five samples across the tyre's footprint, weighted toward the highest.
   One ray treats a pebble as a step and throws the truck; a tyre bridges it. */
function envHeight(px,pz,fx,fz,rx,rz){
  var h0=height(px,pz);
  var a=height(px+fx*0.26,pz+fz*0.26), b=height(px-fx*0.26,pz-fz*0.26);
  var c=height(px+rx*0.13,pz+rz*0.13), d=height(px-rx*0.13,pz-rz*0.13);
  var mx=Math.max(h0,Math.max(Math.max(a,b),Math.max(c,d)));
  var mean=(h0+a+b+c+d)*0.2;
  return mx*0.68+mean*0.32;
}

function normalAt(x,z,out){""")

sub("""    var t=SUS_MAX;
    for(var it=0; it<2; it++){
      var px=_wp.x+_dir.x*t, pz=_wp.z+_dir.z*t;
      var gy=height(px,pz);
      normalAt(px,pz,_nrm);""",
"""    var t=SUS_MAX;
    for(var it=0; it<2; it++){
      var px=_wp.x+_dir.x*t, pz=_wp.z+_dir.z*t;
      var gy=envHeight(px,pz,_bfwd.x,_bfwd.z,_brgt.x,_brgt.z);
      normalAt(px,pz,_nrm);""")

# ---------------------------------------------------------------- engine
sub("""    var o1=ctx.createOscillator(); o1.setPeriodicWave(wave);
    var o2=ctx.createOscillator(); o2.setPeriodicWave(wave); o2.detune.value=-11;
    var sub=ctx.createOscillator(); sub.type='sine';""",
"""    var o1=ctx.createOscillator(); o1.setPeriodicWave(wave);
    var o2=ctx.createOscillator(); o2.setPeriodicWave(wave); o2.detune.value=-11;
    var sub=ctx.createOscillator(); sub.type='sine';
    var sub2=ctx.createOscillator(); sub2.type='triangle';   /* an octave lower again */
    var turbo=ctx.createOscillator(); turbo.type='sine';""")

sub("""    o1.connect(drive); o2.connect(drive);
    drive.connect(lp); lp.connect(shaper); shaper.connect(eg); eg.connect(comp);
    sub.connect(subg); subg.connect(comp);
    o1.start(); o2.start(); sub.start();""",
"""    var sub2g=ctx.createGain(); sub2g.gain.value=0.0;
    var turbog=ctx.createGain(); turbog.gain.value=0.0;

    o1.connect(drive); o2.connect(drive);
    drive.connect(lp); lp.connect(shaper); shaper.connect(eg); eg.connect(comp);
    sub.connect(subg); subg.connect(comp);
    sub2.connect(sub2g); sub2g.connect(comp);
    turbo.connect(turbog); turbog.connect(comp);
    o1.start(); o2.start(); sub.start(); sub2.start(); turbo.start();""")

sub("""    A={ctx:ctx, comp:comp, master:master, buf:buf,
       o1:o1, o2:o2, sub:sub, lp:lp, drive:drive, eg:eg, subg:subg,""",
"""    A={ctx:ctx, comp:comp, master:master, buf:buf,
       o1:o1, o2:o2, sub:sub, sub2:sub2, turbo:turbo, lp:lp, drive:drive,
       eg:eg, subg:subg, sub2g:sub2g, turbog:turbog,""")

# a noise burst at a scheduled time, for crackle
sub("""function pop(vol,freq){""",
"""function popAt(when,vol,freq,dur){
  if(!A) return;
  var src=A.ctx.createBufferSource(); src.buffer=A.buf;
  src.playbackRate.value=0.8+Math.random()*0.7;
  var f=A.ctx.createBiquadFilter(); f.type='bandpass'; f.frequency.value=freq; f.Q.value=1.1;
  var g=A.ctx.createGain();
  g.gain.setValueAtTime(0.0001,when);
  g.gain.exponentialRampToValueAtTime(vol,when+0.004);
  g.gain.exponentialRampToValueAtTime(0.0006,when+(dur||0.075));
  src.connect(f); f.connect(g); g.connect(A.comp);
  src.start(when); src.stop(when+(dur||0.075)+0.03);
}

/* Anti lag. Lift off at revs and the exhaust lets go properly. */
function crackle(intensity){
  if(!A) return;
  var t=A.ctx.currentTime+0.02;
  var count=3+Math.floor(Math.random()*5);
  popAt(t,0.16*intensity,240,0.11);                 /* the first one is the bang */
  for(var i=1;i<count;i++){
    t += 0.035+Math.random()*0.085;
    popAt(t,(0.07+Math.random()*0.10)*intensity, 420+Math.random()*1100, 0.05);
  }
  /* dump valve, a short falling chirp */
  var src=A.ctx.createBufferSource(); src.buffer=A.buf;
  var f=A.ctx.createBiquadFilter(); f.type='bandpass'; f.Q.value=5.0;
  var t0=A.ctx.currentTime;
  f.frequency.setValueAtTime(3400,t0);
  f.frequency.exponentialRampToValueAtTime(900,t0+0.16);
  var g=A.ctx.createGain();
  g.gain.setValueAtTime(0.09*intensity,t0);
  g.gain.exponentialRampToValueAtTime(0.0008,t0+0.18);
  src.connect(f); f.connect(g); g.connect(A.comp);
  src.start(t0); src.stop(t0+0.20);
}

function pop(vol,freq){""")

# ---------------------------------------------------------------- tick
sub("""  /* V8: four firing pulses per revolution on a four stroke */
  var f0=Math.max(12,S.rpm/60*4);
  A.o1.frequency.setTargetAtTime(f0,t,0.02);
  A.o2.frequency.setTargetAtTime(f0*1.004,t,0.02);
  A.sub.frequency.setTargetAtTime(f0*0.5,t,0.03);

  /* timbre opens with load, not with speed */
  var load=S.throttle;
  A.lp.frequency.setTargetAtTime(360+load*2600+frac*1100+(S.grounded===0?400:0),t,0.04);
  A.drive.gain.setTargetAtTime(0.8+load*1.7,t,0.05);

  var want=(S.crank>0?0.02:0.030)+load*0.055+(S.grounded===0?0.010:0);
  A.eg.gain.setTargetAtTime(want,t,0.05);
  A.subg.gain.setTargetAtTime(S.crank>0?0.0:0.026+load*0.030,t,0.06);

  /* Overrun burble. Off the throttle at revs, the exhaust pops, and this is
     most of what makes an engine sound like an engine rather than a tone. */
  A.burble-=dt;
  if(load<0.22 && S.rpm>2100 && A.burble<=0 && S.crank<=0){
    pop(0.05+Math.random()*0.05, 170+Math.random()*160);
    A.burble=0.045+Math.random()*0.10;
  }""",
"""  /* Two and a half pulses a rev rather than four. Lower fundamental, more
     weight, less buzz. */
  var f0=Math.max(10,S.rpm/60*2.5);
  A.o1.frequency.setTargetAtTime(f0,t,0.02);
  A.o2.frequency.setTargetAtTime(f0*1.004,t,0.02);
  A.sub.frequency.setTargetAtTime(f0*0.5,t,0.03);
  A.sub2.frequency.setTargetAtTime(f0*0.25,t,0.04);

  /* timbre opens with load, not with speed */
  var load=S.throttle;
  A.lp.frequency.setTargetAtTime(300+load*2800+frac*1200+(S.grounded===0?400:0),t,0.04);
  A.drive.gain.setTargetAtTime(0.9+load*2.1,t,0.05);

  var want=(S.crank>0?0.026:0.042)+load*0.070+(S.grounded===0?0.012:0);
  A.eg.gain.setTargetAtTime(want,t,0.05);
  A.subg.gain.setTargetAtTime(S.crank>0?0.0:0.040+load*0.046,t,0.06);
  A.sub2g.gain.setTargetAtTime(S.crank>0?0.0:0.022+load*0.030,t,0.08);

  /* turbo, spooling with load and revs */
  var spool=load*Math.min(1,S.rpm/4200);
  A.turbo.frequency.setTargetAtTime(1500+S.rpm*0.62,t,0.09);
  A.turbog.gain.setTargetAtTime(spool*0.016,t,0.10);

  /* Lift off at revs and it bangs. This is the rally sound. */
  var lifted=(S.prevThr>0.45 && load<0.20 && S.rpm>2000 && S.crank<=0);
  if(lifted) crackle(Math.min(1,(S.rpm-2000)/2600+0.45));
  S.prevThr=load;

  /* and a quieter idle burble between the big ones */
  A.burble-=dt;
  if(load<0.22 && S.rpm>1900 && A.burble<=0 && S.crank<=0 && !lifted){
    popAt(t+0.01,0.045+Math.random()*0.05, 180+Math.random()*220, 0.06);
    A.burble=0.06+Math.random()*0.16;
  }""")

sub("  gearFrac:0, shifted:false,", "  gearFrac:0, shifted:false, prevThr:0,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
