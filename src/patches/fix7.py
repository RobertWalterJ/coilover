# -*- coding: utf-8 -*-
"""The crackle, and the rollover.

THE CRACKLE. It has never fired once. The test compared this frame's throttle
against last frame's and wanted a fall from above 0.45 to below 0.20 in that
single step. But the throttle is smoothed at dt*18, which keeps 70 percent of
it per frame at sixty. So the pair could only ever satisfy the test below about
twenty two frames a second. Simulated across fifteen frame rates: zero fires
from 25 up to 144. Confirmed in the running game: lifting off at 120 km/h, zero
fires. The whole overrun system, the bang series and the dump valve chirp were
all unreachable, which is why the one sound you asked for most was not in the
game.

It now latches the highest throttle seen in the last third of a second and
compares the current load against that, so a lift is a lift regardless of frame
rate. Once it fires the latch is cleared so it does not machine gun.

THE ROLLOVER. The truck could not be tipped. Injecting roll rates from 2 to 20
radians a second all produced the same 42.9 degree maximum lean, because the
roll damper is a flat rate times 9200 that simply overwhelms anything. So the
righting branch was unreachable, the Upright button was dead UI, and you could
not fail a landing, which is most of the surprise in an off road game.

The damper now falls away as the truck leans. Upright it is as firm as it was,
so the handling is unchanged; past about thirty degrees it lets go, so a bad
landing can actually put you over and you have to right it.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# =================================================================== crackle
sub("""  var lifted=(S.prevThr>0.45 && load<0.20 && S.rpm>2000 && S.crank<=0);
  if(lifted) crackle(Math.min(1,(S.rpm-2000)/2600+0.45));
  S.prevThr=load;""",
"""  /* Latch the highest throttle of the last third of a second rather than
     comparing two adjacent smoothed frames, which could only ever satisfy the
     old test below about twenty two frames a second. */
  if(load>S.thrPeak) S.thrPeak=load;
  S.thrPeakT=(S.thrPeakT||0)+dt;
  if(S.thrPeakT>0.34){ S.thrPeak=load; S.thrPeakT=0; }
  var lifted=(S.thrPeak>0.45 && load<0.22 && S.rpm>2000 && S.crank<=0 && A.pop<=0);
  if(lifted){
    crackle(Math.min(1,(S.rpm-2000)/2600+0.45));
    S.thrPeak=load;                       /* so it fires once, not continuously */
    A.pop=0.42+Math.random()*0.24;
  }
  A.pop=(A.pop||0)-dt;
  S.prevThr=load;""")

sub("""  gearFrac:0, shifted:false, prevThr:0,""",
    """  gearFrac:0, shifted:false, prevThr:0, thrPeak:0, thrPeakT:0,""")

# ================================================================= rollover
sub("""    Tsum.addScaledVector(_bfwd,-rollRate*9200 - S.steer*3600);""",
"""    /* Firm while upright so the handling is unchanged, then letting go past
       about thirty degrees so a bad landing can genuinely put you over. */
    var rollGive=1.0-sstep(0.52,1.15,lean);
    Tsum.addScaledVector(_bfwd,(-rollRate*9200 - S.steer*3600)*(0.22+0.78*rollGive));""")

# and the righting assist should only help once you are properly over
sub("""  if(lean>0.96){
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,3900*Math.min(1,(lean-0.96)/0.44));""",
"""  if(lean>1.30){
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,2100*Math.min(1,(lean-1.30)/0.55));""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
