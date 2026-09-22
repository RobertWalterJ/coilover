# -*- coding: utf-8 -*-
"""A truck, not a teardrop.

The first rebuild made it one continuous mass, which fixed the tractor, but I
tapered the tail away and rounded the sections until it read as a 1930s
streamlined lorry. Two mistakes:

ROUND WAS THE WRONG INSTRUCTION HERE. "Smoother and rounder" was said about the
GT. A Dakar truck is rectangular with softened edges: the section wants to be
near square with a radius on it, not an egg. The squareness exponent goes from
about 5 up to 6.6, so the corners are radii on a box rather than an oval.

AND A TRUCK DOES NOT TAPER. The body was narrowing and dropping from halfway
back, which is what made the tail read as a speedster. The rear body now holds
its full section all the way to a near vertical back panel, with a short
chamfer at the very end, and there is a real step down behind the cab so the
cab reads as a cab and the body reads as a body.

The arches were grey hoops floating clear of the paint. They are body coloured
now, thicker, and pulled in against the flank so they read as flares.

The spares were buried inside the body: the deck top is at 0.86 and they were
centred at 0.94 with a 0.42 radius, so two thirds of each was inside the
bodywork. They stand on the deck now.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- the hull: square sections, no taper, a real step behind the cab
sub("""    loft([
      {z: 2.34, w:hw*0.86, y: 0.46, up:0.52, dn:0.56, n:4.6},
      {z: 2.16, w:hw*0.95, y: 0.48, up:0.60, dn:0.60, n:5.0},
      {z: 1.55, w:hw*1.00, y: 0.50, up:0.66, dn:0.62, n:5.4},
      {z: 0.72, w:hw*1.00, y: 0.50, up:0.66, dn:0.62, n:5.4},
      {z: 0.30, w:hw*0.97, y: 0.42, up:0.52, dn:0.58, n:5.0},
      {z:-0.55, w:hw*0.95, y: 0.38, up:0.46, dn:0.54, n:5.0},
      {z:-1.70, w:hw*0.95, y: 0.38, up:0.46, dn:0.52, n:5.0},
      {z:-2.24, w:hw*0.86, y: 0.34, up:0.40, dn:0.46, n:4.4},
      {z:-2.46, w:hw*0.66, y: 0.30, up:0.30, dn:0.36, n:3.4}
    ], paint);""",
"""    loft([
      {z: 2.44, w:hw*0.88, y: 0.50, up:0.54, dn:0.58, n:5.4},
      {z: 2.30, w:hw*0.97, y: 0.52, up:0.62, dn:0.62, n:6.2},
      {z: 1.50, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},
      {z: 0.88, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},
      {z: 0.62, w:hw*0.95, y: 0.44, up:0.44, dn:0.58, n:5.6},   /* the step */
      {z: 0.34, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-1.16, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-2.02, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-2.30, w:hw*0.92, y: 0.46, up:0.52, dn:0.56, n:5.8},
      {z:-2.42, w:hw*0.78, y: 0.44, up:0.44, dn:0.48, n:5.0}
    ], paint);""")

# ---- the glass follows the taller cab
sub("""    var scr=box(W*0.80,0.62,0.07, glass, 0, 0.86, 2.06, false);
    scr.rotation.x=-0.30;
    box(0.06,0.34,0.86, glass, -hw*0.96, 0.82, 1.42, false);
    box(0.06,0.34,0.86, glass,  hw*0.96, 0.82, 1.42, false);
    /* the cab roof, so the top of the cab is a panel and not the paint */
    box(W*0.90,0.09,1.46, second, 0, 1.16, 1.34, false);""",
"""    var scr=box(W*0.80,0.60,0.07, glass, 0, 0.96, 2.22, false);
    scr.rotation.x=-0.24;
    box(0.06,0.40,0.92, glass, -hw*0.97, 0.92, 1.56, false);
    box(0.06,0.40,0.92, glass,  hw*0.97, 0.92, 1.56, false);
    /* the cab roof, so the top of the cab is a panel and not the paint */
    box(W*0.92,0.09,1.44, second, 0, 1.21, 1.58, false);""")

# ---- the rack sits on the cab roof, which has moved
sub("    var rz0=1.94, rz1=0.72, ry=1.30;",
    "    var rz0=2.20, rz1=0.98, ry=1.36;")

# ---- spares stand on the deck instead of inside it
sub("""    [[-0.46],[0.46]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,0.26,12),tyreM);
      sw.rotation.x=Math.PI/2; add(sw,sp[0],0.94,-1.30);
    });
    box(W*0.86,0.07,0.07, trim, 0, 0.86,-0.62, false);
    box(W*0.86,0.07,0.07, trim, 0, 0.86,-1.98, false);
    box(0.07,0.07,1.42, trim, -hw*0.84, 0.86,-1.30, false);
    box(0.07,0.07,1.42, trim,  hw*0.84, 0.86,-1.30, false);""",
"""    /* the deck top is at 1.04, so a 0.40 spare stands at 1.44, not 0.94 */
    [[-0.50],[0.50]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.40,0.40,0.26,12),tyreM);
      sw.rotation.z=Math.PI/2; add(sw,sp[0],1.42,-1.16);
    });
    box(W*0.88,0.07,0.07, trim, 0, 1.06,-0.58, false);
    box(W*0.88,0.07,0.07, trim, 0, 1.06,-1.86, false);
    box(0.07,0.07,1.34, trim, -hw*0.86, 1.06,-1.22, false);
    box(0.07,0.07,1.34, trim,  hw*0.86, 1.06,-1.22, false);""")

# ---- arches read as flares, not hoops
sub("""    var ay=V.wheelR*0.28-V.bodyY-0.30;
    [[1.62],[-1.62]].forEach(function(a){
      archT(flare, -hw*0.90, ay, a[0], V.wheelR*1.16, 0.085);
      archT(flare,  hw*0.90, ay, a[0], V.wheelR*1.16, 0.085);
    });""",
"""    var ay=V.wheelR*0.22-V.bodyY-0.30;
    [[1.70],[-1.54]].forEach(function(a){
      archT(paint, -hw*0.84, ay, a[0], V.wheelR*1.06, 0.13);
      archT(paint,  hw*0.84, ay, a[0], V.wheelR*1.06, 0.13);
    });""")

# ---- and the snorkel/bull bar follow the taller front
sub("    box(0.14,0.86,0.14, trim, hw*0.90, 0.98, 1.94, false);\n"
    "    box(0.16,0.16,0.22, trim, hw*0.90, 1.44, 1.86, false);",
    "    box(0.14,0.92,0.14, trim, hw*0.94, 1.06, 2.02, false);\n"
    "    box(0.16,0.16,0.22, trim, hw*0.94, 1.56, 1.94, false);")
sub("    box(W*0.92,0.16,0.14, trim, 0, 0.30, 2.44, false);",
    "    box(W*0.92,0.16,0.14, trim, 0, 0.34, 2.52, false);")
sub("    box(0.12,0.52,0.12, trim, -hw*0.62, 0.08, 2.42, false);\n"
    "    box(0.12,0.52,0.12, trim,  hw*0.62, 0.08, 2.42, false);",
    "    box(0.12,0.56,0.12, trim, -hw*0.62, 0.10, 2.50, false);\n"
    "    box(0.12,0.56,0.12, trim,  hw*0.62, 0.10, 2.50, false);")
sub("    cyl(0.19,0.12,12, lampM, -hw*0.52,0.34,2.42, Math.PI/2);\n"
    "    cyl(0.19,0.12,12, lampM,  hw*0.52,0.34,2.42, Math.PI/2);",
    "    cyl(0.19,0.12,12, lampM, -hw*0.52,0.40,2.50, Math.PI/2);\n"
    "    cyl(0.19,0.12,12, lampM,  hw*0.52,0.40,2.50, Math.PI/2);")
sub("    box(W*0.82,0.11,0.07, tailM, 0, 0.44,-2.52, false);\n"
    "    box(0.30,0.22,0.10, trim, 0,-0.02,-2.50, false);",
    "    box(W*0.82,0.11,0.07, tailM, 0, 0.62,-2.48, false);\n"
    "    box(0.30,0.22,0.10, trim, 0,-0.02,-2.46, false);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
