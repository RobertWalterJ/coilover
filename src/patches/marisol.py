# -*- coding: utf-8 -*-
"""The Marisol was a tractor, and the Veloce's wheels were outside its body.

THE MARISOL. It is meant to be a Dakar T4 rally raid truck, the Kamaz sort:
forward control, cab over the front axle, one tall body running the length of
it, wheels at the extreme corners. What was actually built was a short cab box
at the front, a separate low deck at the back, and a light gantry over the top
of the gap between them, which is the exact silhouette of a farm tractor with
an implement on the back.

The frame really does end in mid air. The two roof rails run from z=+0.30 to
z=-1.50 at y=1.55 and there is no rear hoop, no down tubes and nothing under
them. They are two poles sticking out over the back attached at one end only.
That is not a detail I missed, it is the whole rear structure missing.

Rebuilt as one lofted mass from nose to tail: a blunt forward control face, a
tall cab, a step down behind it and a rear body of nearly the same height, so
the truck reads as a single object. The gantry is gone. In its place is a roof
rack that closes on all four sides and sits on the cab where it belongs, spare
wheels lashed to the deck, and arches over the wheels.

THE VELOCE. The body was 1.90 wide on a 2.24 track, so each wheel stood 17 cm
proud of the bodywork with the coilover in open air beside it, and the arch
hoops floated clear of everything. Body out to 2.10, track in to 2.00, so the
wheels sit under the arches; and on this one car the exposed struts are tucked
away, because a GT keeps its suspension inside the body. The trucks keep theirs
on show.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================ 1. proportions that work
sub("    mass:1310, track:2.24, wb:2.98, wheelR:0.46, tyreW:0.60,",
    "    mass:1310, track:2.00, wb:2.98, wheelR:0.46, tyreW:0.60,")
sub("    bodyY:-0.30, paint:0x2f5fd0, second:0xe8e2d4, W:1.90, L:4.30 }",
    "    bodyY:-0.30, paint:0x2f5fd0, second:0xe8e2d4, W:2.10, L:4.30, tuck:true }")
sub("    bodyY:-0.10, paint:0xe0683a, second:0xf2e8d4, W:1.92, L:4.55 },",
    "    bodyY:-0.10, paint:0xe0683a, second:0xf2e8d4, W:2.36, L:4.55 },")

# a GT keeps its suspension inside the bodywork; the trucks show theirs off
sub("    /* new shell */",
    "    /* A GT hides its suspension under the body. The off roaders keep theirs\n"
    "       out in the open, which was the whole point of the exposed strut. */\n"
    "    var show=!V.tuck;\n"
    "    for(var q=0;q<4;q++){\n"
    "      var sq=STRUT[q];\n"
    "      sq.shock.visible=show; sq.spring.visible=show;\n"
    "      sq.arm.visible=show;   sq.link.visible=show; sq.capB.visible=show;\n"
    "    }\n"
    "\n"
    "    /* new shell */")

# the arch lip should sit on the body edge, not hover beside it
sub("    var ay=V.wheelR*0.36-V.bodyY-0.30;\n"
    "    [[1.42],[-1.44]].forEach(function(a){\n"
    "      archT(flare, -hw*0.99, ay, a[0], V.wheelR*1.12, 0.075);\n"
    "      archT(flare,  hw*0.99, ay, a[0], V.wheelR*1.12, 0.075);\n"
    "    });",
    "    var ay=V.wheelR*0.30-V.bodyY-0.30;\n"
    "    [[1.42],[-1.44]].forEach(function(a){\n"
    "      archT(flare, -hw*0.90, ay, a[0], V.wheelR*1.04, 0.055);\n"
    "      archT(flare,  hw*0.90, ay, a[0], V.wheelR*1.04, 0.055);\n"
    "    });")

# ================================================== 2. the Marisol, rebuilt
i0 = s.index("  function shellMarisol(V){")
i1 = s.index("  /* ---- Kestrel RS:")
new = """  /* ---- Marisol T4: a Dakar rally raid truck. Forward control, so the cab
     sits over the front axle and the face is blunt and upright; one mass from
     the nose to the tail with a step down behind the cab; wheels pushed to
     the extreme corners under real arches. Everything that was an unattached
     pole over the back is gone. ---- */
  function shellMarisol(V){
    W=V.W;
    var hw=W/2;

    /* the hull: cab and body as one object, which is what stops it reading as
       a tractor pulling something */
    loft([
      {z: 2.34, w:hw*0.86, y: 0.46, up:0.52, dn:0.56, n:4.6},
      {z: 2.16, w:hw*0.95, y: 0.48, up:0.60, dn:0.60, n:5.0},
      {z: 1.55, w:hw*1.00, y: 0.50, up:0.66, dn:0.62, n:5.4},
      {z: 0.72, w:hw*1.00, y: 0.50, up:0.66, dn:0.62, n:5.4},
      {z: 0.30, w:hw*0.97, y: 0.42, up:0.52, dn:0.58, n:5.0},
      {z:-0.55, w:hw*0.95, y: 0.38, up:0.46, dn:0.54, n:5.0},
      {z:-1.70, w:hw*0.95, y: 0.38, up:0.46, dn:0.52, n:5.0},
      {z:-2.24, w:hw*0.86, y: 0.34, up:0.40, dn:0.46, n:4.4},
      {z:-2.46, w:hw*0.66, y: 0.30, up:0.30, dn:0.36, n:3.4}
    ], paint);

    /* the screen, raked back off the blunt face, and the door glass */
    var scr=box(W*0.80,0.62,0.07, glass, 0, 0.86, 2.06, false);
    scr.rotation.x=-0.30;
    box(0.06,0.34,0.86, glass, -hw*0.96, 0.82, 1.42, false);
    box(0.06,0.34,0.86, glass,  hw*0.96, 0.82, 1.42, false);
    /* the cab roof, so the top of the cab is a panel and not the paint */
    box(W*0.90,0.09,1.46, second, 0, 1.16, 1.34, false);

    /* a roof rack that CLOSES: four rails and four legs, all joined, sitting
       on the cab. No more poles over the deck attached at one end. */
    var rz0=1.94, rz1=0.72, ry=1.30;
    [[-1],[1]].forEach(function(sd){
      box(0.07,0.07,rz0-rz1, trim, sd[0]*hw*0.84, ry, (rz0+rz1)/2, false);
      box(0.07,0.20,0.07, trim, sd[0]*hw*0.84, ry-0.13, rz0-0.06, false);
      box(0.07,0.20,0.07, trim, sd[0]*hw*0.84, ry-0.13, rz1+0.06, false);
    });
    box(hw*1.68,0.07,0.07, trim, 0, ry, rz0, false);
    box(hw*1.68,0.07,0.07, trim, 0, ry, rz1, false);
    /* and the light bar it exists to carry */
    box(hw*1.30,0.15,0.16, trim, 0, ry+0.13, rz0-0.02, false);
    for(var li=0;li<5;li++)
      cyl(0.085,0.08,10, lampM, -0.44+li*0.22, ry+0.13, rz0+0.06, Math.PI/2);

    /* the deck: spares lashed down, and a rack around them so they belong */
    [[-0.46],[0.46]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,0.26,12),tyreM);
      sw.rotation.x=Math.PI/2; add(sw,sp[0],0.94,-1.30);
    });
    box(W*0.86,0.07,0.07, trim, 0, 0.86,-0.62, false);
    box(W*0.86,0.07,0.07, trim, 0, 0.86,-1.98, false);
    box(0.07,0.07,1.42, trim, -hw*0.84, 0.86,-1.30, false);
    box(0.07,0.07,1.42, trim,  hw*0.84, 0.86,-1.30, false);

    /* arches with a radius, over wheels that are at the corners */
    var ay=V.wheelR*0.28-V.bodyY-0.30;
    [[1.62],[-1.62]].forEach(function(a){
      archT(flare, -hw*0.90, ay, a[0], V.wheelR*1.16, 0.085);
      archT(flare,  hw*0.90, ay, a[0], V.wheelR*1.16, 0.085);
    });

    /* a bull bar and a sump guard, which is what the front of one of these is */
    box(W*0.92,0.16,0.14, trim, 0, 0.30, 2.44, false);
    box(0.12,0.52,0.12, trim, -hw*0.62, 0.08, 2.42, false);
    box(0.12,0.52,0.12, trim,  hw*0.62, 0.08, 2.42, false);
    box(W*0.80,0.09,0.90, trim, 0,-0.22, 1.90, false);
    cyl(0.19,0.12,12, lampM, -hw*0.52,0.34,2.42, Math.PI/2);
    cyl(0.19,0.12,12, lampM,  hw*0.52,0.34,2.42, Math.PI/2);
    /* a snorkel, because these things drive through dust all day */
    box(0.14,0.86,0.14, trim, hw*0.90, 0.98, 1.94, false);
    box(0.16,0.16,0.22, trim, hw*0.90, 1.44, 1.86, false);

    box(W*0.82,0.11,0.07, tailM, 0, 0.44,-2.52, false);
    box(0.30,0.22,0.10, trim, 0,-0.02,-2.50, false);
    /* side steps, so the cab has a way in */
    box(0.16,0.07,1.30, trim, -hw*1.00,-0.16, 0.50, false);
    box(0.16,0.07,1.30, trim,  hw*1.00,-0.16, 0.50, false);
  }

"""
s = s[:i0] + new + s[i1:]
n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
