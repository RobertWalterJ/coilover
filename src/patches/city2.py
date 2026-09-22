# -*- coding: utf-8 -*-
"""The city, rebuilt on a different idea.

The old one put isolated boxes in the middle of 31 m plots and hoped. This one
starts from the street cross section and the block as a solid mass, which is
what a city actually is.

THE CROSS SECTION. Street centrelines on a 96 by 64 m lattice, which is roughly
Toronto's short block face. Across a street, from the middle out: 13 m of
carriageway, a 0.15 m kerb step, 3.5 m of sidewalk, then the building line.
That is a 20 m right of way, which is Ontario's two chain survey standard and
within a metre of San Francisco's 25 vara street. One default serves both.

THE BLOCK IS SOLID. Each block is divided into parcels along its frontage, and
each parcel is a mass rising from the sidewalk to its own height. That mass is
in the height function, so the buildings are genuinely solid: you cannot drive
through them any more, and the facade you see is the exact surface the wheels
collide with. It also means the street wall is continuous by construction,
because neighbouring parcels share their edge. A street wall is cheaper than
freestanding boxes, not dearer.

GRADED, NOT DRAPED. The road surface is the terrain sampled only at the
intersections and interpolated between them, so every street segment is a plane
and every junction is a landing. That is how a graded street is actually
engineered, it removes street scale noise entirely, and on a hill it produces
the stepped roofline that reads as San Francisco without anyone authoring it.

Parcel heights come from a downtown field rather than pure noise, so there is a
core that falls away to low rise, which is what makes a skyline.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ===================================================== the new city heightfield
old_start = s.index("/* ================= the city ================= */")
old_end   = s.index("/* ================= maps ================= */")
s = s[:old_start] + """/* ================= the city ================= */
/* A 20 m right of way: 13 m of carriageway, a kerb, 3.5 m of sidewalk. That is
   Ontario's two chain road allowance and within a metre of a 25 vara San
   Francisco street, so one section serves both references. */
var PX=96, PZ=64;                 /* street centreline spacing, x and z */
var CARR=6.5, KERB=0.16, SIDE=3.5;
var BUILD=CARR+SIDE;              /* the building line, 10 m from the centre */

/* the hills, with nothing at street scale */
function cityTerr(x,z){
  var h = vnoise(x*0.0038+40.5, z*0.0038-25.5)*48 - 21;
  h += vnoise(x*0.0091+11.2, z*0.0091-4.4)*15 - 7.5;
  return h;
}
/* The road surface is the terrain sampled at the intersections only, then
   interpolated. Every segment becomes a plane and every junction a landing,
   which is how a graded street is built and why they feel right to drive. */
function roadH(x,z){
  var fx=x/PX, fz=z/PZ;
  var i=Math.floor(fx), j=Math.floor(fz);
  var tx=fx-i, tz=fz-j;
  tx=tx*tx*(3-2*tx); tz=tz*tz*(3-2*tz);
  var a=cityTerr(i*PX,j*PZ),      b=cityTerr((i+1)*PX,j*PZ);
  var c=cityTerr(i*PX,(j+1)*PZ),  d=cityTerr((i+1)*PX,(j+1)*PZ);
  return (a+(b-a)*tx)*(1-tz) + (c+(d-c)*tx)*tz;
}
/* distance from the nearest street centreline, in each axis and combined */
function streetD(x,z){
  var du=Math.abs((((x+PX*0.5)%PX)+PX)%PX - PX*0.5);
  var dv=Math.abs((((z+PZ*0.5)%PZ)+PZ)%PZ - PZ*0.5);
  return Math.min(du,dv);
}
/* the flat pan on the water side, which is the Portlands: lake fill, huge
   parcels, no traffic, and honestly the flattest pavement in any city */
function panMask(x,z){
  var d=Math.max(Math.abs(x-104)/98, Math.abs(z-132)/62);
  return 1-sstep(0.84,1.0,d);
}
/* Parcels. A block is cut into a few along its frontage so the street wall
   steps, and each parcel is a solid mass. Height comes from a downtown field
   so there is a core that falls away, rather than noise. */
var PARC_X=32, PARC_Z=32;
function parcelH(x,z){
  var bi=Math.floor((x+PX*0.5)/PX), bj=Math.floor((z+PZ*0.5)/PZ);
  var pi=Math.floor(x/PARC_X), pj=Math.floor(z/PARC_Z);
  var core=1-sstep(40,210,Math.hypot(x-30,z+34));      /* the downtown field */
  var hs=hash2(pi*7.31+bi*0.7, pj*3.97-bj*1.3);
  var base=6 + hs*10;                                   /* low rise everywhere */
  return base + core*core*(14 + hs*54);                 /* rising to a core */
}
function baseHCity(x,z){
  var road=roadH(x,z);
  var pan=panMask(x,z);
  if(pan>0.5) return -7.5;

  var d=streetD(x,z);
  var h=road;
  /* kerb, then sidewalk */
  h += KERB*sstep(CARR-0.35,CARR+0.35,d);
  /* then the built mass, over a 1.1 m shoulder so it is a wall and not a cliff
     the solver has to resolve in one step */
  h += parcelH(x,z)*sstep(BUILD,BUILD+1.1,d);

  h=h*(1-pan) + (-7.5)*pan;
  var r=Math.hypot(x,z);
  if(r>RIM) h += Math.min(72,Math.pow((r-RIM)*0.052,2.2)*13);
  return h;
}

