# -*- coding: utf-8 -*-
"""Analogue pedals, your way.

Press either ring and you get a middle amount, which is the useful default.
Then hold and slide: up on the throttle for more, down on the brake for more,
which is the pedal metaphor the right way round. Release and it lets go. The
ring fills as you push, so you can see how much foot you have in it without
looking away from the truck.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("""    if(kind==='gas'){ IN.gas=1; t0y=e.clientY; gasEl.classList.add('on'); }
    if(kind==='brake'){ IN.brake=1; IN.revHold=0; brakeEl.classList.add('on'); }""",
"""    /* a press gives you the middle of the pedal, not all of it */
    if(kind==='gas'){ IN.gas=0.60; gasEl.classList.add('on'); pedalFill(gasEl,0.60); }
    if(kind==='brake'){ IN.brake=0.50; IN.revHold=0; brakeEl.classList.add('on'); pedalFill(brakeEl,0.50); }""")

sub("""    if(t && t.kind==='gas'){
      /* Press for full, slide down to feather. Weight transfer is the whole
         pleasure of this truck and a binary button hid all of it. */
      IN.gas=Math.max(0.12,Math.min(1,1-(e.clientY-t.oy)/95));
      return;
    }""",
"""    if(t && t.kind==='gas'){
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
    }""")

sub("""    if(t.kind==='gas'){ IN.gas=0; gasEl.classList.remove('on'); }
    if(t.kind==='brake'){ IN.brake=0; IN.revHold=0; brakeEl.classList.remove('on'); }""",
"""    if(t.kind==='gas'){ IN.gas=0; gasEl.classList.remove('on'); pedalFill(gasEl,0); }
    if(t.kind==='brake'){ IN.brake=0; IN.revHold=0; brakeEl.classList.remove('on'); pedalFill(brakeEl,0); }""")

sub("""var _buzzT=0;""",
"""/* the ring fills as you push, so pedal pressure is visible without looking */
function pedalFill(el,v){
  el.style.background = v>0
    ? 'rgba(244,235,221,'+(0.05+0.26*v).toFixed(3)+')'
    : '';
}

var _buzzT=0;""")

# a light brake should not throw the back out as hard as a hard one
sub("""    if(sp>6.9 && lock>0.34) h=Math.min(1,(lock-0.34)/0.34);""",
    """    if(sp>6.9 && lock>0.34) h=Math.min(1,(lock-0.34)/0.34)*Math.min(1,b*1.3);""")

sub("""    active.clear(); IN.gas=IN.brake=IN.steer=IN.hand=0; IN.revHold=0;
    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');""",
"""    active.clear(); IN.gas=IN.brake=IN.steer=IN.hand=0; IN.revHold=0;
    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    pedalFill(gasEl,0); pedalFill(brakeEl,0);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
