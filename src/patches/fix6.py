# -*- coding: utf-8 -*-
"""Three things you asked for.

THE GAPS. Confirmed exactly. The cabin spanned z minus 0.83 to plus 0.79 and
the rear body started at minus 0.93, so there was a 10 cm empty slot between
them, and their heights differed by 6 cm as well, so there was a step too. Only
visible from the side, which is what you saw. The rear body now joins the cabin
and matches its height, and the roof runs the full length instead of stopping
2 cm before the rear body begins, which also gives the truck a light shape from
behind for the first time. The spare wheel on the back door goes: it was 44
percent of the rear face and it read as a bullseye rather than as a vehicle.
The whole body drops 18 cm relative to the wheels, because 90 cm of ground
clearance under a 4.9 m truck read as a table on castors.

TURNING AT SPEED. The steering limiter gave you extra lock in proportion to how
sideways the truck already was. That is right for CATCHING a slide and wrong
for starting one, because it fed back on itself: turn, get sideways, get more
lock, get more sideways. Now the bonus only applies when you are steering
against the slide.

SURFACES. Four of them, chosen from the same functions that paint the ground so
what you see is what you get: hard sand, deep sand, rock, and the dried
riverbed. Each has its own grip, slip window, breakaway sharpness, rolling drag
and dust. They cross fade over about a fifth of a second so crossing a boundary
does not snap.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================================ 1. the body
sub("""  function add(mesh,x,y,z,cast){
    mesh.position.set(x,y,z);
    if(cast!==false) mesh.castShadow=true;
    truck.add(mesh); return mesh;
  }""",
"""  /* The body hangs in its own group so it can sit lower over the wheels
     without moving the strut mounts. */
  var bodyG=new THREE.Group(); bodyG.position.y=-0.18; truck.add(bodyG);
  function add(mesh,x,y,z,cast){
    mesh.position.set(x,y,z);
    if(cast!==false) mesh.castShadow=true;
    bodyG.add(mesh); return mesh;
  }""")

sub("""  /* ---- rear body and door ---- */
  box(W,0.86,1.30, paint, 0, 0.88,-1.58);
  box(1.60,0.46,0.08, glass, 0, 1.06,-2.22, false);
  box(0.30,0.16,0.06, tailM,-0.66, 0.52,-2.24, false);
  box(0.30,0.16,0.06, tailM, 0.66, 0.52,-2.24, false);
  box(1.90,0.20,0.30, trim, 0,-0.08,-2.24);           /* rear bar */""",
"""  /* ---- rear body ----
     Same height as the cabin and overlapping it, so the two read as one
     volume rather than as two boxes with a slot between them. */
  box(W,0.92,1.44, paint, 0, 0.91,-1.51);
  box(1.60,0.40,0.08, glass, 0, 1.14,-2.22, false);
  /* a cream tailgate, which is the light shape the chase camera needs */
  box(1.62,0.44,0.07, roofM, 0, 0.72,-2.235, false);
  box(0.26,0.24,0.06, tailM,-0.70, 0.70,-2.26, false);
  box(0.26,0.24,0.06, tailM, 0.70, 0.70,-2.26, false);
  box(1.90,0.20,0.30, trim, 0,-0.08,-2.24);           /* rear bar */""")

sub("  box(1.84,0.12,1.74, roofM, 0, 1.43,-0.04);          /* white roof */",
    "  box(1.90,0.12,3.16, roofM, 0, 1.43,-0.62);          /* full length white roof */")

# the rack sat over a roof that was not there; move it back onto the roof
sub("""  box(1.86,0.07,1.80, trim, 0, 1.54,-0.90, false);
  [[-0.86,-0.02],[0.86,-0.02],[-0.86,-1.76],[0.86,-1.76]].forEach(function(pp){
    box(0.07,0.22,0.07, trim, pp[0],1.60,pp[1], false);
  });
  box(1.70,0.10,1.66, trim, 0, 1.70,-0.90);
  box(0.90,0.26,0.60, canvasM, -0.30,1.88,-1.20);
  box(0.34,0.44,0.26, trim, 0.56,1.97,-1.34);""",
"""  [[-0.80,-1.90],[0.80,-1.90]].forEach(function(pp){
    box(0.06,0.10,0.06, trim, pp[0],1.54,pp[1], false);
  });
  box(1.70,0.08,1.50, trim, 0, 1.58,-1.28);
  box(0.86,0.22,0.52, canvasM, -0.28,1.72,-1.30);""")

# the spare was the strongest contrast on the whole vehicle and meant nothing
sub("""  /* ---- spare on the back door ---- */
  var spare=new THREE.Mesh(new THREE.CylinderGeometry(0.50,0.50,0.32,14),tyreM);
  spare.rotation.x=Math.PI/2; add(spare,0.16,0.72,-2.36);
  var spareR=new THREE.Mesh(new THREE.CylinderGeometry(0.24,0.24,0.34,9),rimM);
  spareR.rotation.x=Math.PI/2; add(spareR,0.16,0.72,-2.36,false);
