# -*- coding: utf-8 -*-
"""Four vehicles, and a garage to choose them in.

You asked for options in the spirit of the rally raid cars, the lifted
rear engine coupe and the lifted supercar. All four are invented, with invented
names and no badges of any kind, because copying a real car's trade dress into
a published game is not something I will do.

  BRACKEN     the utility 4x4 you have been driving. Heavy, tall, softest
              springs and the most travel. Slowest, and the most forgiving.
  MARISOL T4  rally raid. Widest track, longest travel, big power, and enough
              rear bias to rotate on the throttle without ever snapping.
  KESTREL RS  a lifted rear engine coupe. Light, and with the weight behind the
              rear axle it rotates early and holds it. Least travel of the
              four, so it skips where the truck absorbs.
  SERRANO SV  a lifted mid engine car on knobblies. Lightest, most power,
              widest track, stiffest springs. Very fast and genuinely nervous.

The physics is not cosmetic. Each car sets its own mass, spring rate, damping,
anti roll bars, drive split, grip, travel and roll couple, and the inertia
tensor is recomputed from its own mass and dimensions.

The strut mounts move too, so the wheels actually sit at the car's own track
and wheelbase, and the wheel geometry is rebuilt when the tyre size changes.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ============================================================ the fleet table
sub("""var truck=new THREE.Group(); scene.add(truck);""",
"""/* ---- the fleet ----
   Every number here is load bearing. `body` draws the shell; everything else
   is handed straight to the solver. */
var VEHICLES=[
  { id:'bracken', name:'Bracken', kind:'Utility 4x4',
    mass:1400, track:2.06, wb:3.10, wheelR:0.55, tyreW:0.62,
    rest:0.60, susMax:0.95, susMin:0.26, k:16400, dBump:1885, dReb:2390,
    arbF:4100, arbR:6640, drive:22000, brake:25000, biasF:0.62,
    dF:0.35, dR:0.65, muF:1.00, muR:0.92, hRoll:0.56, hPitch:1.05,
    bodyY:-0.18, paint:0x3f9dab, second:0xf0ece0, W:1.78, L:4.30 },

  { id:'marisol', name:'Marisol T4', kind:'Rally raid',
    mass:1520, track:2.32, wb:3.24, wheelR:0.60, tyreW:0.68,
    rest:0.72, susMax:1.16, susMin:0.30, k:15200, dBump:2050, dReb:2560,
    arbF:3200, arbR:5200, drive:27500, brake:26500, biasF:0.58,
    dF:0.42, dR:0.58, muF:1.06, muR:1.00, hRoll:0.60, hPitch:1.02,
    bodyY:-0.10, paint:0xe0683a, second:0xf2e8d4, W:1.92, L:4.55 },

  { id:'kestrel', name:'Kestrel RS', kind:'Lifted coupe',
    mass:1240, track:1.94, wb:2.62, wheelR:0.49, tyreW:0.52,
    rest:0.50, susMax:0.78, susMin:0.22, k:19800, dBump:2260, dReb:2820,
    arbF:5400, arbR:7600, drive:25000, brake:27000, biasF:0.66,
    dF:0.10, dR:0.90, muF:0.98, muR:1.02, hRoll:0.44, hPitch:0.86,
    bodyY:-0.24, paint:0xd8c352, second:0x3a3f52, W:1.80, L:4.05 },

  { id:'serrano', name:'Serrano SV', kind:'Lifted mid engine',
    mass:1180, track:2.14, wb:2.72, wheelR:0.47, tyreW:0.56,
    rest:0.46, susMax:0.72, susMin:0.20, k:22400, dBump:2420, dReb:3050,
    arbF:6200, arbR:8400, drive:29500, brake:28500, biasF:0.64,
    dF:0.18, dR:0.82, muF:1.02, muR:1.06, hRoll:0.40, hPitch:0.80,
    bodyY:-0.26, paint:0x66c04a, second:0x241f2a, W:1.86, L:4.12 }
];
var VEH=0;

