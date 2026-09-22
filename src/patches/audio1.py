# -*- coding: utf-8 -*-
"""Sound, and two steering fixes.

STEERING SIGN. The chase camera looks along the truck's forward axis. In a
Y up right handed frame that puts body right on the LEFT of the screen, so
steering toward body right read as turning left. Worse, ground steering and
air yaw disagreed with each other. Both are flipped at the point of use, so
the on screen arc still follows the thumb.

SNAPPIER. Full lock comes in at 95 px instead of 120, the response curve
softens less in the middle, and the rack itself moves faster.

SOUND. The engine was two sawtooths through a lowpass, which is a buzz, not a
motor. Now it is a real harmonic series through a periodic wave, tuned as a V8
so the firing frequency is rpm over sixty times four. On top of that:

  a starter that cranks and catches when you press Drive
  load dependent timbre, so the filter and the drive into the soft clipper
    both open up with the throttle
  five gears with an audible dip and chuff on each shift
  exhaust burble on the overrun, which is most of the character
  chassis rattle driven by how hard the suspension is actually working
  sand hiss under the tyres that rises with speed
  tyre scrub that tracks slip angle rather than just speed
  wind
  and a compressor on the end so none of it clips a phone speaker
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- steering
sub("""  var dmax=0.13 + 0.47/(1+Math.pow(speed/9.0,1.6)) + Math.min(0.28,Math.abs(beta));
  var steerAng=S.steer*dmax;""",
"""  var dmax=0.15 + 0.50/(1+Math.pow(speed/9.5,1.6)) + Math.min(0.28,Math.abs(beta));
  /* negated: the chase camera looks along the truck's forward axis, which puts
     body right on the left of the screen. Thumb left has to turn left. */
  var steerAng=-S.steer*dmax;""")

sub("""  var steerAng=S.steer*(0.13+0.47/(1+Math.pow(speed/9.0,1.6))+Math.min(0.28,Math.abs(beta2)));""",
    """  var steerAng=-S.steer*(0.15+0.50/(1+Math.pow(speed/9.5,1.6))+Math.min(0.28,Math.abs(beta2)));""")

sub("""    Tsum.addScaledVector(_bup,-S.steer*3000);""",
    """    Tsum.addScaledVector(_bup,S.steer*3000);""")

sub("  var LOCK=120, DEAD=5;", "  var LOCK=95, DEAD=4;")
sub("""    IN.steer=(d<0?-1:1)*Math.pow(Math.min(m,1),1.6);""",
    """    IN.steer=(d<0?-1:1)*Math.pow(Math.min(m,1),1.25);""")
sub("""    arcDot.style.left=(t.ox+IN.steer*62)+'px';""",
    """    arcDot.style.left=(t.ox+IN.steer*58)+'px';""")
sub("""  S.steer += (s-S.steer)*Math.min(1,dt*11);""",
    """  S.steer += (s-S.steer)*Math.min(1,dt*17);""")

# ---------------------------------------------------------------- suspension activity
sub("""    /* kick dust when the tyre is working */""",
"""    /* how hard the suspension is working, for the chassis rattle */
    if(c.lastLen===undefined) c.lastLen=c.len;
    susAct += Math.abs(c.len-c.lastLen); c.lastLen=c.len;

    /* kick dust when the tyre is working */""")

sub("""  var speed=S.v.length();
  var vbF2=S.v.dot(_bfwd), vbR2=S.v.dot(_brgt);""",
    """  var speed=S.v.length(), susAct=0;
  var vbF2=S.v.dot(_bfwd), vbR2=S.v.dot(_brgt);""")

sub("""  /* how hard the suspension is working, for the chassis rattle */
    if(c.lastLen===undefined) c.lastLen=c.len;""",
    """  /* how hard the suspension is working, for the chassis rattle */
    if(c.lastLen===undefined) c.lastLen=c.len;""")

sub("""  if(WINDMILL) WINDMILL.rotation.z+=dt*0.5;""",
    """  S.susAct = S.susAct*0.72 + susAct*0.28;
  if(WINDMILL) WINDMILL.rotation.z+=dt*0.5;""")

sub("  steer:0, throttle:0, brake:0, hand:0, rev:0, haptics:true, dip:0,",
    "  steer:0, throttle:0, brake:0, hand:0, rev:0, haptics:true, dip:0, susAct:0, crank:0,")

# ---------------------------------------------------------------- audio
a = s.index("/* ================= audio ================= */")
b = s.index("/* ================= HUD ================= */")
new_audio = '''/* ================= audio ================= */
var A=null;
function audioOn(){
  if(A||!S.sound) return;
  try{
    var Ctx=window.AudioContext||window.webkitAudioContext; if(!Ctx) return;
    var ctx=new Ctx();
    if(ctx.state==='suspended' && ctx.resume) ctx.resume();

    /* Everything lands on a compressor. Phone speakers clip early and a
       clipped engine is the difference between a motor and a fart. */
    var comp=ctx.createDynamicsCompressor();
    comp.threshold.value=-15; comp.knee.value=24; comp.ratio.value=8;
    comp.attack.value=0.004; comp.release.value=0.20;
    var master=ctx.createGain(); master.gain.value=0.62;
    comp.connect(master); master.connect(ctx.destination);

    /* ---- engine ----
       A real exhaust is a pulse train, not a sawtooth. Build the harmonic
       series directly and let the filter decide how much of it you hear. */
    var NH=14, real=new Float32Array(NH), imag=new Float32Array(NH);
    var H=[0,1,0.64,0.44,0.31,0.23,0.17,0.13,0.10,0.075,0.058,0.045,0.034,0.026];
    for(var i=1;i<NH;i++) imag[i]=H[i];
    var wave=ctx.createPeriodicWave(real,imag);

    var o1=ctx.createOscillator(); o1.setPeriodicWave(wave);
    var o2=ctx.createOscillator(); o2.setPeriodicWave(wave); o2.detune.value=-11;
    var sub=ctx.createOscillator(); sub.type='sine';

    var lp=ctx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=520; lp.Q.value=1.4;
    var shaper=ctx.createWaveShaper();
    var cs=new Float32Array(1024);
    for(var j=0;j<1024;j++){ var x=j/1023*2-1; cs[j]=Math.tanh(x*2.4); }
    shaper.curve=cs; shaper.oversample='2x';

    var drive=ctx.createGain(); drive.gain.value=1.0;      /* into the clipper */
    var eg=ctx.createGain(); eg.gain.value=0.0;
    var subg=ctx.createGain(); subg.gain.value=0.0;

    o1.connect(drive); o2.connect(drive);
    drive.connect(lp); lp.connect(shaper); shaper.connect(eg); eg.connect(comp);
    sub.connect(subg); subg.connect(comp);
    o1.start(); o2.start(); sub.start();

    /* one noise buffer, shared by everything that hisses or rattles */
    var len=Math.floor(ctx.sampleRate*2.2);
    var buf=ctx.createBuffer(1,len,ctx.sampleRate), ch=buf.getChannelData(0);
    for(var q=0;q<len;q++) ch[q]=Math.random()*2-1;

    function noiseBed(type,freq,Q){
      var src=ctx.createBufferSource(); src.buffer=buf; src.loop=true;
      var f=ctx.createBiquadFilter(); f.type=type; f.frequency.value=freq;
      if(Q) f.Q.value=Q;
      var g=ctx.createGain(); g.gain.value=0;
      src.connect(f); f.connect(g); g.connect(comp); src.start();
      return {g:g,f:f};
    }

    A={ctx:ctx, comp:comp, master:master, buf:buf,
       o1:o1, o2:o2, sub:sub, lp:lp, drive:drive, eg:eg, subg:subg,
       wind  :noiseBed('bandpass',520,0.7),
       scrub :noiseBed('bandpass',1700,2.4),
       sand  :noiseBed('bandpass',2900,0.9),
       rattle:noiseBed('bandpass',780,3.0),
       gear:1, burble:0, starter:null};
  }catch(e){ A=null; }
}

/* a starter motor, then it catches */
function engineStart(){
  if(!A) return;
  S.crank=1.05; S.rpm=0;
  var o=A.ctx.createOscillator(), g=A.ctx.createGain(), f=A.ctx.createBiquadFilter();
  o.type='sawtooth'; o.frequency.value=42;
  f.type='bandpass'; f.frequency.value=430; f.Q.value=2.2;
  g.gain.setValueAtTime(0.0001,A.ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.16,A.ctx.currentTime+0.05);
  g.gain.setValueAtTime(0.16,A.ctx.currentTime+0.62);
  g.gain.exponentialRampToValueAtTime(0.0001,A.ctx.currentTime+0.80);
  /* the crank wobble */
  var lfo=A.ctx.createOscillator(), lg=A.ctx.createGain();
  lfo.type='square'; lfo.frequency.value=9.5; lg.gain.value=16;
  lfo.connect(lg); lg.connect(o.frequency); lfo.start();
  o.connect(f); f.connect(g); g.connect(A.comp); o.start();
  o.stop(A.ctx.currentTime+0.84); lfo.stop(A.ctx.currentTime+0.84);
}

function pop(vol,freq){
  if(!A) return;
  var t=A.ctx.currentTime;
  var src=A.ctx.createBufferSource(); src.buffer=A.buf;
  var f=A.ctx.createBiquadFilter(); f.type='bandpass'; f.frequency.value=freq||240; f.Q.value=1.6;
  var g=A.ctx.createGain();
  g.gain.setValueAtTime(vol,t);
  g.gain.exponentialRampToValueAtTime(0.0008,t+0.09);
  src.connect(f); f.connect(g); g.connect(A.comp);
  src.start(t); src.stop(t+0.11);
}

var TOPS=[9,17,25,33,44];
function audioTick(dt){
  if(!A) return;
  var t=A.ctx.currentTime;
  var speed=S.v.length();

  /* gears, so the note rises and falls instead of droning */
  var g=0; while(g<4 && speed>TOPS[g]) g++;
  var lo=g===0?0:TOPS[g-1];
  var frac=Math.max(0,Math.min(1,(speed-lo)/(TOPS[g]-lo)));
  if(g+1!==A.gear){
    /* a shift you can hear: cut the note, chuff the exhaust */
    A.eg.gain.setTargetAtTime(0.010,t,0.012);
    pop(0.11,300);
    A.gear=g+1;
  }

  if(S.crank>0){ S.crank=Math.max(0,S.crank-dt); }

  var idle=760;
  var target=idle+frac*5600+(S.throttle>0.5?280:0);
  if(S.grounded===0) target=idle+3600+frac*1400;      /* free revs in the air */
  if(S.crank>0.25) target=210+Math.random()*90;        /* still cranking */
  S.rpm += (target-S.rpm)*Math.min(1,dt*(S.throttle>0.4?7.0:3.4));

  /* V8: four firing pulses per revolution on a four stroke */
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
  }

  /* wind, sand, scrub, rattle */
  A.wind.g.gain.setTargetAtTime(Math.min(0.085,speed*speed*0.00009),t,0.10);
  A.wind.f.frequency.setTargetAtTime(420+speed*13,t,0.15);

  var onGround=S.grounded>0;
  A.sand.g.gain.setTargetAtTime(onGround?Math.min(0.055,speed*0.0032):0,t,0.09);

  var slip=0;
  for(var i=0;i<4;i++) if(corners[i].contact) slip+=Math.abs(corners[i].alphaF);
  A.scrub.g.gain.setTargetAtTime(Math.min(0.13,slip*0.075),t,0.05);
  A.scrub.f.frequency.setTargetAtTime(1300+Math.min(1400,slip*900),t,0.08);

  A.rattle.g.gain.setTargetAtTime(Math.min(0.075,S.susAct*2.6),t,0.05);
}

function blip(fr,dur,type,vol){
  if(!A) return;
  var o=A.ctx.createOscillator(), g=A.ctx.createGain();
  o.type=type||'sine'; o.frequency.value=fr;
  g.gain.setValueAtTime(vol||0.15,A.ctx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.0008,A.ctx.currentTime+dur);
  o.connect(g); g.connect(A.comp); o.start(); o.stop(A.ctx.currentTime+dur+0.02);
}
function chime(){
  blip(660,0.16,'triangle',0.12);
  setTimeout(function(){ blip(990,0.24,'triangle',0.10); },95);
}
function thump(v){
  if(!A) return;
  var t=A.ctx.currentTime;
  /* body of the hit */
  var o=A.ctx.createOscillator(), og=A.ctx.createGain();
  o.type='sine'; o.frequency.setValueAtTime(96,t);
  o.frequency.exponentialRampToValueAtTime(38,t+0.16);
  og.gain.setValueAtTime(0.30*v,t);
  og.gain.exponentialRampToValueAtTime(0.001,t+0.24);
  o.connect(og); og.connect(A.comp); o.start(t); o.stop(t+0.26);
  /* the tyre and the bump stop */
  var nsrc=A.ctx.createBufferSource(); nsrc.buffer=A.buf;
  var f=A.ctx.createBiquadFilter(); f.type='lowpass'; f.frequency.value=520;
  var ng=A.ctx.createGain();
  ng.gain.setValueAtTime(0.26*v,t);
  ng.gain.exponentialRampToValueAtTime(0.001,t+0.20);
  nsrc.connect(f); f.connect(ng); ng.connect(A.comp);
  nsrc.start(t); nsrc.stop(t+0.22);
}

'''
s = s[:a] + new_audio + s[b:]
n += 1

# audioTick now needs dt, and the engine should crank when you press Drive
sub("    hud(dt); audioTick();", "    hud(dt); audioTick(dt);")
sub("""  audioOn(); show('intro',false); S.running=true; last=performance.now(); acc=0;""",
    """  audioOn(); engineStart(); show('intro',false); S.running=true; last=performance.now(); acc=0;""")
sub("  if(A) A.master.gain.value=S.sound?0.5:0; else if(S.sound) audioOn();",
    "  if(A) A.master.gain.value=S.sound?0.62:0; else if(S.sound) audioOn();")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
