# -*- coding: utf-8 -*-
"""The Bracken, lofted. Still a box, but a box with radii on it.

The last car still built out of stacked cubes: a sill, a bonnet, a cabin and a
rear body, four hard edged volumes with the seams showing. A utility 4x4 SHOULD
read as rectangular, so this one keeps a high squareness right through, between
7 and 8, which gives a section that is square with a small radius on every
corner rather than an oval. What it gains is that the sill, the bonnet step,
the cabin and the tailgate are now one continuous surface with one break in it
where the scuttle is, instead of four objects meeting at slots.

Its wheels stood 45 cm proud of the bodywork, more than any other car here, so
the body goes out from 1.78 to 2.02 and the arches are stations in the hull at
each axle, the same fix the other four got.

The glasshouse is upright and nearly rectangular, because that is the whole
face of this kind of vehicle, and everything that made it characterful (the
bull bar, the round lamps, the snorkel up the pillar, the full length cream
roof, the rack and the light bar) is carried over onto the new surface.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("    bodyY:-0.18, paint:0x3f9dab, second:0xf0ece0, W:1.78, L:4.30 },",
    "    bodyY:-0.18, paint:0x3f9dab, second:0xf0ece0, W:2.02, L:4.30 },")

i0 = s.index("  function shellBracken(V){")
i1 = s.index("  function shellMarisol(V){")
# keep the tail of the old function that sits after the arches, if any
new = r"""  function shellBracken(V){
    W=V.W;
    var hw=W/2;

    /* One hull, floor to beltline. Squareness stays high all the way through,
       so every corner is a radius on a box and not an oval: this is a utility
       vehicle and it should read as one. The single break is the scuttle,
       where the bonnet steps up to the cabin. */
    loft([
      {z: 2.22, w:hw*0.94, y: 0.06, up:0.34, dn:0.42, n:7.0},
      {z: 2.10, w:hw*0.99, y: 0.08, up:0.38, dn:0.44, n:7.6},
      {z: 1.78, w:hw*1.18, y: 0.10, up:0.40, dn:0.46, n:6.6},   /* front flare */
      {z: 1.55, w:hw*1.30, y: 0.10, up:0.40, dn:0.46, n:6.4},
      {z: 1.30, w:hw*1.16, y: 0.12, up:0.42, dn:0.48, n:6.8},
      {z: 0.94, w:hw*1.00, y: 0.14, up:0.44, dn:0.50, n:7.6},   /* bonnet */
      {z: 0.80, w:hw*1.00, y: 0.30, up:0.74, dn:0.62, n:7.8},   /* the scuttle */
      {z: 0.10, w:hw*1.00, y: 0.32, up:0.76, dn:0.64, n:7.8},
      {z:-1.20, w:hw*1.00, y: 0.32, up:0.76, dn:0.64, n:7.8},
      {z:-1.46, w:hw*1.16, y: 0.31, up:0.75, dn:0.62, n:6.8},   /* rear flare */
      {z:-1.70, w:hw*1.30, y: 0.31, up:0.75, dn:0.60, n:6.4},
      {z:-1.96, w:hw*1.14, y: 0.31, up:0.75, dn:0.62, n:6.8},
      {z:-2.26, w:hw*0.98, y: 0.30, up:0.74, dn:0.62, n:7.4},
      {z:-2.36, w:hw*0.84, y: 0.28, up:0.68, dn:0.56, n:6.2}
    ], paint);

    /* the glasshouse: upright and nearly rectangular, which is the face */
    loft([
      {z: 0.86, w:hw*0.88, y: 1.08, up:0.04, dn:0.28, n:5.0},
      {z: 0.62, w:hw*0.92, y: 1.16, up:0.14, dn:0.34, n:6.6},
      {z:-0.60, w:hw*0.93, y: 1.17, up:0.15, dn:0.34, n:7.4},
      {z:-2.06, w:hw*0.92, y: 1.16, up:0.14, dn:0.34, n:7.0},
      {z:-2.24, w:hw*0.86, y: 1.12, up:0.06, dn:0.30, n:5.4}
    ], glass, undefined, undefined, false);

    /* the full length cream roof, which is what this thing is known by */
    box(W*0.92,0.13,3.30, roofM, 0, 1.36,-0.62);
    box(W*0.86,0.07,0.34, roofM, 0, 1.27, 0.94, false);   /* over the screen */

    /* ---- underneath ---- */
    box(1.30,0.14,0.60, trim, 0,-0.34, 2.02);             /* sump guard */
    box(0.17,0.17,2.30, trim,-hw*1.00,-0.34,-0.10);       /* rock sliders */
    box(0.17,0.17,2.30, trim, hw*1.00,-0.34,-0.10);

    /* ---- the face ---- */
    box(W*0.92,0.60,0.12, trim,  0, 0.18, 2.22);          /* upright grille */
    for(var gi=0;gi<5;gi++) box(0.05,0.44,0.05, chrome, -0.44+gi*0.22,0.18,2.27,false);
    box(W*0.98,0.22,0.32, trim, 0,-0.14, 2.24);           /* bull bar */
    box(0.10,0.62,0.10, trim,-hw*0.90, 0.08, 2.24,false);
    box(0.10,0.62,0.10, trim, hw*0.90, 0.08, 2.24,false);
    cyl(0.19,0.11,12, lampM, -hw*0.60,0.24,2.28, Math.PI/2);
    cyl(0.19,0.11,12, lampM,  hw*0.60,0.24,2.28, Math.PI/2);
    cyl(0.10,0.10,8,  lampM, -hw*0.86,0.02,2.28, Math.PI/2);
    cyl(0.10,0.10,8,  lampM,  hw*0.86,0.02,2.28, Math.PI/2);
    box(W*0.60,0.08,0.30, paint, 0, 0.56, 1.60, false);    /* bonnet lip */

    /* ---- the snorkel, up the pillar where it belongs ---- */
    box(0.12,1.24,0.12, trim, hw*0.94, 0.86, 0.84);
    box(0.16,0.16,0.24, trim, hw*0.94, 1.52, 0.78, false);
    box(0.09,0.30,0.09, trim, hw*0.92, 1.18, 0.72, false);

    /* ---- the back ---- */
    box(W*0.80,0.46,0.08, roofM, 0, 0.62,-2.36, false);   /* cream tailgate */
    box(0.26,0.24,0.07, tailM,-hw*0.68, 0.60,-2.38, false);
    box(0.26,0.24,0.07, tailM, hw*0.68, 0.60,-2.38, false);
    box(W*0.96,0.20,0.30, trim, 0,-0.12,-2.30);           /* rear bar */
    /* a spare on the tailgate, which is where this kind of vehicle carries it */
    var spr2=new THREE.Mesh(new THREE.CylinderGeometry(0.40,0.40,0.26,12),tyreM);
    spr2.rotation.x=Math.PI/2; add(spr2,0.18,0.68,-2.54);

    /* ---- rack and lights, standing on the roof they are bolted to ---- */
    [[-hw*0.78,-1.90],[hw*0.78,-1.90],[-hw*0.78,-0.60],[hw*0.78,-0.60]].forEach(function(pp){
      box(0.06,0.12,0.06, trim, pp[0],1.48,pp[1], false);
    });
    box(W*0.84,0.08,1.60, trim, 0, 1.53,-1.28);
    box(0.90,0.24,0.54, canvasM, -0.26,1.69,-1.30);
    [[-0.42],[0.42]].forEach(function(pp){
      box(0.06,0.24,0.06, trim, pp[0],1.54,0.06, false);
    });
    box(1.10,0.13,0.17, trim, 0, 1.72, 0.06, false);      /* roof light bar */
    for(var li=0;li<4;li++)
      cyl(0.085,0.07,10, lampM, -0.39+li*0.26,1.72,0.14, Math.PI/2);

    /* ---- mirrors, and a jerry can on the flank ---- */
    [[-1],[1]].forEach(function(sd){
      box(0.05,0.05,0.20, trim, sd[0]*hw*0.96, 1.02, 0.86, false);
      box(0.16,0.20,0.09, trim, sd[0]*hw*1.06, 1.02, 0.80, false);
    });
    box(0.14,0.42,0.30, trim, -hw*1.02, 0.44,-1.02, false);
  }

"""
s = s[:i0] + new + s[i1:]
n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
