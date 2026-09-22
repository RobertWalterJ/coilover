# -*- coding: utf-8 -*-
"""Snappier. The gravity was the problem, and it was literally the problem.

Everything was tuned around 9.81, which is correct and which is exactly why it
felt floaty. Real gravity gives long hang times, lazy landings and an
acceleration ceiling set by how hard a tyre can push at one g. Arcade driving
games routinely run 1.4 to 2 times g for precisely this reason: jumps get
punchy, the car plants, and the grip limit rises so it can actually accelerate.

Gravity goes to 15.5, and every load bearing number scales with it or the truck
would sit on its bump stops. Spring rate scales linearly, damping by the square
root, bump stops and anti roll bars linearly. Ride height and travel are
unchanged, so it looks the same and behaves completely differently.

Then drive and brake go up to match the higher grip ceiling, the steering rack
gets quicker and keeps more lock at speed, and the camera field of view opens
further with speed so the sense of speed matches the actual speed.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("var G=9.81;",
    """/* 1.58 times real gravity. Everything below that carries load is scaled to
   match, so the ride height and the travel are unchanged. */
var G=15.5;""")

sub("""var SPRING_K=10400;                               /* N/m, static sits near 0.62 */
var DAMP_BUMP=1500, DAMP_REB=1900;                /* rebound was packing over whoops */
var DAMP_KNEE=1.8, DAMP_CLAMP=7500;               /* digressive blowoff, like a bypass */
var ARB_F=2600, ARB_R=4200;                       /* low, and rear biased, so it rolls */
var BS_ZONE=0.12, BS_K1=120000, BS_K2=1.2e6, BS_DAMP=4500, BS_REST=0.55;""",
"""var SPRING_K=16400;                               /* N/m, static still sits near 0.62 */
var DAMP_BUMP=1885, DAMP_REB=2390;                /* scaled by the square root of g */
var DAMP_KNEE=1.8, DAMP_CLAMP=11800;              /* digressive blowoff, like a bypass */
var ARB_F=4100, ARB_R=6640;                       /* low, and rear biased, so it rolls */
var BS_ZONE=0.12, BS_K1=190000, BS_K2=1.9e6, BS_DAMP=5660, BS_REST=0.55;""")

sub("if(Fs<0) Fs=0; if(Fs>41000) Fs=41000;", "if(Fs<0) Fs=0; if(Fs>65000) Fs=65000;")
sub("var FZ_REF=3433, RELAX=0.55;",
    "var FZ_REF=5425, RELAX=0.40;                      /* shorter relaxation, quicker turn in */")

# more push, more stop. The grip ceiling went up with gravity, so use it.
sub("var MAX_DRIVE=15000, MAX_BRAKE=16000, BRAKE_BIAS_F=0.62;",
    "var MAX_DRIVE=22000, MAX_BRAKE=25000, BRAKE_BIAS_F=0.62;")
sub("var driveCurve=Math.max(0,1-Math.pow(speed/44,1.6));",
    "var driveCurve=Math.max(0,1-Math.pow(speed/52,1.6));")

# quicker rack, and keep more lock at speed so it still turns when it is moving
sub("""  var dmax=0.15 + 0.50/(1+Math.pow(speed/9.5,1.6)) + Math.min(0.28,Math.abs(beta));""",
    """  var dmax=0.17 + 0.56/(1+Math.pow(speed/11.0,1.6)) + Math.min(0.30,Math.abs(beta));""")
sub("""  var steerAng=-S.steer*(0.15+0.50/(1+Math.pow(speed/9.5,1.6))+Math.min(0.28,Math.abs(beta2)));""",
    """  var steerAng=-S.steer*(0.17+0.56/(1+Math.pow(speed/11.0,1.6))+Math.min(0.30,Math.abs(beta2)));""")
sub("  S.steer += (s-S.steer)*Math.min(1,dt*17);",
    "  S.steer += (s-S.steer)*Math.min(1,dt*24);")
sub("  S.throttle += (g-S.throttle)*Math.min(1,dt*13);",
    "  S.throttle += (g-S.throttle)*Math.min(1,dt*18);")

# air authority scales with the shorter flights
sub("    Tsum.addScaledVector(_ra, angE*11000*auth);\n    Tsum.addScaledVector(_wWorld, -2400*auth);",
    "    Tsum.addScaledVector(_ra, angE*15000*auth);\n    Tsum.addScaledVector(_wWorld, -3100*auth);")
sub("    var auth=0.30+0.70*Math.max(0,1-tImp/1.20);",
    "    var auth=0.34+0.66*Math.max(0,1-tImp/0.95);")

# the sense of speed has to match the speed
sub("    camera.fov=56+PB()+Math.min(14,speed*0.40);",
    "    camera.fov=54+PB()+Math.min(21,speed*0.55);")
sub("    camera.fov=66+PB()+Math.min(14,speed*0.40);",
    "    camera.fov=64+PB()+Math.min(18,speed*0.50);")

# The rollover catch window was lost when the air control rewrite replaced
# everything between the air block and the integrator. Restore it, scaled.
sub("""    /* steering still yaws, and yaw never ruins a landing */
    Tsum.addScaledVector(_bup,S.steer*3000);
  }
""",
"""    /* steering still yaws, and yaw never ruins a landing */
    Tsum.addScaledVector(_bup,S.steer*3000);
  }

  /* Rollovers should be survivable stories, not instant losses. Between 40 and
     75 degrees of lean, damp the roll hard so a tip stretches out to about a
     second, and let steering shove back against it. */
  var lean=Math.acos(Math.max(-1,Math.min(1,_bup.y)));
  if(lean>0.70 && lean<1.31){
    var rollRate=_wWorld.dot(_bfwd);
    Tsum.addScaledVector(_bfwd,-rollRate*9200 - S.steer*3600);
  }
  if(lean>0.96){
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,3900*Math.min(1,(lean-0.96)/0.44));
  }
""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