var truck=new THREE.Group(); scene.add(truck);""")

# ================================================ make the builder swappable
sub("""  /* The body hangs in its own group so it can sit lower over the wheels
     without moving the strut mounts. */
  var bodyG=new THREE.Group(); bodyG.position.y=-0.18; truck.add(bodyG);""",
"""  /* The body hangs in its own group so it can sit lower over the wheels
     without moving the strut mounts, and so a whole shell can be swapped by
     emptying one group. */
  var bodyG=new THREE.Group(); bodyG.position.y=-0.18; truck.add(bodyG);""")

# the existing body build becomes Bracken's, wrapped in a function
sub("""  var W=1.78;                       /* body width */

  /* ---- chassis and lower body ---- */""",
"""  /* ---------------------------------------------------------------- shells
     Each takes the spec and draws itself into bodyG. They share the helpers
     above, so a shell is only the shape, never the plumbing. */
  var W=1.78;

  function shellBracken(V){
  W=V.W;

  /* ---- chassis and lower body ---- */""")

sub("""  /* a light shoulder line down each flank so the body holds its shape when
     the whole truck is sitting in one dark band */
  box(W+0.03,0.07,3.90, roofM, 0, 0.30, -0.20, false);

  /* ---- struts and wheels ---- */""",
"""  /* a light shoulder line down each flank so the body holds its shape when
     the whole truck is sitting in one dark band */
  box(W+0.03,0.07,3.90, roofM, 0, 0.30, -0.20, false);
  }

  /* ---- Marisol T4: rally raid. Low cab well forward, a long tapering tail,
     a spare on the deck and a roll hoop you can see over the body. ---- */
  function shellMarisol(V){
    W=V.W;
    box(W,0.34,4.55, paint, 0,-0.14, 0.00);
    box(W-0.06,0.86,1.72, paint, 0, 0.46, 1.10);          /* forward cab */
    box(1.56,0.50,0.08, glass, 0, 0.74, 1.94, false);
    box(W-0.10,0.10,1.60, roofM, 0, 0.92, 1.06, false);   /* cab roof */
    /* roll hoop, the shape that says rally raid from a long way off */
    [[-0.80],[0.80]].forEach(function(pp){
      box(0.10,1.10,0.10, trim, pp[0],1.02,0.28, false);
    });
    box(1.74,0.10,0.10, trim, 0, 1.55, 0.28, false);
    box(0.10,0.10,1.80, trim,-0.80, 1.55,-0.60, false);
    box(0.10,0.10,1.80, trim, 0.80, 1.55,-0.60, false);
    /* long tail deck, tapering */
    box(W-0.16,0.52,2.30, paint, 0, 0.32,-1.35);
    box(W-0.42,0.26,1.10, roofM, 0, 0.66,-1.90, false);
    var spare=new THREE.Mesh(new THREE.CylinderGeometry(0.44,0.44,0.30,12),tyreM);
    add(spare,0,0.74,-1.30);
    box(1.20,0.16,0.24, trim, 0,-0.06,-2.34);
    box(0.24,0.20,0.06, tailM,-0.62, 0.28,-2.42, false);
    box(0.24,0.20,0.06, tailM, 0.62, 0.28,-2.42, false);
    /* nose, low and wide, with a light bar across it */
    box(W,0.34,0.90, paint, 0, 0.08, 2.10);
    box(1.90,0.18,0.28, trim, 0,-0.14, 2.36);
    cyl(0.17,0.10,12, lampM, -0.52,0.20,2.52, Math.PI/2);
    cyl(0.17,0.10,12, lampM,  0.52,0.20,2.52, Math.PI/2);
    box(1.02,0.13,0.16, trim, 0, 1.62, 0.28, false);
    for(var li=0;li<4;li++)
      cyl(0.080,0.07,10, lampM, -0.36+li*0.24,1.62,0.36, Math.PI/2);
    box(W+0.03,0.07,4.10, roofM, 0, 0.16,-0.10, false);
    flares(V,1.62,-1.62,0.44,0.20);
  }

  /* ---- Kestrel RS: rear engine coupe, lifted. Sloping nose, cabin forward,
     a fat haunch over the back axle and a ducktail. ---- */
  function shellKestrel(V){
    W=V.W;
    box(W,0.44,4.05, paint, 0,-0.04, 0.00);
    /* nose slopes away; two boxes stepping down read as a taper */
    box(W-0.10,0.34,0.90, paint, 0, 0.30, 1.52);
    box(W-0.30,0.24,0.60, paint, 0, 0.46, 1.06, false);
    cyl(0.17,0.10,12, lampM, -0.56,0.34,1.94, Math.PI/2);
    cyl(0.17,0.10,12, lampM,  0.56,0.34,1.94, Math.PI/2);
    box(1.66,0.16,0.24, trim, 0,-0.14, 1.98);
    /* cabin */
    box(W-0.16,0.62,1.42, paint, 0, 0.66, 0.14);
    box(1.46,0.46,0.08, glass, 0, 0.86, 0.86, false);
    box(0.08,0.40,1.10, glass,-0.84, 0.86, 0.10, false);
    box(0.08,0.40,1.10, glass, 0.84, 0.86, 0.10, false);
    box(W-0.22,0.09,1.16, roofM, 0, 1.00, 0.06, false);
    /* haunch over the rear axle, then the ducktail */
    box(W,0.66,1.46, paint, 0, 0.44,-1.16);
    box(1.52,0.30,0.08, glass, 0, 0.70,-0.60, false);
    box(W-0.20,0.09,0.52, second, 0, 0.80,-1.62, false);   /* ducktail */
    box(1.44,0.16,0.06, tailM, 0, 0.50,-1.94, false);
    box(1.30,0.14,0.20, trim, 0,-0.16,-1.96);
    box(W+0.03,0.06,3.60, second, 0, 0.16,-0.10, false);
    flares(V,1.31,-1.31,0.40,0.16);
  }

  /* ---- Serrano SV: mid engine, lifted. A wedge. Low nose, cab pushed
     forward, a wide flat engine deck behind with a spoiler. ---- */
  function shellSerrano(V){
    W=V.W;
    box(W,0.40,4.12, paint, 0,-0.06, 0.00);
    /* the wedge: three steps up from the nose to the roof */
    box(W-0.14,0.22,1.10, paint, 0, 0.22, 1.44);
    box(W-0.34,0.20,0.66, paint, 0, 0.40, 1.02, false);
    cyl(0.13,0.09,10, lampM, -0.60,0.28,1.96, Math.PI/2);
    cyl(0.13,0.09,10, lampM,  0.60,0.28,1.96, Math.PI/2);
    box(1.62,0.14,0.22, trim, 0,-0.16, 2.00);
    box(0.70,0.10,0.30, second, 0, 0.34, 1.98, false);     /* nose slot */
    /* cab, short and forward */
    box(W-0.22,0.52,1.16, paint, 0, 0.58, 0.36);
    box(1.36,0.44,0.10, glass, 0, 0.74, 0.92, false);
    box(0.08,0.34,0.92, glass,-0.80, 0.76, 0.32, false);
    box(0.08,0.34,0.92, glass, 0.80, 0.76, 0.32, false);
    box(W-0.30,0.08,0.94, second, 0, 0.86, 0.30, false);
    /* engine deck, louvres, spoiler */
    box(W-0.06,0.44,1.66, paint, 0, 0.36,-1.06);
    for(var s=0;s<4;s++) box(1.10,0.04,0.09, second, 0,0.59,-0.72-s*0.24, false);
    [[-0.74],[0.74]].forEach(function(pp){
      box(0.09,0.26,0.09, trim, pp[0],0.72,-1.78, false);
    });
    box(W+0.10,0.07,0.42, second, 0, 0.88,-1.80, false);   /* spoiler */
    box(1.36,0.13,0.06, tailM, 0, 0.44,-1.98, false);
    box(1.24,0.14,0.20, trim, 0,-0.18,-2.00);
    box(W+0.03,0.06,3.70, second, 0, 0.10,-0.10, false);
    flares(V,1.36,-1.36,0.46,0.18);
  }

  /* shared flare, sized to the car it is on */
  function flares(V,zf,zr,wid,hgt){
    [[-1,zf],[1,zf],[-1,zr],[1,zr]].forEach(function(f){
      var ar=box(wid,hgt,V.wheelR*2.6, flare, f[0]*(V.track/2*0.99),
                 V.wheelR*0.42-V.bodyY-0.30, f[1]);
      ar.rotation.z=(f[0]<0?1:-1)*0.34;
    });
  }

  var SHELLS={bracken:shellBracken, marisol:shellMarisol,
              kestrel:shellKestrel, serrano:shellSerrano};

  /* ---- struts and wheels ---- */""")

# ------------------------------------------- parameterise the wheel geometry
sub("""  var tyreGeo=new THREE.CylinderGeometry(WHEEL_R,WHEEL_R,0.62,14);
  tyreGeo.rotateZ(Math.PI/2);
  var shoGeo=new THREE.CylinderGeometry(WHEEL_R*0.965,WHEEL_R*0.965,0.66,14);
  shoGeo.rotateZ(Math.PI/2);
  var lugGeo=new THREE.CylinderGeometry(WHEEL_R*1.105,WHEEL_R*1.105,0.50,9);
  lugGeo.rotateZ(Math.PI/2);
  var lug2Geo=new THREE.CylinderGeometry(WHEEL_R*1.085,WHEEL_R*1.085,0.30,9);
  lug2Geo.rotateZ(Math.PI/2); lug2Geo.rotateX(Math.PI/9);
  var rimGeo=new THREE.CylinderGeometry(WHEEL_R*0.63,WHEEL_R*0.63,0.66,8);
  rimGeo.rotateZ(Math.PI/2);
  var hubGeo=new THREE.CylinderGeometry(WHEEL_R*0.20,WHEEL_R*0.20,0.72,6);
  hubGeo.rotateZ(Math.PI/2);
  var linkGeo=new THREE.BoxGeometry(0.13,0.13,0.62);""",
"""  function wheelGeos(R,Wd){
    function C(r,h,seg,tw){
      var g=new THREE.CylinderGeometry(r,r,h,seg); g.rotateZ(Math.PI/2);
      if(tw) g.rotateX(tw); return g;
    }
    return {tyre:C(R,Wd,14), sho:C(R*0.965,Wd*1.06,14),
            lug:C(R*1.105,Wd*0.81,9), lug2:C(R*1.085,Wd*0.48,9,Math.PI/9),
            rim:C(R*0.63,Wd*1.06,8), hub:C(R*0.20,Wd*1.16,6)};
  }
  var WG=wheelGeos(WHEEL_R,0.62);
  var tyreGeo=WG.tyre, shoGeo=WG.sho, lugGeo=WG.lug,
      lug2Geo=WG.lug2, rimGeo=WG.rim, hubGeo=WG.hub;
  var linkGeo=new THREE.BoxGeometry(0.13,0.13,0.62);""")

# --------------------------------------------- keep handles for the swapper
sub("""    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim,
                link:link,capB:capB,zOff:zOff});""",
"""    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim,
                link:link,capB:capB,zOff:zOff,
                sho:hubg.children[1], lugA:hubg.children[2], lugB:hubg.children[3],
                hubc:hubg.children[5]});""")

# ---------------------------------------------------- the swap itself
sub("""      cp:new THREE.Vector3(), nrm:new THREE.Vector3(0,1,0)
    });
  }
})();""",
"""      cp:new THREE.Vector3(), nrm:new THREE.Vector3(0,1,0)
    });
  }

  /* Swap everything a vehicle owns: the numbers the solver reads, where the
     struts sit, how big the wheels are, and the shell itself. */
  window.__setVehicle=function(i){
    var V=VEHICLES[i]; VEH=i;
    MASS=V.mass; TRACK=V.track; WHEELBASE=V.wb; WHEEL_R=V.wheelR;
    SUS_REST=V.rest; SUS_MAX=V.susMax; SUS_MIN=V.susMin;
    SPRING_K=V.k; DAMP_BUMP=V.dBump; DAMP_REB=V.dReb;
    ARB_F=V.arbF; ARB_R=V.arbR;
    MAX_DRIVE=V.drive; MAX_BRAKE=V.brake; BRAKE_BIAS_F=V.biasF;
    DRIVE_F=V.dF; DRIVE_R=V.dR;
    MU_LAT_F=V.muF; MU_LAT_R=V.muR;
    H_ROLL=V.hRoll; H_PITCH=V.hPitch;
    Ibody.set(MASS/12*(1.05*1.05+V.L*V.L),
              MASS/12*(V.W*V.W+V.L*V.L),
              MASS/12*(V.W*V.W+1.05*1.05)*1.25);

    /* new wheels if the tyre changed size */
    var g=wheelGeos(V.wheelR,V.tyreW);
    for(var k=0;k<4;k++){
      var st=STRUT[k];
      st.wheel.geometry=g.tyre; st.sho.geometry=g.sho;
      st.lugA.geometry=g.lug;   st.lugB.geometry=g.lug2;
      st.rim.geometry=g.rim;    st.hubc.geometry=g.hub;
      var mx=(k%2===0?-1:1)*V.track/2, mz=(k<2?1:-1)*V.wb/2;
      st.grp.position.set(mx,-0.06,mz);
      corners[k].mount.set(mx,-0.06,mz);
      corners[k].len=V.rest; corners[k].prevLen=V.rest;
    }

    /* new shell */
    while(bodyG.children.length) bodyG.remove(bodyG.children[0]);
    bodyG.position.y=V.bodyY;
    paint.color.copy(sc(V.paint));
    paint.emissive.copy(new THREE.Color(V.paint).convertSRGBToLinear()).multiplyScalar(0.36);
    second.color.copy(sc(V.second));
    SHELLS[V.id](V);
  };
})();""")

# `second` is the car's own contrast colour, alongside the cream roof
sub("""  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});""",
    """  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});
  var second = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
