# -*- coding: utf-8 -*-
"""The vehicle rebuild.

The headline defect, and I should have caught it much earlier: the coilovers
were invisible. The spring sat at the wheel centre with a radius of 0.13 inside
a tyre of radius 0.55 and half width 0.23, so it was entirely enclosed by its
own wheel. In a game called Coilover, built around exaggerated strut travel,
you could not see a single spring move. Geometry confirmed it and a side view
confirmed the geometry.

They now sit outboard of the body and offset toward the middle of the truck, so
each one stands in clear air between the wheels where the whole travel reads
from the side. They are thicker, and a link bar runs from the strut foot to the
hub so the movement is connected to something rather than floating.

The second defect: every corner was one black mass. Tyre 0x241f2a, lugs
0x1a171f, arches 0x24313a. Three near blacks touching, so the wheel had no
internal shape and its travel was invisible even when it moved. The arch is now
a mid grey flare, the rim face is light, and the tyre carries a lighter
shoulder, so the wheel reads as a wheel and you can see it work.

Third: the whole truck was a silhouette. Against a low key desert the dark teal
and the near black trim collapsed together and only the headlights and the roof
strip read at all. The paint comes up, the trim separates from the tyres, and
the body keeps a light shoulder line so the shape holds at distance.

Stance: track goes 1.90 to 2.06 and the tyres get wider and squarer in the
shoulder. The physics is untouched, because WHEEL_R drives the raycast and it
stays where it is.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:100].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------------------------ stance
sub("var TRACK=1.90, WHEELBASE=3.10;", "var TRACK=2.06, WHEELBASE=3.10;")

# ------------------------------------------------------------- the palette
# the corner needs three separable values, not three near blacks
sub("""  var trim   = smat(0x24313a);                           /* black trim and arches */""",
"""  var trim   = smat(0x3d4650);                           /* trim, no longer near black */
  var flare  = smat(0x6f6675);                           /* arch flares, a mid grey */
  var shoulder=smat(0x3a3340);                           /* tyre shoulder, lifts the wheel */""")
sub("  var rimM   = smat(PAL.wheel);", "  var rimM   = smat(0xbdb3a2);           /* a light rim face reads at distance */")

# the body was collapsing into the ground at every time of day
sub("""  var paint  = styleMat(mat(PAL.body),{rim:[2.4,0.85]});
  paint.emissive=new THREE.Color(PAL.body).convertSRGBToLinear().multiplyScalar(0.30);""",
"""  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95]});
  paint.emissive=new THREE.Color(0x3f9dab).convertSRGBToLinear().multiplyScalar(0.36);""")

# ----------------------------------------------------- arches become flares
sub("""  [[-1,1.55],[1,1.55],[-1,-1.55],[1,-1.55]].forEach(function(f){
    var ar=box(0.30,0.22,1.62, trim, f[0]*(W/2+0.06),-0.02,f[1]);
    ar.rotation.z=(f[0]<0?1:-1)*0.30;
  });""",
"""  /* A wider flare, in a value that separates from both the tyre below it and
     the paint above it, so the gap the wheel travels through is legible. */
  [[-1,1.55],[1,1.55],[-1,-1.55],[1,-1.55]].forEach(function(f){
    var ar=box(0.34,0.24,1.74, flare, f[0]*(W/2+0.13),0.02,f[1]);
    ar.rotation.z=(f[0]<0?1:-1)*0.30;
    var lip=box(0.30,0.10,1.66, trim, f[0]*(W/2+0.16),-0.13,f[1]);
    lip.rotation.z=(f[0]<0?1:-1)*0.30;
  });
  /* a light shoulder line down each flank so the body holds its shape when
     the whole truck is sitting in one dark band */
  box(W+0.03,0.07,3.90, roofM, 0, 0.30, -0.20, false);""")

# ------------------------------------------------------- the visible coilover
sub("  var springGeo=helix(0.130,7,1.0,0.032);",
    "  var springGeo=helix(0.170,7,1.0,0.044);   /* thicker, it is the whole point */")

sub("""  var tyreGeo=new THREE.CylinderGeometry(WHEEL_R,WHEEL_R,0.46,14);
  tyreGeo.rotateZ(Math.PI/2);
  var lugGeo=new THREE.CylinderGeometry(WHEEL_R*1.075,WHEEL_R*1.075,0.34,9);
  lugGeo.rotateZ(Math.PI/2);
  var lug2Geo=new THREE.CylinderGeometry(WHEEL_R*1.055,WHEEL_R*1.055,0.20,9);
  lug2Geo.rotateZ(Math.PI/2); lug2Geo.rotateX(Math.PI/9);
  var rimGeo=new THREE.CylinderGeometry(WHEEL_R*0.52,WHEEL_R*0.52,0.48,8);
  rimGeo.rotateZ(Math.PI/2);
  var hubGeo=new THREE.CylinderGeometry(WHEEL_R*0.16,WHEEL_R*0.16,0.52,6);
  hubGeo.rotateZ(Math.PI/2);""",
"""  /* Wider and squarer in the shoulder. WHEEL_R is left alone because the
     raycast uses it, so this is all silhouette and no physics. */
  var tyreGeo=new THREE.CylinderGeometry(WHEEL_R,WHEEL_R,0.62,14);
  tyreGeo.rotateZ(Math.PI/2);
  var shoGeo=new THREE.CylinderGeometry(WHEEL_R*0.965,WHEEL_R*0.965,0.66,14);
  shoGeo.rotateZ(Math.PI/2);
  var lugGeo=new THREE.CylinderGeometry(WHEEL_R*1.105,WHEEL_R*1.105,0.50,9);
  lugGeo.rotateZ(Math.PI/2);
  var lug2Geo=new THREE.CylinderGeometry(WHEEL_R*1.085,WHEEL_R*1.085,0.30,9);
  lug2Geo.rotateZ(Math.PI/2); lug2Geo.rotateX(Math.PI/9);
  var rimGeo=new THREE.CylinderGeometry(WHEEL_R*0.56,WHEEL_R*0.56,0.64,8);
  rimGeo.rotateZ(Math.PI/2);
  var hubGeo=new THREE.CylinderGeometry(WHEEL_R*0.17,WHEEL_R*0.17,0.70,6);
  hubGeo.rotateZ(Math.PI/2);
  var linkGeo=new THREE.BoxGeometry(0.13,0.13,0.62);""")

sub("""    var shock=new THREE.Mesh(new THREE.CylinderGeometry(0.050,0.050,1.0,7),chrome);
    shock.position.y=-0.5; grp.add(shock);
    var spr=new THREE.Mesh(springGeo,spring); grp.add(spr);

    var arm=new THREE.Mesh(new THREE.BoxGeometry(0.70,0.11,0.20),trim);
    arm.castShadow=true; grp.add(arm);

    var hubg=new THREE.Group(); grp.add(hubg);
    var wheel=new THREE.Mesh(tyreGeo,tyreM); wheel.castShadow=true; hubg.add(wheel);
    hubg.add(new THREE.Mesh(lugGeo,lugM));
    hubg.add(new THREE.Mesh(lug2Geo,lugM));
    var rim=new THREE.Mesh(rimGeo,rimM); hubg.add(rim);
    hubg.add(new THREE.Mesh(hubGeo,chrome));

    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim});""",
"""    /* The coilover stands in open air, outboard of the body and set toward
       the middle of the truck, so the tyre no longer hides it. Front struts
       sit behind their wheel, rear struts ahead of theirs. */
    var zOff=(i<2? -0.56 : 0.56);

    var shock=new THREE.Mesh(new THREE.CylinderGeometry(0.062,0.062,1.0,7),chrome);
    shock.position.set(0,-0.5,zOff); grp.add(shock);
    var spr=new THREE.Mesh(springGeo,spring);
    spr.position.z=zOff; spr.castShadow=true; grp.add(spr);
    /* a cap top and bottom, so it terminates rather than just stopping */
    var capT=new THREE.Mesh(new THREE.BoxGeometry(0.40,0.09,0.24),trim);
    capT.position.set(0,0.05,zOff); grp.add(capT);
    var capB=new THREE.Mesh(new THREE.BoxGeometry(0.34,0.09,0.22),trim);
    grp.add(capB);

    var arm=new THREE.Mesh(new THREE.BoxGeometry(0.70,0.11,0.20),trim);
    arm.castShadow=true; grp.add(arm);
    /* and a link from the strut foot back to the hub, so the travel is
       attached to the wheel instead of happening beside it */
    var link=new THREE.Mesh(linkGeo,trim); link.castShadow=true; grp.add(link);

    var hubg=new THREE.Group(); grp.add(hubg);
    var wheel=new THREE.Mesh(tyreGeo,tyreM); wheel.castShadow=true; hubg.add(wheel);
    hubg.add(new THREE.Mesh(shoGeo,shoulder));
    hubg.add(new THREE.Mesh(lugGeo,lugM));
    hubg.add(new THREE.Mesh(lug2Geo,lugM));
    var rim=new THREE.Mesh(rimGeo,rimM); hubg.add(rim);
    hubg.add(new THREE.Mesh(hubGeo,chrome));

    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim,
                link:link,capB:capB,zOff:zOff});""")

# ------------------------------------------------------------ animate the link
sub("""    st.arm.position.set(c.left?0.24:-0.24,-len*0.92,0);
    st.arm.rotation.z=(c.left?1:-1)*Math.atan2(len*0.30,0.5);""",
"""    st.arm.position.set(c.left?0.24:-0.24,-len*0.92,0);
    st.arm.rotation.z=(c.left?1:-1)*Math.atan2(len*0.30,0.5);
    /* the strut foot rides the hub, and the link joins the two */
    st.capB.position.set(0,-len,st.zOff);
    st.link.position.set(0,-len,st.zOff*0.5);
    st.link.scale.z=Math.abs(st.zOff)/0.62*1.02;""")

# ---------------------------------------------- the snorkel read as a chimney
sub("""  box(0.10,0.34,0.10, trim, 0.92, 1.24, 0.72,false);  /* snorkel up the pillar */
  box(0.14,1.30,0.14, trim, 0.96, 0.80, 0.86);
  box(0.20,0.20,0.20, trim, 0.96, 1.48, 0.86,false);""",
"""  box(0.09,0.30,0.09, trim, 0.93, 1.20, 0.74,false);  /* snorkel up the pillar */
  box(0.11,1.16,0.11, trim, 0.955, 0.76, 0.86);
  box(0.15,0.15,0.15, trim, 0.955, 1.36, 0.86,false);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
