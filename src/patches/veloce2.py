# -*- coding: utf-8 -*-
"""Why the Veloce dives into the scenery, and the four wheel drive you asked for.

TWO BUGS, BOTH MINE.

1. DOWNFORCE WAS APPLIED IN THE AIR. There is no ground test on it at all. At
   60 m/s the Veloce made about 9.4 kN along its own down axis with all four
   wheels off the ground, which is three quarters of its weight of extra
   gravity, aimed wherever the nose happened to be pointing. Pitch the nose
   down on a jump and that vector points down AND forward, so the car is thrown
   at the ground nose first and buries itself. That is exactly what you
   described and it got worse every time you asked for more downforce.

   Downforce now scales with how many wheels are actually on the ground.

2. IT LIVED ON THE BUMP STOPS. I raised its spring rate to 40,000 N/m and cut
   its bump travel to 0.14 m to stop it bottoming under aero. At rest it then
   sat with about 8 cm of stroke left, and the bump stop is deliberately
   springy: BS_K2 is 1.9 million and it returns 55 percent of what it absorbs,
   because that is what launches you off a landing. So every small bump hit the
   stop and got a relaunch. Softer springs, more travel, and the aero no longer
   needs the stiffness because of the change below.

THE CHEAT THAT MAKES MORE DOWNFORCE POSSIBLE. Downforce did two jobs: it
pressed the tyres (grip) and it squashed the springs (which is what bottoms the
car on rough ground). Only the first one is what you want from it. It now puts
its full value into the tyre load and only 30 percent of it into the chassis,
so you get the grip of a huge wing without the car being crushed onto its
bumpstops on a Shield trail. It is not physical; it is the right trade for a
game where the fast car has to survive a bad landing.

AND THE REST OF WHAT YOU ASKED FOR: four wheel drive, an even split; drive up
from 34,000 to 52,000 N with the ceiling raised to match; downforce from 2.6 to
4.4, which is about 1.8 times its own weight flat out.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- 1. downforce only where there are wheels on the ground
sub("""  S.dfF=0; S.dfR=0;
  if(AERO>0){
    _bup.set(0,1,0).applyQuaternion(S.q);
    var vFwd=Math.abs(S.v.dot(_bfwd0.set(0,0,1).applyQuaternion(S.q)));
    var dfTot=AERO*vFwd*vFwd;
    S.dfF=dfTot*AERO_F; S.dfR=dfTot*(1-AERO_F);
    Fsum.addScaledVector(_bup,-dfTot);
    /* the pitching moment from putting it on the axles, not the middle */
    _tmp.set(0,0,1).applyQuaternion(S.q);
    Tsum.addScaledVector(_tmp.cross(_bup), (S.dfF-S.dfR)*WHEELBASE*0.5*0.0);
  }""",
"""  S.dfF=0; S.dfR=0;
  if(AERO>0){
    _bup.set(0,1,0).applyQuaternion(S.q);
    var vFwd=Math.abs(S.v.dot(_bfwd0.set(0,0,1).applyQuaternion(S.q)));
    /* Wheels on the ground, from last step. Downforce with all four in the air
       is three quarters of a g aimed wherever the nose is pointing, which
       threw the car at the ground nose first on every jump. */
    var gAir=Math.min(1,(S.grounded||0)/3);
    var dfTot=AERO*vFwd*vFwd*gAir;
    S.dfF=dfTot*AERO_F; S.dfR=dfTot*(1-AERO_F);
    /* Full value into the tyre load below, but only a fraction into the
       chassis. Pressing the tyres is the point of downforce; squashing the
       springs is the part that bottoms the car out on rough ground, and this
       car has to survive a Shield trail at 250. */
    Fsum.addScaledVector(_bup,-dfTot*AERO_BODY);
  }""")

sub("var AERO=0, AERO_F=0.42;   /* newtons per (m/s)^2, and the front share */",
    "var AERO=0, AERO_F=0.42;   /* newtons per (m/s)^2, and the front share */\n"
    "var AERO_BODY=0.30;        /* how much of it the springs have to carry */")

# ---- 2. a car that can take a bump again, and the rest of the brief
sub("    rest:0.40, susMax:0.62, susMin:0.14, k:40000, dBump:3800, dReb:4600,",
    "    rest:0.42, susMax:0.74, susMin:0.20, k:26000, dBump:2950, dReb:3600,")
sub("arbF:12600, arbR:8400, drive:34000, brake:33000, biasF:0.56, vmax:84, cd:0.21,",
    "arbF:9200, arbR:7400, drive:52000, brake:34000, biasF:0.54, vmax:92, cd:0.20,")
sub("    dF:0.44, dR:0.56, muF:1.16, muR:1.20,",
    "    dF:0.50, dR:0.50, muF:1.16, muR:1.20,")   # four wheel drive, even split
sub("    aero:2.60, aeroF:0.44,", "    aero:4.40, aeroF:0.40,")

# the bars have to keep up again
sub("pct(V.drive,20000,34500)", "pct(V.drive,20000,53000)")
sub("pct(V.vmax||52,44,86)",    "pct(V.vmax||52,44,94)")
sub("pct(V.aero||0,0,2.8)",     "pct(V.aero||0,0,4.6)")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
