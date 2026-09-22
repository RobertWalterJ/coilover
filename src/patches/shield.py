# -*- coding: utf-8 -*-
"""Pike Narrows: the Canadian Shield, north of cottage country.

Stage one, the ground itself. What makes the Shield the Shield, and none of it
is the desert with green paint on:

ROLLING, NOT ALPINE. Two hundred metre wavelengths and about thirty metres of
relief. You are never on a mountain and never on a plain; you are always going
over something.

GRANITE WHALEBACKS. Ridged noise, thresholded so only the strong ridges
survive, which gives scattered bald domes standing above the bush rather than a
mountain range. These are the bit you climb.

WATER AT THE BOTTOM OF EVERYTHING. On the Shield the low ground is always a
lake. Five of them, elongated and rotated along the ice flow with noise-ragged
shorelines, all at the same level, because they are all the same water table.
The ground falls to a bed beneath them.

MUSKEG in the hollows: flat, wet, and the low grip surface of this map. It is
where you get stuck, which is the thing that makes the road worth finding.

AN ESKER. A long sinuous gravel ridge left by a meltwater river under the ice.
It is the only naturally flat fast line on a map like this and every road in
Northern Ontario that is straight for more than a kilometre is on one.

A LOGGING ROAD that wanders, with a spur, cut into the hills: the road takes
the broad shape of the land and ignores the chop, which is what grading does.

Four new surfaces. Grass has more rolling drag than sand and less grip than
rock. Granite is the best grip on the map. Muskeg is deliberately awful: 0.74
of grip and three times the rolling drag of hard sand, so a bog is a decision
rather than a texture. Gravel sits between them and throws a lot of dust.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ======================================================== 1. the surfaces
sub("  {n:'sidewalk',  muF:1.10, muR:1.02, ap:0.108, c:1.68, roll:22, dust:0.30, sink:0.000}\n];",
    "  {n:'sidewalk',  muF:1.10, muR:1.02, ap:0.108, c:1.68, roll:22, dust:0.30, sink:0.000},\n"
    "  /* The Shield. Grass drags more than sand and grips less than rock;\n"
    "     granite is the best surface on the map; muskeg is deliberately awful,\n"
    "     so a bog is a decision and not a texture; gravel sits between and\n"
    "     throws the most dust of anything here. */\n"
    "  {n:'grass',     muF:1.02, muR:0.94, ap:0.158, c:1.48, roll:27, dust:0.75, sink:0.022},\n"
    "  {n:'granite',   muF:1.16, muR:1.08, ap:0.106, c:1.72, roll:13, dust:0.12, sink:0.000},\n"
    "  {n:'muskeg',    muF:0.74, muR:0.66, ap:0.235, c:1.26, roll:56, dust:1.70, sink:0.080},\n"
    "  {n:'gravel',    muF:1.00, muR:0.92, ap:0.146, c:1.50, roll:19, dust:1.55, sink:0.014},\n"
    "  {n:'water',     muF:0.58, muR:0.52, ap:0.260, c:1.20, roll:96, dust:0.90, sink:0.120}\n];")

# ======================================================== 2. the ground
sub("function baseH(x,z){",
"""/* ---------------------------------------------------------------- Shield
   Pike Narrows. Every lake on the map is at the same level because they share
   a water table, which is why Shield country reads as one landscape rather
   than a set of separate basins. */
var SH_WATER=-6.0;

/* Five lakes, elongated and rotated roughly along the ice flow, with the
   shoreline pushed about by noise so none of them reads as a crater.
   Returns a normalised distance: under 1 is water. */
var SH_LAKES=[[-146,118, 78,46, 0.55],[132,-104, 88,50,-0.42],
              [-40,-176, 62,42, 1.15],[178,150, 54,36, 0.20],
              [-6, 22, 40,28, -0.9]];
function shLakeD(x,z){
  var best=9;
  for(var i=0;i<SH_LAKES.length;i++){
    var a=SH_LAKES[i], dx=x-a[0], dz=z-a[1];
    var cs=Math.cos(a[4]), sn=Math.sin(a[4]);
    var u=(dx*cs+dz*sn)/a[2], v=(-dx*sn+dz*cs)/a[3];
    var r=Math.sqrt(u*u+v*v);
    r += (vnoise(x*0.019+i*13.7, z*0.019-i*7.1)-0.5)*0.34;   /* ragged shore */
    if(r<best) best=r;
  }
  return best;
}
/* Muskeg fills the hollows between the rock. Two conditions, both required:
   low ground, and a slow noise field, so bogs are patches and not a fringe
   around every lake. */
function shBog(x,z){
  var f=vnoise(x*0.0116-8.4, z*0.0116+19.2);
  return sstep(0.56,0.74,f);
}
/* The bald domes. Ridged noise thresholded hard, so only the strong ridges
   survive and you get scattered whalebacks instead of a mountain range. */
