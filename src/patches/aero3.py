# -*- coding: utf-8 -*-
"""Straight line speed that is actually per-vehicle.

Every car shared one drive curve, cut off at 52 m/s, and one drag coefficient.
Near the top of the range the curve goes to zero for everybody at the same
speed, so the Veloce's 31,500 N of drive against the Bracken's 22,000 bought it
two km/h: 145 against 143. Torque decides how fast you GET there; the cutoff
and the drag decide where you STOP. Both are now per vehicle, so the low sleek
one runs away from the trucks on anything open, which is the whole point of it.

It also drove 70 percent of its torque through the rear axle, which is how you
build a car that lights the back up under power. Moved forward.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# a per-vehicle speed ceiling and a per-vehicle drag
sub("var GRIP_F=1.0, GRIP_R=1.0;",
    "var GRIP_F=1.0, GRIP_R=1.0;\n"
    "/* Where the drive tails off, and how hard the air pushes back. Shared\n"
    "   constants here meant a car could only ever be quicker off the line, not\n"
    "   faster down a straight. */\n"
    "var DRIVE_VMAX=52, DRAG_C=0.357;")

sub("    GRIP_F=V.muF/1.00; GRIP_R=V.muR/0.92;",
    "    GRIP_F=V.muF/1.00; GRIP_R=V.muR/0.92;\n"
    "    DRIVE_VMAX=V.vmax||52; DRAG_C=(V.cd===undefined?0.357:V.cd);")

sub("  var driveCurve=Math.max(0,1-Math.pow(speed/52,1.6));",
    "  var driveCurve=Math.max(0,1-Math.pow(speed/DRIVE_VMAX,1.6));")

sub("  Fsum.addScaledVector(S.v,-1.05*speed*0.34);",
    "  Fsum.addScaledVector(S.v,-DRAG_C*speed);")

# a slab sided truck pushes a lot of air; a low wedge does not
sub("arbF:4100, arbR:6640, drive:22000, brake:25000, biasF:0.62,",
    "arbF:4100, arbR:6640, drive:22000, brake:25000, biasF:0.62, vmax:48, cd:0.44,")
sub("arbF:3200, arbR:5200, drive:27500, brake:26500, biasF:0.58,",
    "arbF:3200, arbR:5200, drive:27500, brake:26500, biasF:0.58, vmax:53, cd:0.42,")
sub("arbF:5400, arbR:7600, drive:25000, brake:27000, biasF:0.66,",
    "arbF:5400, arbR:7600, drive:25000, brake:27000, biasF:0.66, vmax:55, cd:0.33,")
sub("arbF:6200, arbR:8400, drive:29500, brake:28500, biasF:0.64,",
    "arbF:6200, arbR:8400, drive:29500, brake:28500, biasF:0.64, vmax:59, cd:0.31,")
sub("arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.62,",
    "arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.62, vmax:72, cd:0.25,")

# and stop driving it mostly through the back axle
sub("    dF:0.30, dR:0.70, muF:1.16, muR:1.20,",
    "    dF:0.44, dR:0.56, muF:1.16, muR:1.20,")

# the garage should show top speed, since it is now a real per-vehicle number
sub("""      <div><span>Power</span><i><b id="g-pow"></b></i></div>""",
    """      <div><span>Power</span><i><b id="g-pow"></b></i></div>
      <div><span>Top speed</span><i><b id="g-vmax"></b></i></div>""")
sub("""  document.getElementById('g-pow').style.width =pct(V.drive,20000,32000);""",
    """  document.getElementById('g-pow').style.width =pct(V.drive,20000,32000);
  var vm=document.getElementById('g-vmax');
  if(vm) vm.style.width=pct(V.vmax||52,44,74);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
