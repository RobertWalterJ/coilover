# -*- coding: utf-8 -*-
"""Two worlds, and the machinery to swap between them.

THE CITY. Hills you crest and drop off, in a grid, which is the San Francisco
part, and a big flat pan on the water side for exactly the drifts you asked
for. The blocks are raised plateaus in the heightfield itself, not decoration,
so the streets are real canyons you drive along and the physics agrees with
what you can see. Buildings stand on those plateaus. Streets follow the hills
rather than being cut into them, which is what makes a grid on hills fun to
drive: you go over a crest and the road disappears under the bonnet.

The pan is a separate surface with a little less lateral grip than the desert
riverbed, because maximum grip is the enemy of a long drift. It is 190 metres
across with nothing in it.

Street lights along every block edge, which matters more than it sounds: the
light pool system already picks up the nearest lit things, so at dusk the city
is a grid of warm pools in a blue field. That is the reference look arriving
for free from a subject that actually has lights in it, rather than being
chased across a desert that does not.

HOW SWAPPING WORKS. The terrain is one mesh built from an analytic height
function, so a map is really just a different height function plus a different
set of props. `height()` dispatches on the current map, the terrain geometry is
rebuilt in place, and each map's props live in their own group that is simply
shown or hidden. Nothing is disposed and rebuilt, so switching is instant.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# =========================================================== the city terrain
sub("""var PAD_Y=0;
function height(x,z){
  var h=baseH(x,z);
  var sp=disc(x,z,0,0,13,26);                        /* the pit pad */
  return h*(1-sp)+PAD_Y*sp;
}""",
"""/* ================= the city ================= */
var CITY_PITCH=54, CITY_ST=16, BLOCK_H=5.6;

/* how far inside a block you are, 0 at the kerb and 1 well in */
function cityBlock(x,z){
  var P=CITY_PITCH, half=(P-CITY_ST)*0.5;
  var bx=Math.abs((((x+P*0.5)%P)+P)%P - P*0.5);
  var bz=Math.abs((((z+P*0.5)%P)+P)%P - P*0.5);
  return sstep(0,3.4,Math.min(half-bx,half-bz));
}
/* the flat pan on the water side: big, empty, and yours to slide on */
function panMask(x,z){
  var d=Math.max(Math.abs(x-104)/98, Math.abs(z-118)/74);
  return 1-sstep(0.84,1.0,d);
}
function baseHCity(x,z){
  /* the hills. Big and smooth, so a grid laid over them gives real crests. */
  var h = fbm(x*0.0050+40.5, z*0.0050-25.5, 3)*54 - 25;
  h += fbm(x*0.0190+7.1, z*0.0190+3.3, 2)*4.4 - 2.2;
  h += (vnoise(x*0.061,z*0.061)-0.5)*0.22;

  var pan=panMask(x,z);
  h = h*(1-pan) + (-7.5)*pan;                        /* dead flat, for drifts */

  /* the blocks are in the ground, so the streets are canyons */
  h += cityBlock(x,z)*(1-pan)*BLOCK_H;

  var r=Math.hypot(x,z);
  if(r>RIM) h += Math.min(72,Math.pow((r-RIM)*0.052,2.2)*13);
  return h;
}

/* ================= maps ================= */
var MAPS=[
  {id:'basin', name:'Ochre Basin', kind:'High desert', h:baseH,     start:[0,0,0.4]},
  {id:'city',  name:'Vantage Hill', kind:'City and pan', h:baseHCity, start:[-8,-40,1.2]}
];
var MAP=0;