function shDome(x,z){
  var rn=1-Math.abs(vnoise(x*0.0088-21.4, z*0.0088+6.2)*2-1);
  return Math.max(0,(rn-0.44)/0.56);
}
/* An esker: the sinuous gravel ridge a meltwater river left under the ice.
   The only naturally flat fast line on a map like this. */
function shEskerD(x,z){
  return Math.abs(x - (Math.sin(z*0.0094+0.6)*104 + Math.sin(z*0.0037-1.1)*46 + 52));
}
/* The logging road wanders north to south with one spur running east. */
function shRoadD(x,z){
  var a=Math.abs(x - (Math.sin(z*0.0125)*86 + Math.sin(z*0.0041+1.2)*54 - 34));
  var b=Math.abs(z - (Math.sin(x*0.0102+2.1)*66 + 108));
  return Math.min(a,b);
}
function baseHShield(x,z){
  /* the broad shape, which the road and the esker will follow */
  var broad = fbm(x*0.0043, z*0.0043, 2)*30 - 15;
  var h = broad;
  h += fbm(x*0.0140, z*0.0140, 3)*7.4 - 3.7;         /* the chop you feel */
  h += (vnoise(x*0.052,z*0.052)-0.5)*0.24;           /* surface grain */

  h += shDome(x,z)*shDome(x,z)*24;                   /* granite whalebacks */

  /* muskeg is flat and low: the hollows fill in and stay filled */
  var mk=shBog(x,z);
  h = h*(1-mk) + Math.min(h,-1.8)*mk;

  /* the esker rides over everything, because it was laid on top of it */
  var ek=1-sstep(9,34,shEskerD(x,z));
  h = h*(1-ek*0.55) + (broad+9.5)*(ek*0.55);
  h += ek*ek*3.2;

  /* the road takes the broad shape and ignores the chop, which is grading */
  var rd=1-sstep(5.6,13.0,shRoadD(x,z));
  h = h*(1-rd) + (broad-0.8)*rd;

  /* lakes: the ground falls away to a bed under the water */
  var ld=shLakeD(x,z);
  if(ld<1.22){
    var t=1-sstep(0.98,1.22,ld);
    h = h*(1-t) + (SH_WATER-3.0-7.0*t)*t;
  }

  /* and a ring of higher bush closing the map in, rather than a basin wall */
  var r=Math.hypot(x,z);
  if(r>210) h += Math.min(58, Math.pow((r-210)*0.049,2.1)*15);
  return h;
}