""" + s[old_end:]
n += 1

# --------------------------------------------------------------- surfaces
sub("""  if(MAP===1){
    if(panMask(x,z)>0.55) return 5;         /* the drift pan */
    if(cityBlock(x,z)>0.5) return 2;        /* up on a block, call it rock */
    return 4;                               /* the streets */
  }""",
"""  if(MAP===1){
    if(panMask(x,z)>0.55) return 5;         /* the pan, for sliding on */
    if(streetD(x,z)>CARR) return 6;         /* kerb and sidewalk */
    return 4;                               /* the carriageway */
  }""")
sub("""  {n:'pan',       muF:0.99, muR:0.90, ap:0.150, c:1.42, roll:7,  dust:0.45, sink:0.000}
];""",
"""  {n:'pan',       muF:0.99, muR:0.90, ap:0.150, c:1.42, roll:7,  dust:0.45, sink:0.000},
  {n:'sidewalk',  muF:1.10, muR:1.02, ap:0.108, c:1.68, roll:22, dust:0.30, sink:0.000}
];""")

# ------------------------------------------------- the city's ground colours
sub("""    if(MAP===1){
      /* street, kerb, block top, and the pan */
      var onB=cityBlock(mx,mz), onP=panMask(mx,mz);
      c.setHex(0x6e6c7a).convertSRGBToLinear();               /* asphalt */
      var cb=new THREE.Color(0x6d6456).convertSRGBToLinear(); /* block top */
      var cg=new THREE.Color(0x4c5c46).convertSRGBToLinear(); /* a bit of green */
      var mix=hash2(Math.floor(mx/CITY_PITCH)*3.1,Math.floor(mz/CITY_PITCH)*7.7);
      c.lerp(mix>0.62?cg:cb, sstep(0.20,0.72,onB));
      c.lerp(new THREE.Color(0x8b8378).convertSRGBToLinear(), onP);
      /* the block sides are steep by design, so sending them to rock colour
         turned every kerb into a black cliff. Concrete, not sandstone. */
      c.lerp(new THREE.Color(0x7d7568).convertSRGBToLinear(), sstep(0.34,0.70,slope));
    }else{""",
"""    if(MAP===1){
      var dS=streetD(mx,mz), onP=panMask(mx,mz);
      c.setHex(0x5f5d6b).convertSRGBToLinear();                 /* asphalt */
      /* Road markings, painted straight into the vertex colour. A dashed
         centreline and an edge line either side is the whole vocabulary and
         it does more for a road than any geometry would. */
      var du=Math.abs((((mx+PX*0.5)%PX)+PX)%PX - PX*0.5);
      var dv=Math.abs((((mz+PZ*0.5)%PZ)+PZ)%PZ - PZ*0.5);
      var onCarr=(dS<CARR);
      var dash=(Math.abs(((mz%9)+9)%9-4.5)<2.6);                /* along z streets */
      var dash2=(Math.abs(((mx%9)+9)%9-4.5)<2.6);
      var paint=0;
      if(onCarr){
        if(du<0.42 && dash) paint=1;                            /* centreline */
        if(dv<0.42 && dash2) paint=1;
        if(Math.abs(du-(CARR-0.7))<0.30 || Math.abs(dv-(CARR-0.7))<0.30) paint=1;
      }
      if(paint) c.setHex(0xcfc8ae).convertSRGBToLinear();
      /* sidewalk, then the facade above the building line */
      c.lerp(new THREE.Color(0x8d8a86).convertSRGBToLinear(), sstep(CARR-0.1,CARR+0.5,dS));
      c.lerp(new THREE.Color(0x8f8478).convertSRGBToLinear(), sstep(BUILD,BUILD+1.3,dS));
      c.lerp(new THREE.Color(0x8b8378).convertSRGBToLinear(), onP);
    }else{""")

sub("""    var lkw=(MAP===1?panMask(mx,mz):lakeMask(mx,mz)), rkw=sstep(0.16,0.44,slope);""",
"""    var lkw=(MAP===1?panMask(mx,mz):lakeMask(mx,mz));
    var rkw=(MAP===1? sstep(BUILD,BUILD+1.3,streetD(mx,mz)) : sstep(0.16,0.44,slope));""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
