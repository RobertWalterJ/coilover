# -*- coding: utf-8 -*-
"""Audit of all five bodies, and the two that were still stacks of boxes.

THE AUDIT. Built a connectivity test: take every mesh in a body, find the
largest one (the hull), and flood fill through parts whose bounding boxes
touch. Anything the flood never reaches is not attached to the car. Run over
all five:

  Bracken     0 of 49 parts detached
  Marisol T4  1 of 39   the rear light bar, sitting 6 cm behind the tail
  Kestrel RS  0 of 22
  Serrano SV  1 of 27   the rear light bar, 2 cm behind the deck
  Veloce GT   4 of 28   the WHOLE REAR WING: both stalks and the wing and its
                        gurney, hanging 11 cm clear of the deck with nothing
                        under them

The Veloce one is the bad one and it is exactly what you spotted. The stalks
started at y=0.44 and the deck at that station tops out at 0.31.

THE TWO REMAINING BOX CARS. The Kestrel and the Serrano were still stacks of
axis aligned boxes, so they had the same problem the Veloce had before it was
lofted: no matter how the boxes are arranged the corners stay right angles.
Both rebuilt on the loft.

  Kestrel RS  is a lifted rear engine coupe, so: a rounded nose that falls away,
  fenders that stand proud of it at the headlights, a cabin well forward, and
  one unbroken line from the roof over the rear haunch to a cut off tail. The
  sections stay fairly round because that car is round.

  Serrano SV  is a lifted mid engine wedge, and a wedge is not round. Its
  sections keep a high squareness so the surfaces stay taut and faceted; what
  the loft buys here is that the wedge is now continuous from the nose to the
  deck instead of three boxes stepping up.

Both also gain their arches as stations in the hull, which is the only way they
can cover the tyres: the Kestrel's wheels stood 25 cm proud of its bodywork and
the Serrano's 24 cm.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------- 1. the Veloce's wing lands
sub("""    [[-0.60],[0.60]].forEach(function(pp){
      var st=box(0.06,0.32,0.11, carbon, pp[0],0.60,-1.84, false);
      st.rotation.x=0.12;
    });
    var wing=box(W+0.18,0.055,0.42, carbon, 0, 0.80,-1.86, false);
    wing.rotation.x=0.13;
    box(W+0.18,0.05,0.13, carbon, 0, 0.735,-1.70, false);""",
"""    /* The deck at this station tops out at 0.31, so a stalk starting at 0.44
       was standing in mid air. It starts on the deck now. */
    [[-0.60],[0.60]].forEach(function(pp){
      var st=box(0.07,0.52,0.12, carbon, pp[0],0.54,-1.80, false);
      st.rotation.x=0.10;
    });
    var wing=box(W+0.18,0.055,0.42, carbon, 0, 0.78,-1.84, false);
    wing.rotation.x=0.13;
    box(W+0.18,0.05,0.13, carbon, 0, 0.725,-1.68, false);""")

# ------------------------------------------- 2. the Marisol's light bar lands
sub("    box(W*0.82,0.11,0.07, tailM, 0, 0.56,-2.48, false);",
    "    box(W*0.70,0.11,0.09, tailM, 0, 0.56,-2.40, false);")

# ------------------------------------------------- 3. wider bodies, so the
#                                                     arches can cover the tyres
sub("    bodyY:-0.24, paint:0xd8c352, second:0x3a3f52, W:1.80, L:4.05 },",
    "    bodyY:-0.24, paint:0xd8c352, second:0x3a3f52, W:1.96, L:4.05 },")
sub("    bodyY:-0.26, paint:0x66c04a, second:0x241f2a, W:1.86, L:4.12 },",
    "    bodyY:-0.26, paint:0x66c04a, second:0x241f2a, W:2.06, L:4.12 },")

# ------------------------------------------------------ 4. the two rebuilds
i0 = s.index("  /* ---- Kestrel RS:")
i1 = s.index("  /* shared flare, sized to the car it is on */")
new = """  /* ---- Kestrel RS: a lifted rear engine coupe. The whole car is one line
     from the nose over the roof and down the fastback into a cut off tail,
     with the fenders standing proud of the bonnet at the headlights and the
     rear haunch as the widest thing on it. Round sections, because it is a
     round car. ---- */
  function shellKestrel(V){
    W=V.W;
    var hw=W/2;
    loft([
      {z: 2.00, w:hw*0.58, y: 0.14, up:0.13, dn:0.13, n:2.8},
      {z: 1.80, w:hw*0.80, y: 0.16, up:0.21, dn:0.17, n:3.0},
      {z: 1.52, w:hw*1.14, y: 0.19, up:0.31, dn:0.21, n:3.4},   /* fender tops */
      {z: 1.24, w:hw*1.24, y: 0.20, up:0.33, dn:0.22, n:3.8},   /* front arch */
      {z: 0.96, w:hw*1.10, y: 0.22, up:0.33, dn:0.22, n:3.6},
      {z: 0.52, w:hw*0.98, y: 0.25, up:0.35, dn:0.24, n:3.8},
      {z:-0.12, w:hw*1.00, y: 0.27, up:0.37, dn:0.25, n:4.0},
      {z:-0.84, w:hw*1.14, y: 0.27, up:0.39, dn:0.25, n:4.2},   /* haunch */
      {z:-1.22, w:hw*1.24, y: 0.27, up:0.39, dn:0.25, n:4.4},   /* rear arch */
      {z:-1.64, w:hw*1.10, y: 0.25, up:0.35, dn:0.23, n:4.0},
      {z:-1.94, w:hw*0.90, y: 0.22, up:0.27, dn:0.19, n:3.4},
      {z:-2.04, w:hw*0.70, y: 0.20, up:0.21, dn:0.16, n:3.0}
    ], paint);

    /* cabin forward, then one unbroken fastback */
    loft([
      {z: 1.02, w:hw*0.62, y: 0.48, up:0.05, dn:0.16, n:2.6},
      {z: 0.62, w:hw*0.74, y: 0.60, up:0.16, dn:0.20, n:3.0},
      {z: 0.04, w:hw*0.80, y: 0.64, up:0.20, dn:0.24, n:3.4},
      {z:-0.62, w:hw*0.76, y: 0.58, up:0.16, dn:0.26, n:3.4},
      {z:-1.22, w:hw*0.62, y: 0.44, up:0.06, dn:0.24, n:2.8}
    ], glass, undefined, undefined, false);
    loft([
      {z: 0.42, w:hw*0.75, y: 0.61, up:0.18, dn:0.20, n:3.0},
      {z: 0.04, w:hw*0.81, y: 0.64, up:0.21, dn:0.24, n:3.4},
      {z:-0.62, w:hw*0.77, y: 0.58, up:0.17, dn:0.26, n:3.4},
      {z:-1.10, w:hw*0.66, y: 0.46, up:0.09, dn:0.24, n:2.8}
    ], paint, 0.15, 0.35, false);

    /* round lamps standing in the fender tops, which is the whole face */
    cyl(0.185,0.13,12, lampM, -hw*0.72,0.44,1.58, Math.PI/2);
    cyl(0.185,0.13,12, lampM,  hw*0.72,0.44,1.58, Math.PI/2);
    box(hw*0.80,0.10,0.30, second, 0, 0.30, 1.84, false);      /* bonnet vent */
    box(W*0.74,0.15,0.22, trim, 0,-0.06, 1.92, false);         /* nose intake */
    /* a ducktail that sits ON the deck, and louvres over the engine */
    var duck=box(W*0.80,0.10,0.46, second, 0, 0.60,-1.62, false);
    duck.rotation.x=0.16;
    for(var lv=0;lv<4;lv++) box(hw*0.86,0.04,0.09, second, 0,0.53,-1.02-lv*0.18, false);
    box(W*0.76,0.12,0.07, tailM, 0, 0.42,-1.96, false);
    box(W*0.62,0.14,0.20, trim, 0,-0.10,-1.92, false);
    /* mirrors on stalks that reach the door, not the air */
    [[-1],[1]].forEach(function(sd){
      box(0.05,0.05,0.18, trim, sd[0]*hw*0.86, 0.46, 0.78, false);
      box(0.15,0.09,0.09, second, sd[0]*hw*0.98, 0.47, 0.72, false);
    });
    box(0.06,0.16,0.62, trim, -hw*1.02, 0.12,-0.62, false);    /* side intake */
    box(0.06,0.16,0.62, trim,  hw*1.02, 0.12,-0.62, false);
    box(W*0.94,0.08,0.16, trim, 0,-0.14, 0.20, false);         /* sill */
  }

  /* ---- Serrano SV: a lifted mid engine wedge. A wedge is not round, so the
     sections stay square and the surfaces taut; what the loft buys is that the
     wedge runs unbroken from the nose to the engine deck instead of three
     boxes stepping up. ---- */
  function shellSerrano(V){
    W=V.W;
    var hw=W/2;
    loft([
      {z: 2.06, w:hw*0.64, y:-0.02, up:0.07, dn:0.10, n:4.0},
      {z: 1.82, w:hw*0.86, y: 0.02, up:0.15, dn:0.14, n:4.4},
      {z: 1.50, w:hw*1.20, y: 0.06, up:0.23, dn:0.18, n:5.0},   /* front arch */
      {z: 1.22, w:hw*1.30, y: 0.06, up:0.25, dn:0.18, n:5.4},
      {z: 0.92, w:hw*1.12, y: 0.08, up:0.27, dn:0.20, n:4.8},
      {z: 0.28, w:hw*1.00, y: 0.10, up:0.29, dn:0.22, n:4.6},
      {z:-0.42, w:hw*1.06, y: 0.12, up:0.31, dn:0.22, n:4.8},
      {z:-1.02, w:hw*1.20, y: 0.12, up:0.31, dn:0.22, n:5.2},   /* rear arch */
      {z:-1.30, w:hw*1.30, y: 0.12, up:0.30, dn:0.21, n:5.4},
      {z:-1.70, w:hw*1.12, y: 0.10, up:0.27, dn:0.19, n:4.8},
      {z:-2.00, w:hw*0.94, y: 0.08, up:0.21, dn:0.16, n:4.2},
      {z:-2.10, w:hw*0.74, y: 0.06, up:0.15, dn:0.13, n:3.6}
    ], paint);

    loft([
      {z: 1.06, w:hw*0.60, y: 0.34, up:0.04, dn:0.14, n:3.0},
      {z: 0.70, w:hw*0.70, y: 0.46, up:0.14, dn:0.18, n:3.4},
      {z: 0.18, w:hw*0.74, y: 0.51, up:0.17, dn:0.22, n:3.8},
      {z:-0.32, w:hw*0.70, y: 0.48, up:0.13, dn:0.22, n:3.8},
      {z:-0.72, w:hw*0.58, y: 0.40, up:0.05, dn:0.20, n:3.2}
    ], glass, undefined, undefined, false);
    loft([
      {z: 0.44, w:hw*0.71, y: 0.48, up:0.16, dn:0.18, n:3.4},
      {z: 0.18, w:hw*0.75, y: 0.51, up:0.18, dn:0.22, n:3.8},
      {z:-0.32, w:hw*0.71, y: 0.48, up:0.14, dn:0.22, n:3.8},
      {z:-0.66, w:hw*0.62, y: 0.41, up:0.07, dn:0.20, n:3.2}
    ], paint, 0.15, 0.35, false);

    /* the wedge's face: a slot, a splitter and rally lamps on the bar */
    box(W*0.40,0.07,0.24, second, 0, 0.14, 1.98, false);
    box(W*0.86,0.06,0.46, carbon, 0,-0.10, 1.90, false);
    var bar=box(W*0.52,0.09,0.09, trim, 0, 0.18, 1.96, false);
    for(var rl=0;rl<3;rl++)
      cyl(0.105,0.09,10, lampM, -0.34+rl*0.34, 0.26, 1.98, Math.PI/2);
    cyl(0.115,0.09,10, lampM, -hw*0.66,0.16,2.00, Math.PI/2);
    cyl(0.115,0.09,10, lampM,  hw*0.66,0.16,2.00, Math.PI/2);

    /* a roof scoop feeding the engine, sitting on the roof it feeds */
    var sc2=box(hw*0.44,0.11,0.52, second, 0, 0.70, 0.06, false);
    sc2.rotation.x=0.10;
    /* engine deck louvres and a spoiler standing on the deck, not above it */
    for(var s2=0;s2<5;s2++) box(hw*0.92,0.04,0.09, second, 0,0.43,-0.86-s2*0.20, false);
    [[-0.72],[0.72]].forEach(function(pp){
      box(0.08,0.30,0.10, carbon, pp[0],0.44,-1.72, false);
    });
    var spo=box(W+0.10,0.06,0.40, carbon, 0, 0.60,-1.74, false);
    spo.rotation.x=0.12;
    /* diffuser, lights and sills, all touching the body they belong to */
    var dif2=box(W*0.82,0.14,0.44, carbon, 0,-0.02,-1.94, false);
    dif2.rotation.x=-0.26;
    box(W*0.70,0.11,0.07, tailM, 0, 0.24,-2.02, false);
    box(0.09,0.18,0.56, trim, -hw*1.06, 0.06,-0.60, false);
    box(0.09,0.18,0.56, trim,  hw*1.06, 0.06,-0.60, false);
    box(0.10,0.10,2.10, carbon, -hw*1.04,-0.14, 0.10, false);
    box(0.10,0.10,2.10, carbon,  hw*1.04,-0.14, 0.10, false);
    [[-1],[1]].forEach(function(sd){
      box(0.05,0.05,0.18, trim, sd[0]*hw*0.80, 0.42, 0.80, false);
      box(0.15,0.08,0.09, second, sd[0]*hw*0.92, 0.43, 0.74, false);
    });
  }

"""
s = s[:i0] + new + s[i1:]
n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