var PAD_Y=0;
function height(x,z){
  if(MAP===1) return baseHCity(x,z);
  var h=baseH(x,z);
  var sp=disc(x,z,0,0,13,26);                        /* the pit pad */
  return h*(1-sp)+PAD_Y*sp;
}""")

# ------------------------------------------------- a surface you can slide on
sub("""  {n:'riverbed',  muF:1.18, muR:1.08, ap:0.102, c:1.70, roll:11, dust:0.55, sink:0.000}
];""",
"""  {n:'riverbed',  muF:1.18, muR:1.08, ap:0.102, c:1.70, roll:11, dust:0.55, sink:0.000},
  /* Asphalt, and then the pan. Maximum grip is the enemy of a long drift, so
     the pan gives a little away laterally and lets go smoothly. */
  {n:'asphalt',   muF:1.22, muR:1.14, ap:0.096, c:1.78, roll:9,  dust:0.20, sink:0.000},
  {n:'pan',       muF:0.99, muR:0.90, ap:0.150, c:1.42, roll:7,  dust:0.45, sink:0.000}
];""")

sub("""function surfaceAt(x,z,slope){
  if(lakeMask(x,z)>0.55) return 3;          /* the dried riverbed */""",
"""function surfaceAt(x,z,slope){
  if(MAP===1){
    if(panMask(x,z)>0.55) return 5;         /* the drift pan */
    if(cityBlock(x,z)>0.5) return 2;        /* up on a block, call it rock */
    return 4;                               /* the streets */
  }
  if(lakeMask(x,z)>0.55) return 3;          /* the dried riverbed */""")

# ============================================== terrain becomes rebuildable
sub("""var terrainMat;
/* texels of about 7.5 cm, so 128 of them span roughly 12 m of world */
GRAIN_TEX=grainTex(128,7,0.55,6);
var PAPER_TEX=grainTex(256,44,0.30,5);
(function(){
  var N=Math.round(WORLD/GRID), V=N+1;""",
"""var terrainMat, terrainMesh=null;
/* texels of about 7.5 cm, so 128 of them span roughly 12 m of world */
GRAIN_TEX=grainTex(128,7,0.55,6);
var PAPER_TEX=grainTex(256,44,0.30,5);
function buildTerrain(){
  var N=Math.round(WORLD/GRID), V=N+1;""")

sub("""  var mesh=new THREE.Mesh(g2,terrainMat);
  /* Dunes do not cast. A nine degree sun already bands them through N dot L
     for free, and keeping the sheet out of the shadow pass pays for the rest. */
  mesh.castShadow=false; mesh.receiveShadow=true;
  scene.add(mesh);
})();""",
"""  if(terrainMesh){
    terrainMesh.geometry.dispose();
    terrainMesh.geometry=g2;
  }else{
    terrainMesh=new THREE.Mesh(g2,terrainMat);
    /* Dunes do not cast. A nine degree sun already bands them through N dot L
       for free, and keeping the sheet out of the shadow pass pays for the rest. */
    terrainMesh.castShadow=false; terrainMesh.receiveShadow=true;
    scene.add(terrainMesh);
  }
}
buildTerrain();""")

# the city needs its own ground colours
sub("""    c.copy(cLow).lerp(cMid, sstep(-11,-2,my));
    c.lerp(cHigh, sstep(1,13,my));
    c.lerp(cPlaya, lakeMask(mx,mz));
    c.lerp(cRock, sstep(0.15,0.40,slope));""",
"""    if(MAP===1){
      /* street, kerb, block top, and the pan */
      var onB=cityBlock(mx,mz), onP=panMask(mx,mz);
      c.setHex(0x3c3a46).convertSRGBToLinear();               /* asphalt */
      var cb=new THREE.Color(0x6d6456).convertSRGBToLinear(); /* block top */
      var cg=new THREE.Color(0x4c5c46).convertSRGBToLinear(); /* a bit of green */
      var mix=hash2(Math.floor(mx/CITY_PITCH)*3.1,Math.floor(mz/CITY_PITCH)*7.7);
      c.lerp(mix>0.62?cg:cb, sstep(0.20,0.72,onB));
      c.lerp(new THREE.Color(0x8b8378).convertSRGBToLinear(), onP);
      c.lerp(cRock, sstep(0.30,0.62,slope));
    }else{
    c.copy(cLow).lerp(cMid, sstep(-11,-2,my));
    c.lerp(cHigh, sstep(1,13,my));
    c.lerp(cPlaya, lakeMask(mx,mz));
    c.lerp(cRock, sstep(0.15,0.40,slope));
    }""")

sub("""    var lkw=lakeMask(mx,mz), rkw=sstep(0.16,0.44,slope);""",
    """    var lkw=(MAP===1?panMask(mx,mz):lakeMask(mx,mz)), rkw=sstep(0.16,0.44,slope);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
