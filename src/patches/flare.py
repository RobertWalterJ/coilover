# -*- coding: utf-8 -*-
"""Arches that are part of the body, and a Veloce that is pressed down harder.

THE ARCHES WERE FLOATING. A torus centred on the wheel cannot be placed from
the body's coordinates: the wheel hangs off a strut whose length changes with
the suspension, so the ring sat wherever the spring happened to leave it and
read as a hoop standing beside the car. It was also inboard of the tyre, which
is why it looked offset.

Bodies do not have hoops over their wheels, they have flares, so the flare is
now part of the hull: extra stations in the loft at each axle, wider than the
rest of the body, with the section squared off a little so the arch has a lip.
It cannot float because it is the same surface as the flank, and it covers the
tyre, which the old body did not (each wheel stood 15 to 30 cm proud).

MORE DOWNFORCE AND MORE SPEED, and the springs to survive it. Downforce is
limited by bump travel, not by taste: at rest each corner sits 0.116 m into a
0.43 m stroke on a 27,600 N/m spring, which leaves 0.094 m before it bottoms,
so the whole car could only take 10,376 N of aero before dragging its floor.
That is the real ceiling and it is why the earlier attempts made it slower.

Springs to 38,000 N/m with the damping raised to match, which is stiff even for
a GT and is exactly why real downforce cars run stiff. Bump budget goes to
19,076 N. Aero to 2.6, which at its new terminal speed makes about 14,200 N:
more than the car weighs, and still inside the springs. Ceiling to 84 m/s, drag
down to 0.21 and drive to 34,000, which works out around 266 km/h on sand and
281 on asphalt.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ============================================ 1. Veloce: aero, springs, speed
sub("    rest:0.40, susMax:0.62, susMin:0.19, k:27600, dBump:2880, dReb:3520,",
    "    rest:0.40, susMax:0.62, susMin:0.19, k:38000, dBump:3600, dReb:4400,")
sub("arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.56, vmax:72, cd:0.25,",
    "arbF:12600, arbR:8400, drive:34000, brake:33000, biasF:0.56, vmax:84, cd:0.21,")
sub("    aero:1.70, aeroF:0.44,", "    aero:2.60, aeroF:0.44,")

# the bars have to keep up with the numbers
sub("pct(V.drive,20000,32000)", "pct(V.drive,20000,34500)")
sub("pct(V.vmax||52,44,74)",    "pct(V.vmax||52,44,86)")
sub("pct(V.aero||0,0,1.8)",     "pct(V.aero||0,0,2.8)")

# ============================================== 2. Veloce: flares in the hull
sub("""      {z: 1.44, w:hw*0.94, y: 0.00, up:0.24, dn:0.19, n:3.4},
      {z: 0.86, w:hw*0.99, y: 0.03, up:0.28, dn:0.22, n:3.8},
      {z: 0.10, w:hw*1.00, y: 0.04, up:0.30, dn:0.24, n:4.2},
      {z:-0.72, w:hw*1.00, y: 0.06, up:0.32, dn:0.24, n:4.4},
      {z:-1.42, w:hw*0.98, y: 0.05, up:0.30, dn:0.22, n:4.0},""",
"""      {z: 1.72, w:hw*1.14, y: 0.00, up:0.25, dn:0.20, n:4.6},   /* front flare */
      {z: 1.44, w:hw*1.24, y: 0.00, up:0.26, dn:0.20, n:5.0},
      {z: 1.18, w:hw*1.14, y: 0.01, up:0.26, dn:0.21, n:4.6},
      {z: 0.86, w:hw*0.99, y: 0.03, up:0.28, dn:0.22, n:3.8},
      {z: 0.10, w:hw*1.00, y: 0.04, up:0.30, dn:0.24, n:4.2},
      {z:-0.72, w:hw*1.02, y: 0.06, up:0.32, dn:0.24, n:4.4},
      {z:-1.20, w:hw*1.16, y: 0.05, up:0.32, dn:0.23, n:4.8},   /* rear flare */
      {z:-1.48, w:hw*1.24, y: 0.05, up:0.31, dn:0.22, n:5.0},
      {z:-1.72, w:hw*1.12, y: 0.04, up:0.29, dn:0.21, n:4.6},""")

sub("""    var ay=V.wheelR*0.30-V.bodyY-0.30;
    [[1.42],[-1.44]].forEach(function(a){
      archT(flare, -hw*0.90, ay, a[0], V.wheelR*1.04, 0.055);
      archT(flare,  hw*0.90, ay, a[0], V.wheelR*1.04, 0.055);
    });""",
"""    /* the arch lip is a station in the hull above, not a hoop beside it */""")

# ============================================ 3. Marisol: flares in the hull
sub("""      {z: 1.50, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},
      {z: 0.88, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},""",
"""      {z: 1.94, w:hw*1.10, y: 0.52, up:0.64, dn:0.62, n:6.4},   /* front flare */
      {z: 1.70, w:hw*1.17, y: 0.52, up:0.64, dn:0.60, n:6.6},
      {z: 1.44, w:hw*1.08, y: 0.53, up:0.65, dn:0.62, n:6.4},
      {z: 0.88, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},""")
sub("""      {z:-1.16, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-2.02, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},""",
"""      {z:-1.28, w:hw*1.08, y: 0.48, up:0.56, dn:0.58, n:6.4},   /* rear flare */
      {z:-1.54, w:hw*1.17, y: 0.48, up:0.56, dn:0.56, n:6.6},
      {z:-1.80, w:hw*1.08, y: 0.48, up:0.56, dn:0.58, n:6.4},
      {z:-2.02, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},""")
sub("""    var ay=V.wheelR*0.22-V.bodyY-0.30;
    [[1.70],[-1.54]].forEach(function(a){
      archT(paint, -hw*0.84, ay, a[0], V.wheelR*1.06, 0.13);
      archT(paint,  hw*0.84, ay, a[0], V.wheelR*1.06, 0.13);
    });""",
"""    /* the arches are stations in the hull above, so they cannot float away */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
