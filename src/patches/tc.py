# -*- coding: utf-8 -*-
"""Traction control, so unlimited torque is usable instead of destructive.

Averaged over five different start points instead of one (single runs diverge
over the terrain and are not comparable, which sent me chasing the springs for
three rounds), the cause was unambiguous:

  Veloce as built        air 40%  31 flights  worst rise 27.1 m  nose 67 deg
  with aero switched off air 17%  16 flights            15.7 m       39 deg
  with drive x 0.4       air  4%   9 flights             0.4 m       42 deg
  with softer springs    air 32%  21 flights            19.1 m       70 deg
  Bracken, for reference air  3%   7 flights             1.8 m       19 deg

The torque was doing it, not the suspension. And the reason is that the
friction ellipse scales Flong and Flat DOWN TOGETHER when a tyre is over its
limit. Demand 52 kN through a patch that can take 5 and the tyre spends every
frame saturated, which costs all of its lateral grip at the same time, so the
car skitters, the front unloads and it launches off the next rise.

Making the engine smaller is not the answer, because you asked for the
opposite. So the cars that have more torque than tyre now get what a real four
wheel drive hypercar has: the drive demand is capped at what THAT contact patch
can take, computed before the ellipse, so the full 52 kN is deployed exactly to
the limit of grip and never past it. Because the cap includes the downforce
term, the faster it goes the more of its engine it can use, which is the
fantasy you were asking for in the first place.

Off by default; only the Veloce has it. The other four keep their wheelspin,
because lighting the rears up is most of the character of a rally raid truck.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("var AERO_BODY=0.30;        /* how much of it the springs have to carry */",
    "var AERO_BODY=0.30;        /* how much of it the springs have to carry */\n"
    "var TRACTION=0;            /* 0 is off; otherwise the share of grip drive may use */")

sub("    AERO=V.aero||0; AERO_F=(V.aeroF===undefined?0.42:V.aeroF);",
    "    AERO=V.aero||0; AERO_F=(V.aeroF===undefined?0.42:V.aeroF);\n"
    "    TRACTION=V.tc||0;")

sub("""    var share=c2.front? DRIVE_F/Math.max(1,nF) : DRIVE_R/Math.max(1,nR);
    Flong += (S.throttle-S.rev*0.55)*MAX_DRIVE*driveCurve*share;""",
"""    var share=c2.front? DRIVE_F/Math.max(1,nF) : DRIVE_R/Math.max(1,nR);
    var drv=(S.throttle-S.rev*0.55)*MAX_DRIVE*driveCurve*share;
    /* Cap the demand at what this patch can take, before the ellipse gets to
       scale the lateral force down with it. Without this a very large engine
       costs you all of your cornering grip and throws the car off every rise. */
    if(TRACTION>0){
      var cap=TRACTION*MU_LONG_MULT*muL*D*(c2.load + (c2.front? S.dfF*0.5 : S.dfR*0.5));
      if(drv>cap) drv=cap; else if(drv<-cap) drv=-cap;
    }
    Flong += drv;""")

# the one car that has more engine than tyre
sub("    dF:0.50, dR:0.50, muF:1.16, muR:1.20,",
    "    dF:0.50, dR:0.50, tc:0.96, muF:1.16, muR:1.20,")
# and a little less wheelie out of the longitudinal couple
sub("hRoll:0.34, hPitch:0.74, rb:0.54,", "hRoll:0.34, hPitch:0.60, rb:0.54,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
