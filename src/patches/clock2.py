# -*- coding: utf-8 -*-
"""The real reason time ran away: two branches fighting, and the fast one won.

    if(TOD.k<1){ TOD.k=Math.min(1,TOD.k+dt*0.55); applyTime(TOD.k); }
    else if(TOD.drift){ TOD.k+=dt*RATE; ... }

The first branch is the animation for a manual time change: press the button
and the light slides to the next setting over about two seconds. The second is
the clock. But the first is tested FIRST, and it is true whenever k<1 - which
is exactly when the clock is mid stage. So with the clock on, the drift branch
never ran except for the single frame where k reached 1; it advanced the stage,
reset k to 0, and the two second animation immediately took over again.

Every time of day therefore lasted about 1.8 seconds and a full day took nine.
The 0.0055 rate I have been carefully retuning was never controlling anything.

The two are now separate states: `TOD.jump` is set only by the button and only
it runs the fast slide. The clock runs its own rate to completion.

I also could not test any of this, because the clock lives in `frame()`, which
is driven by requestAnimationFrame, and the headless harness only ever ran
`step` and the per frame layer. That is the same class of gap as the `fa` bug.
The clock is now a named function that both the real loop and `tick` call, so
it is measurable.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("""  if(TOD.k<1){ TOD.k=Math.min(1,TOD.k+dt*0.55); applyTime(TOD.k); }
  else if(TOD.drift){
    /* divided by the dwell of the time we are leaving, so the clock hurries
       through flat morning light and takes its time over golden and dusk */
    TOD.k+=dt*CLOCK_RATE[TOD.drift]/(TIMES[TOD.from].dwell||1);
    if(TOD.k>=1){ TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; }
    applyTime(TOD.k);
  }
  sync(dt);""",
"""  stepClock(dt);
  sync(dt);""")

sub("""/* ================= grade ================= */""",
"""/* Two separate things that were sharing one test, which is why every time of
   day lasted under two seconds. `jump` is the slide after you press the button;
   `drift` is the clock. Only one of them may ever be moving k. */
function stepClock(dt){
  if(TOD.jump){
    TOD.k=Math.min(1,TOD.k+dt*0.55);
    if(TOD.k>=1) TOD.jump=false;
    applyTime(TOD.k);
  }
  else if(TOD.drift){
    /* divided by the dwell of the time we are leaving, so the clock hurries
       through flat morning light and takes its time over golden and dusk */
    TOD.k+=dt*CLOCK_RATE[TOD.drift]/(TIMES[TOD.from].dwell||1);
    if(TOD.k>=1){ TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; }
    applyTime(TOD.k);
  }
}

/* ================= grade ================= */""")

sub("var TOD={ i:2, from:2, to:2, k:1, drift:0, glow:0.12, night:0 };",
    "var TOD={ i:2, from:2, to:2, k:1, drift:0, jump:false, glow:0.12, night:0 };")

# the button is the only thing that starts a slide
sub("""  TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0;
  this.textContent='Time of day: '+TIMES[TOD.to].name;""",
"""  TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; TOD.jump=true;
  this.textContent='Time of day: '+TIMES[TOD.to].name;""")

# and the harness runs the clock, so it can be measured
sub("        t+=dt; window.__fa+=dt;",
    "        t+=dt; window.__fa+=dt; stepClock(dt);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
