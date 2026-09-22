# -*- coding: utf-8 -*-
"""Real engine assets, generated rather than fetched.

Oscillators are why it does not sound like an engine. An engine is not a tone,
it is a train of exhaust pulses, each one a sharp pressure spike ringing
through a pipe, repeating at the firing rate, with the cylinders slightly
uneven. That is a WAVEFORM, and the way games do it is to play a recorded loop
back at a pitch set by the revs.

We cannot fetch audio files: the artifact CSP blocks media, and the local build
has to run with no signal. So the samples are BAKED at load instead, into two
AudioBuffers, using a physical model of the pulse: two exhaust resonances and a
noise transient under an exponential decay, laid down at the firing interval
with a fixed per cylinder timing and amplitude irregularity so it has character
and still loops seamlessly.

Two buffers, crossfaded by throttle: one on load, longer ringing and dirtier,
one off load, drier and quieter. Both play looped through the same filter and
soft clipper, with playbackRate driven by rpm. Five cylinders, because the five
cylinder rally warble is the most characterful engine note there is.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- build the samples
sub("""    /* ---- engine ----
       A real exhaust is a pulse train, not a sawtooth. Build the harmonic
       series directly and let the filter decide how much of it you hear. */
    var NH=14, real=new Float32Array(NH), imag=new Float32Array(NH);
    var H=[0,1,0.64,0.44,0.31,0.23,0.17,0.13,0.10,0.075,0.058,0.045,0.034,0.026];
    for(var i=1;i<NH;i++) imag[i]=H[i];
    var wave=ctx.createPeriodicWave(real,imag);

    var o1=ctx.createOscillator(); o1.setPeriodicWave(wave);
    var o2=ctx.createOscillator(); o2.setPeriodicWave(wave); o2.detune.value=-11;
    var sub=ctx.createOscillator(); sub.type='sine';
    var sub2=ctx.createOscillator(); sub2.type='triangle';   /* an octave lower again */
    var turbo=ctx.createOscillator(); turbo.type='sine';""",
"""    /* ---- engine ----
       Bake a looping exhaust note. CYL firings per two revolutions, laid down
       at the firing interval, each one a pair of pipe resonances plus a noise
       transient under an exponential decay. Per cylinder timing and level
       irregularity is fixed rather than random, so the loop still joins. */
    var CYL=5, REF_RPM=3000;
    var firesPerSec=REF_RPM/60*CYL/2;              /* 125 a second at the reference */
    var EVENTS=CYL*25;                             /* a whole number of firing cycles */
    function bakeEngine(o){
      var dur=EVENTS/firesPerSec;
      var len=Math.floor(dur*ctx.sampleRate);
      var b=ctx.createBuffer(1,len,ctx.sampleRate), d=b.getChannelData(0);
      var sr=ctx.sampleRate, plen=Math.floor(sr*0.09);
      for(var e=0;e<EVENTS;e++){
        var cy=e%CYL;
        /* fixed unevenness: this is the warble */
        var skew=Math.sin(cy*2.399)*o.uneven;
        var amp=o.amp*(1+Math.sin(cy*1.117)*o.ampVar);
        var t0=Math.floor(((e+skew)/firesPerSec)*sr);
        for(var i=0;i<plen;i++){
          var tt=i/sr;
          var env=Math.exp(-tt*o.decay);
          var v=Math.sin(6.28318*o.f1*tt)*0.55
               +Math.sin(6.28318*o.f2*tt+0.7)*0.30
               +Math.sin(6.28318*o.f1*0.5*tt+1.4)*0.22;
          v+=(Math.random()*2-1)*o.noise*Math.exp(-tt*o.decay*3.2);
          var idx=(t0+i)%len; if(idx<0) idx+=len;
          d[idx]+=v*env*amp;
        }
      }
      /* normalise so the two buffers sit at the same level */
      var mx=0; for(var k=0;k<len;k++) if(Math.abs(d[k])>mx) mx=Math.abs(d[k]);
      if(mx>0) for(var k2=0;k2<len;k2++) d[k2]/=mx;
      return b;
    }
    var bufOn =bakeEngine({f1:112,f2:171,decay:52,noise:0.50,amp:1.0,uneven:0.055,ampVar:0.16});
    var bufOff=bakeEngine({f1:118,f2:181,decay:104,noise:0.26,amp:0.7,uneven:0.040,ampVar:0.10});

    var srcOn=ctx.createBufferSource(); srcOn.buffer=bufOn; srcOn.loop=true;
    var srcOff=ctx.createBufferSource(); srcOff.buffer=bufOff; srcOff.loop=true;
    var gOn=ctx.createGain(); gOn.gain.value=0;
    var gOff=ctx.createGain(); gOff.gain.value=0;

    var sub=ctx.createOscillator(); sub.type='sine';
    var sub2=ctx.createOscillator(); sub2.type='triangle';   /* an octave lower again */
    var turbo=ctx.createOscillator(); turbo.type='sine';""")

sub("""    var sub2g=ctx.createGain(); sub2g.gain.value=0.0;
    var turbog=ctx.createGain(); turbog.gain.value=0.0;

    o1.connect(drive); o2.connect(drive);
    drive.connect(lp); lp.connect(shaper); shaper.connect(eg); eg.connect(comp);
    sub.connect(subg); subg.connect(comp);
    sub2.connect(sub2g); sub2g.connect(comp);
    turbo.connect(turbog); turbog.connect(comp);
    o1.start(); o2.start(); sub.start(); sub2.start(); turbo.start();""",
"""    var sub2g=ctx.createGain(); sub2g.gain.value=0.0;
    var turbog=ctx.createGain(); turbog.gain.value=0.0;

    srcOn.connect(gOn); gOn.connect(drive);
    srcOff.connect(gOff); gOff.connect(drive);
    drive.connect(lp); lp.connect(shaper); shaper.connect(eg); eg.connect(comp);
    sub.connect(subg); subg.connect(comp);
    sub2.connect(sub2g); sub2g.connect(comp);
    turbo.connect(turbog); turbog.connect(comp);
    srcOn.start(); srcOff.start(); sub.start(); sub2.start(); turbo.start();""")

sub("""    A={ctx:ctx, comp:comp, master:master, buf:buf,
       o1:o1, o2:o2, sub:sub, sub2:sub2, turbo:turbo, lp:lp, drive:drive,
       eg:eg, subg:subg, sub2g:sub2g, turbog:turbog,""",
"""    A={ctx:ctx, comp:comp, master:master, buf:buf, REF_RPM:REF_RPM,
       srcOn:srcOn, srcOff:srcOff, gOn:gOn, gOff:gOff,
       sub:sub, sub2:sub2, turbo:turbo, lp:lp, drive:drive,
       eg:eg, subg:subg, sub2g:sub2g, turbog:turbog,""")

# ---------------------------------------------------------------- drive it
sub("""  /* Two and a half pulses a rev rather than four. Lower fundamental, more
     weight, less buzz. */
  var f0=Math.max(10,S.rpm/60*2.5);
  A.o1.frequency.setTargetAtTime(f0,t,0.02);
  A.o2.frequency.setTargetAtTime(f0*1.004,t,0.02);
  A.sub.frequency.setTargetAtTime(f0*0.5,t,0.03);
  A.sub2.frequency.setTargetAtTime(f0*0.25,t,0.04);""",
"""  /* Pitch the baked loops by revs. This is the whole engine. */
  var rate=Math.max(0.16,S.rpm/A.REF_RPM);
  A.srcOn.playbackRate.setTargetAtTime(rate,t,0.028);
  A.srcOff.playbackRate.setTargetAtTime(rate*0.998,t,0.028);

  /* crossfade on load against off load */
  var lf=Math.min(1,Math.max(0,S.throttle*1.25));
  A.gOn.gain.setTargetAtTime((S.crank>0?0.10:0.55)*lf+0.06,t,0.05);
  A.gOff.gain.setTargetAtTime(0.42*(1-lf)+0.05,t,0.06);

  /* the firing fundamental, for the sub octaves underneath */
  var f0=Math.max(10,S.rpm/60*2.5);
  A.sub.frequency.setTargetAtTime(f0*0.5,t,0.03);
  A.sub2.frequency.setTargetAtTime(f0*0.25,t,0.04);""")

sub("""  var want=(S.crank>0?0.026:0.042)+load*0.070+(S.grounded===0?0.012:0);""",
    """  var want=(S.crank>0?0.030:0.060)+load*0.085+(S.grounded===0?0.014:0);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