function baseH(x,z){""")

# ======================================================== 3. wire it up
sub("function height(x,z){\n  if(MAP===1) return baseHCity(x,z);",
    "function height(x,z){\n  if(MAP===1) return baseHCity(x,z);\n  if(MAP===2) return baseHShield(x,z);")

sub("""  {id:'city',  name:'Vantage Hill', kind:'City and pan', unlock:12000, h:baseHCity, start:[0,-32,0.0]}
];""",
"""  {id:'city',  name:'Vantage Hill', kind:'City and pan', unlock:12000, h:baseHCity, start:[0,-32,0.0]},
  {id:'shield',name:'Pike Narrows',  kind:'Shield, bog and bush', unlock:26000,
   h:baseHShield, start:[-34,150,0.0]}
];""")

sub("""function surfaceAt(x,z,slope){
  if(MAP===1){""",
"""function surfaceAt(x,z,slope){
  if(MAP===2){
    if(shLakeD(x,z)<1.00) return 11;                  /* in the water */
    if(shRoadD(x,z)<5.6)  return 10;                  /* the logging road */
    if(shEskerD(x,z)<11)  return 10;                  /* and the esker is gravel */
    if(shBog(x,z)>0.58)   return 9;                   /* muskeg */
    if(slope>0.26 || shDome(x,z)>0.30) return 8;      /* bare granite */
    return 7;                                          /* grass and moss */
  }
  if(MAP===1){""")

# ======================================================== 4. how it looks
sub("""    }else{
    c.copy(cLow).lerp(cMid, sstep(-11,-2,my));""",
"""    }else if(MAP===2){
      /* Shield colour is decided by what the ground IS, not by its height:
         moss and grass everywhere, granite wherever the rock is bare or the
         slope is steep, rust and olive in the muskeg, pale gravel on the road
         and the esker, and a dark green water that reads as deep. */
      c.setHex(0x5c7a44).convertSRGBToLinear();                  /* grass */
      c.lerp(new THREE.Color(0x3f5c33).convertSRGBToLinear(),
             sstep(0.35,0.72,vnoise(mx*0.031+4.1,mz*0.031-2.6))); /* bush shade */
      c.lerp(new THREE.Color(0x8e8378).convertSRGBToLinear(),
             Math.max(sstep(0.16,0.42,slope), sstep(0.10,0.52,shDome(mx,mz))));
      c.lerp(new THREE.Color(0x6d6647).convertSRGBToLinear(), shBog(mx,mz)*0.9);
      var rdw=Math.max(1-sstep(4.4,6.6,shRoadD(mx,mz)), 1-sstep(8,12,shEskerD(mx,mz)));
      c.lerp(new THREE.Color(0xa89a80).convertSRGBToLinear(), rdw);
      var lw=1-sstep(0.94,1.02,shLakeD(mx,mz));
      c.lerp(new THREE.Color(0x2b4a4e).convertSRGBToLinear(), lw);
    }else{
    c.copy(cLow).lerp(cMid, sstep(-11,-2,my));""")

# the two per face weights that drive the photographic texture blend
sub("    var lkw=(MAP===1?panMask(mx,mz):lakeMask(mx,mz));\n"
    "    var rkw=(MAP===1? sstep(BUILD,BUILD+1.3,streetD(mx,mz)) : sstep(0.16,0.44,slope));",
    "    var lkw=(MAP===1?panMask(mx,mz):(MAP===2?(1-sstep(0.94,1.06,shLakeD(mx,mz))):lakeMask(mx,mz)));\n"
    "    var rkw=(MAP===1? sstep(BUILD,BUILD+1.3,streetD(mx,mz))\n"
    "           : (MAP===2? Math.max(sstep(0.16,0.44,slope), sstep(0.10,0.52,shDome(mx,mz)))\n"
    "           : sstep(0.16,0.44,slope)));")

# ======================================================== 5. its own scenery group
sub("var G_CITY=new THREE.Group(); G_CITY.visible=false; scene.add(G_CITY);",
    "var G_CITY=new THREE.Group(); G_CITY.visible=false; scene.add(G_CITY);\n"
    "var G_SHIELD=new THREE.Group(); G_SHIELD.visible=false; scene.add(G_SHIELD);")

sub("""  G_DESERT.visible=(i===0);
  G_CITY.visible=(i===1);
  STYLE_U.uFacade.value=(i===1?1.0:0.0);
  STYLE_U.uTexSteep.value=(i===1?PHOTO_METAL:PHOTO_ROCK);""",
"""  G_DESERT.visible=(i===0);
  G_CITY.visible=(i===1);
  G_SHIELD.visible=(i===2);
  STYLE_U.uFacade.value=(i===1?1.0:0.0);
  STYLE_U.uTexSteep.value=(i===1?PHOTO_METAL:PHOTO_ROCK);""")

sub("  if(i===1) buildCityProps();",
    "  if(i===1) buildCityProps();\n  if(i===2) buildShieldProps();")

# ======================================================== 6. its own scoring
sub("""  {id:'core', map:1, name:'Downtown Loop', t:function(x,z){ return Math.hypot(x-30,z+34)<105; }}
];""",
"""  {id:'core', map:1, name:'Downtown Loop', t:function(x,z){ return Math.hypot(x-30,z+34)<105; }},
  /* Pike Narrows */
  {id:'haul', map:2, name:'The Haul Road',  t:function(x,z){ return shRoadD(x,z)<9; }},
  {id:'esk',  map:2, name:'Esker Run',      t:function(x,z){ return shEskerD(x,z)<16; }},
  {id:'bog',  map:2, name:'Muskeg Flats',   t:function(x,z){ return shBog(x,z)>0.58; }},
  {id:'dome', map:2, name:'Bald Granite',   t:function(x,z){ return shDome(x,z)>0.34; }}
];""")

sub("""  {id:'crest',   map:1, name:'Crest jump',pts:560}
];""",
"""  {id:'crest',   map:1, name:'Crest jump',pts:560},
  {id:'domeup',  map:2, name:'Dome climb',  pts:620},
  {id:'bogrun',  map:2, name:'Bog crossing',pts:680},
  {id:'shore',   map:2, name:'Shoreline run',pts:540}
];""")

sub("""    if(S.grounded<2) FT.crestDone=0;
  }""",
"""    if(S.grounded<2) FT.crestDone=0;
  }
  /* ---- Pike Narrows ---- */
  if(MAP===2){
    /* over the top of a bald dome, still moving */
    if(shDome(S.p.x,S.p.z)>0.72 && sp>11 && S.grounded>=3 && !FT.domeDone){
      FT.domeDone=1; featDone('domeup');
    }
    if(shDome(S.p.x,S.p.z)<0.40) FT.domeDone=0;
    /* across the muskeg without bogging down */
    if(shBog(S.p.x,S.p.z)>0.58 && sp>7){
      FT.bogT=(FT.bogT||0)+dt;
      if(FT.bogT>5.2){ featDone('bogrun'); FT.bogT=-99; }
    }else if(shBog(S.p.x,S.p.z)<0.4) FT.bogT=0;
    /* a long run along a shoreline, close in, without going swimming */
    var ld2=shLakeD(S.p.x,S.p.z);
    if(ld2>1.00 && ld2<1.22 && sp>13){
      FT.shoreT=(FT.shoreT||0)+dt;
      if(FT.shoreT>6.0){ featDone('shore'); FT.shoreT=-99; }
    }else if(ld2>1.34 || ld2<0.98) FT.shoreT=0;
  }""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