""", "")

# ================================================================ 2. steering
sub("""  var beta=Math.atan2(vbR,Math.abs(vbF)+1.0);
  var dmax=0.17 + 0.56/(1+Math.pow(speed/11.0,1.6)) + Math.min(0.30,Math.abs(beta));""",
"""  var beta=Math.atan2(vbR,Math.abs(vbF)+1.0);
  /* Extra lock only when you are steering AGAINST the slide. Granting it
     unconditionally fed back on itself and made fast turns feel loose. */
  var counter=(S.steer*beta<0)? Math.min(0.30,Math.abs(beta)) : 0;
  var dmax=0.17 + 0.56/(1+Math.pow(speed/11.0,1.6)) + counter;""")
sub("""  var steerAng=-S.steer*(0.17+0.56/(1+Math.pow(speed/11.0,1.6))+Math.min(0.30,Math.abs(beta2)));""",
"""  var counter2=(S.steer*beta2<0)? Math.min(0.30,Math.abs(beta2)) : 0;
  var steerAng=-S.steer*(0.17+0.56/(1+Math.pow(speed/11.0,1.6))+counter2);""")

# ================================================================ 3. surfaces
sub("""var MU_HAND=0.34, HAND_C=1.30, HAND_B=Math.tan(Math.PI/(2*HAND_C))/0.436;""",
"""var MU_HAND=0.34, HAND_C=1.30, HAND_B=Math.tan(Math.PI/(2*HAND_C))/0.436;

/* Four ground surfaces, read from the same functions that paint the terrain,
   so what you see is what you feel. B is derived so the curve peaks at ap. */
var SURF=[
  {n:'hard sand', muF:1.00, muR:0.92, ap:0.140, c:1.55, roll:18, dust:1.00, sink:0.018},
  {n:'deep sand', muF:0.86, muR:0.78, ap:0.205, c:1.34, roll:38, dust:3.10, sink:0.055},
  {n:'rock',      muF:1.08, muR:1.02, ap:0.118, c:1.64, roll:26, dust:0.35, sink:0.006},
  {n:'riverbed',  muF:1.18, muR:1.08, ap:0.102, c:1.70, roll:11, dust:0.55, sink:0.000}
];
for(var _s=0;_s<SURF.length;_s++) SURF[_s].b=Math.tan(Math.PI/(2*SURF[_s].c))/SURF[_s].ap;

function surfaceAt(x,z,slope){
  if(lakeMask(x,z)>0.55) return 3;          /* the dried riverbed */
  if(slope>0.30) return 2;                  /* anything steep is rock */
  if(vnoise(x*0.0125+31.7,z*0.0125-8.3)>0.60) return 1;   /* drifts of soft sand */
  return 0;
}""")

sub("""      len:SUS_REST, prevLen:SUS_REST, load:0, contact:false, spin:0, slip:0,
      alphaF:0, locked:false,""",
"""      len:SUS_REST, prevLen:SUS_REST, load:0, contact:false, spin:0, slip:0,
      alphaF:0, locked:false, surf:0,
      muF:1.00, muR:0.92, ap:0.140, tc:1.55, tb:11.43, roll:18, dustK:1.0,""")

sub("""    var hb=c2.front?0:S.hand;
    var muBase=c2.front?MU_LAT_F:MU_LAT_R;
    var muL=muBase+(MU_HAND-muBase)*hb;
    var Bc=hb>0.35?HAND_B:TYRE_B, Cc=hb>0.35?HAND_C:TYRE_C;""",
"""    /* blend this corner toward the surface it is actually on */
    var sf=SURF[surfaceAt(c2.cp.x,c2.cp.z,1-Math.abs(c2.nrm.y))];
    var kS=Math.min(1,dt*5.0);
    c2.surf=sf;
    c2.muF+=(sf.muF-c2.muF)*kS; c2.muR+=(sf.muR-c2.muR)*kS;
    c2.ap+=(sf.ap-c2.ap)*kS;   c2.tc+=(sf.c-c2.tc)*kS;
    c2.tb+=(sf.b-c2.tb)*kS;    c2.roll+=(sf.roll-c2.roll)*kS;
    c2.dustK+=(sf.dust-c2.dustK)*kS;

    var hb=c2.front?0:S.hand;
    var muBase=c2.front?c2.muF:c2.muR;
    var muL=muBase+(MU_HAND-muBase)*hb;
    var Bc=hb>0.35?HAND_B:c2.tb, Cc=hb>0.35?HAND_C:c2.tc;""")

sub("    Flong -= vf*18;                                    /* rolling resistance */",
    "    Flong -= vf*c2.roll;                               /* surface rolling drag */")

sub("""    if(c.contact && (speed>9 || c.slip>3.0) && Math.random()<0.17){""",
    """    if(c.contact && (speed>9 || c.slip>3.0) && Math.random()<0.17*c.dustK){""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
