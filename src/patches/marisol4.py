# -*- coding: utf-8 -*-
"""The Marisol goes back to boxes, because a truck is boxes.

You are right and I was wrong about the method. The loft I built makes rounded
sections by construction: it sweeps a superellipse down the length and smooths
the normals, so the best it can ever do for a truck is a soft-edged capsule.
Pushing the squareness up to 6.6 did not fix that, it just made a squarer
capsule, which is exactly the pill you are looking at.

A rally raid truck is not a shape you can loft. It is a flat-fronted cab box, a
frame, and a cargo box behind, with hard edges and visible seams between them,
and that is how it is built now: flat shaded boxes, sharp corners, and each
volume clearly a separate thing bolted to a chassis. The cab is the tallest
mass and sits over the front axle; the body behind is 35 cm lower so the step
reads from any angle; the frame runs through underneath and both sit on it,
which is what joins them.

This needed a second paint material. When I lofted the cars I set the shared
`paint` to smooth shading, which is right for a curved body and wrong for a
box: a smooth-shaded cube has soft gradients across faces that should be flat.
There is now a flat one alongside it, and both take the vehicle's colour.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- a flat shaded paint for the cars that are made of panels, not curves
sub("""  var paint  = styleMat(mat(0x3f9dab,{flatShading:false}),
                        {rim:[2.4,0.95],obj:true,tex:'paint'});""",
"""  var paint  = styleMat(mat(0x3f9dab,{flatShading:false}),
                        {rim:[2.4,0.95],obj:true,tex:'paint'});
  /* Same colour, hard edges. A smooth shaded box has gradients running across
     faces that ought to be flat, which is half of why a boxy truck built out
     of the lofted material looked wrong. */
  var paintF = styleMat(mat(0x3f9dab),{rim:[2.4,0.95],obj:true,tex:'paint'});""")

sub("""    paint.color.copy(sc(V.paint));""",
"""    paint.color.copy(sc(V.paint));
    paintF.color.copy(sc(V.paint));
    paintF.emissive.copy(new THREE.Color(V.paint).convertSRGBToLinear()).multiplyScalar(0.36);""")

# ---- and the truck, rebuilt out of panels
i0 = s.index("  /* ---- Marisol T4:")
i1 = s.index("  /* ---- Kestrel RS:")
new = r"""  /* ---- Marisol T4: a Dakar rally raid truck, built the way one is: a frame,
     a flat fronted cab over the front axle, and a cargo body behind it that is
     lower than the cab so the step reads. Hard edges throughout. A truck is
     not a shape you can loft. ---- */
  function shellMarisol(V){
    W=V.W;
    var hw=W/2;

    /* ---- the frame, which is the thing everything else is bolted to ---- */
    box(W*0.92,0.46,4.86, paintF, 0, 0.28, 0.00);
    box(0.20,0.30,4.40, trim, -hw*0.86, 0.10, 0.00);
    box(0.20,0.30,4.40, trim,  hw*0.86, 0.10, 0.00);

    /* ---- the cab: tall, blunt, over the front axle ---- */
    box(W,1.52,2.06, paintF, 0, 1.24, 1.32);
    box(W*1.03,0.14,2.14, second, 0, 2.06, 1.32, false);      /* cab roof */
    var scr=box(W*0.86,0.74,0.10, glass, 0, 1.56, 2.31, false);
    scr.rotation.x=-0.13;                                      /* a slight rake */
    box(0.10,0.58,0.96, glass, -hw*0.99, 1.50, 1.62, false);
    box(0.10,0.58,0.96, glass,  hw*0.99, 1.50, 1.62, false);
    box(W*0.30,0.16,0.10, second, 0, 1.06, 2.33, false);       /* badge panel */

    /* ---- the face ---- */
    box(W*0.94,0.56,0.14, trim, 0, 0.66, 2.34);                /* grille */
    for(var gv=0;gv<6;gv++)
      box(W*0.82,0.05,0.05, chrome, 0, 0.46+gv*0.09, 2.41, false);
    box(W*0.98,0.26,0.34, trim, 0, 0.30, 2.44);                /* bull bar */
    box(0.14,0.62,0.14, trim, -hw*0.66, 0.60, 2.44);
    box(0.14,0.62,0.14, trim,  hw*0.66, 0.60, 2.44);
    cyl(0.20,0.13,12, lampM, -hw*0.56,0.72,2.42, Math.PI/2);
    cyl(0.20,0.13,12, lampM,  hw*0.56,0.72,2.42, Math.PI/2);
    box(W*0.86,0.10,0.86, trim, 0,-0.02, 1.94, false);         /* sump guard */

    /* ---- the body behind: lower than the cab, so the step reads ---- */
    box(W*0.98,1.18,2.72, paintF, 0, 0.94,-1.10);
    box(W*1.00,0.12,2.78, second, 0, 1.58,-1.10, false);       /* deck lip */
    /* ribs down the flank, which is what a body like this actually has */
    for(var rb2=0;rb2<5;rb2++){
      box(0.07,1.06,0.09, trim, -hw*1.00, 0.94,-0.10-rb2*0.52, false);
      box(0.07,1.06,0.09, trim,  hw*1.00, 0.94,-0.10-rb2*0.52, false);
    }
    box(W*0.90,0.90,0.10, second, 0, 0.92,-2.47, false);       /* tailgate */
    box(W*0.70,0.12,0.08, tailM, 0, 0.42,-2.50, false);
    box(W*0.96,0.22,0.30, trim, 0, 0.08,-2.50);                /* rear bar */
    box(W*0.86,0.06,0.34, trim, 0,-0.10,-2.62, false);         /* mudflap */

    /* ---- spares lashed flat on the deck ---- */
    [[-0.50,-0.52],[0.50,-0.52],[-0.50,-1.44],[0.50,-1.44]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.40,0.40,0.24,12),tyreM);
      add(sw,sp[0],1.68,sp[1]);
    });
    box(W*0.92,0.07,0.07, trim, 0, 1.66,-0.10, false);
    box(W*0.92,0.07,0.07, trim, 0, 1.66,-1.90, false);
    box(0.07,0.07,1.86, trim, -hw*0.88, 1.66,-1.00, false);
    box(0.07,0.07,1.86, trim,  hw*0.88, 1.66,-1.00, false);
    /* two jerry cans and a toolbox on the frame, off the side */
    box(0.20,0.44,0.32, trim, -hw*0.98, 0.36, 0.30, false);
    box(0.20,0.44,0.32, trim, -hw*0.98, 0.36,-0.08, false);
    box(0.26,0.34,0.80, second, hw*0.96, 0.34, 0.10, false);

    /* ---- a light bar and a rack on the cab roof, bolted to it ---- */
    [[-hw*0.80],[hw*0.80]].forEach(function(pp){
      box(0.07,0.22,0.07, trim, pp[0], 2.20, 2.06, false);
      box(0.07,0.22,0.07, trim, pp[0], 2.20, 0.62, false);
      box(0.07,0.07,1.50, trim, pp[0], 2.30, 1.34, false);
    });
    box(W*1.62/2,0.07,0.07, trim, 0, 2.30, 2.06, false);
    box(W*1.62/2,0.07,0.07, trim, 0, 2.30, 0.62, false);
    box(W*0.60,0.16,0.18, trim, 0, 2.42, 2.02, false);
    for(var li=0;li<5;li++)
      cyl(0.09,0.09,10, lampM, -0.44+li*0.22, 2.42, 2.10, Math.PI/2);

    /* ---- the snorkel, up the back of the cab ---- */
    box(0.15,1.10,0.15, trim, hw*0.96, 1.52, 0.44);
    box(0.17,0.17,0.26, trim, hw*0.96, 2.14, 0.36, false);

    /* ---- square arches, angled out over the wheels ---- */
    [[1.70],[-1.54]].forEach(function(a){
      [[-1],[1]].forEach(function(sd){
        var ar=box(0.42,0.20,V.wheelR*2.5, trim,
                   sd[0]*hw*0.96, 0.62, a[0], false);
        ar.rotation.z=-sd[0]*0.30;
      });
    });
    /* steps into the cab */
    box(0.34,0.07,0.42, trim, -hw*0.98,-0.04, 1.10, false);
    box(0.34,0.07,0.42, trim,  hw*0.98,-0.04, 1.10, false);
  }

"""
s = s[:i0] + new + s[i1:]
n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
