# -*- coding: utf-8 -*-
"""First pass over game.html: a corrupted line, the em dash purge, and a
handful of physics and rendering corrections found on review."""
import io, sys

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0
missed = []

def sub(old, new):
    global s, n
    if old not in s:
        missed.append(old[:78].replace('\n', ' | '))
        return
    s = s.replace(old, new, 1); n += 1

# --- corrupted literal -------------------------------------------------
sub("var dustHead=0, C_DUST=new THREE.Color(0xe6c furthermore);",
    "var dustHead=0;")

# --- em dashes, in copy and in comments --------------------------------
sub("""  /* Coilover — one committed world: a desert basin at golden hour, flat-shaded,
     with a smoked-glass telemetry HUD over it. No theme swap; every colour is
     stated outright so the page holds on any host ground. */""",
"""  /* Coilover. One committed world: a desert basin at golden hour, flat shaded,
     with a smoked glass telemetry HUD over it. No theme swap; every colour is
     stated outright so the page holds on any host ground. */""")

sub("/* N/m — static sits near 0.60 */", "/* N/m, static sits near 0.60 */")
sub("/* dry lakebed — dead flat, the fast bit */",
    "/* dry lakebed, dead flat, the fast bit */")
sub("/* the basin wall — containment you can see, instead of a wall you can't */",
    "/* the basin wall: containment you can see, instead of a wall you cannot */")

sub("<p>A desert basin, a long-travel truck, and 70 cm of suspension you can watch working.",
    "<p>A desert basin, a big truck, and 70 cm of suspension you can watch working.")
sub("Twelve gates out there if you want a route. No clock — nothing is chasing you.",
    "Twelve gates out there if you want a route. No clock, nothing is chasing you.")
sub("flash('Loop complete','all twelve — going round again');",
    "flash('Loop complete','all twelve, going round again');")
sub('<div class="d" id="bdist">— m</div>', '<div class="d" id="bdist">0 m</div>')
sub("}else bdist.textContent='— m';", "}else bdist.textContent='0 m';")

# --- reusable body axis vectors instead of a clone every substep -------
sub("""var _wWorld=new THREE.Vector3(), _P0=new THREE.Vector3(), _nrm=new THREE.Vector3();""",
    """var _wWorld=new THREE.Vector3(), _P0=new THREE.Vector3(), _nrm=new THREE.Vector3();
var _bfwd=new THREE.Vector3(), _bup=new THREE.Vector3();""")

sub("""  var bodyFwd=_tmp.set(0,0,1).applyQuaternion(S.q).clone();
  var bodyUp =new THREE.Vector3(0,1,0).applyQuaternion(S.q);""",
    """  _bfwd.set(0,0,1).applyQuaternion(S.q);
  _bup.set(0,1,0).applyQuaternion(S.q);""")

sub("    _fwd.copy(bodyFwd);\n    if(c2.front) _fwd.applyAxisAngle(bodyUp,steerAng);",
    "    _fwd.copy(_bfwd);\n    if(c2.front) _fwd.applyAxisAngle(_bup,steerAng);")
sub("    Tsum.addScaledVector(bodyUp,-yawT);", "    Tsum.addScaledVector(_bup,-yawT);")
sub("    _tmp.crossVectors(bodyUp,_up);", "    _tmp.crossVectors(_bup,_up);")
sub("  if(bodyUp.y<0.15 && S.v.lengthSq()<4)", "  if(_bup.y<0.15 && S.v.lengthSq()<4)")

# --- the contact patch is where the tyre actually pushes ---------------
# Applying lateral force at the strut mount loses the roll couple, which is
# most of what makes a car lean into a corner. Apply it at the patch.
sub("    c.cp.copy(_wp).addScaledVector(_dir,c.len+WHEEL_R*0.0);",
    "    c.cp.copy(_wp).addScaledVector(_dir,c.len+WHEEL_R);")
sub("""    _r.copy(c2.mount).applyQuaternion(S.q);
    _vp.copy(_wWorld).cross(_r).add(S.v);
    var vf=_vp.dot(_fwd), vr=_vp.dot(_rgt);""",
    """    _r.copy(c2.cp).sub(S.p);          /* the patch, so cornering rolls the body */
    _vp.copy(_wWorld).cross(_r).add(S.v);
    var vf=_vp.dot(_fwd), vr=_vp.dot(_rgt);""")
sub("    _rgt.crossVectors(c2.nrm,_fwd).normalize().multiplyScalar(-1);",
    "    _rgt.crossVectors(c2.nrm,_fwd).normalize();")

# --- air control: positive torque about body +x drops the nose ---------
sub("""    Tsum.addScaledVector(bodyUp.clone().cross(_tmp.set(0,0,0)),0);   /* no-op guard */
    var pitchT=(S.throttle-S.brake)*7000;""",
    """    var pitchT=-(S.throttle-S.brake)*7000;""")

# --- portrait needs a wider lens or the world falls out of frame -------
sub("    camera.fov=70+Math.min(16,speed*0.42);",
    "    camera.fov=70+PB()+Math.min(16,speed*0.42);")
sub("    camera.fov=62+Math.min(20,speed*0.52);",
    "    camera.fov=62+PB()+Math.min(20,speed*0.52);")
sub("var CAMS=['Chase','Hood','Wide'];",
    """var CAMS=['Chase','Hood','Wide'];
/* a tall frame at a fixed vertical FOV leaves almost no horizontal field */
function PB(){ return (1-Math.min(1,camera.aspect))*22; }""")

# --- instanced props need their matrices flagged -----------------------
sub("  rocks.count=k; bushes.count=b;",
    "  rocks.count=k; bushes.count=b;\n  rocks.instanceMatrix.needsUpdate=true; bushes.instanceMatrix.needsUpdate=true;")

# --- dust colour was computed twice, once uselessly --------------------
sub("""    _dc.setHex(0xe8caa0).lerp(FOG,1-t);
    ca.array[i*3]=_dc.r*t+FOG.r*(1-t);
    ca.array[i*3+1]=_dc.g*t+FOG.g*(1-t);
    ca.array[i*3+2]=_dc.b*t+FOG.b*(1-t);""",
    """    _dc.setRGB(0.91,0.79,0.63).lerp(FOG,1-t);
    ca.array[i*3]=_dc.r; ca.array[i*3+1]=_dc.g; ca.array[i*3+2]=_dc.b;""")

# --- gate recolour, written plainly ------------------------------------
sub("""    gt.g.children.forEach(function(ch){
      if(ch.material && ch.material.color && ch!==gt.beam) ch.material=ch.material.clone(),
        ch.material.color.setHex(0x2bc4b0);
    });""",
    """    gt.g.children.forEach(function(ch){
      if(ch===gt.beam || !ch.material || !ch.material.color) return;
      ch.material=ch.material.clone();
      ch.material.color.setHex(0x2bc4b0);
    });""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)

print('applied:', n)
if missed:
    print('MISSED:')
    for m in missed: print('   ', m)

# report any surviving em or en dash with context
bad = []
for i, line in enumerate(s.split('\n'), 1):
    if '—' in line or '–' in line:
        bad.append(str(i) + ': ' + line.strip()[:110])
print('remaining long dashes:', len(bad))
for b in bad: print('   ', b)
