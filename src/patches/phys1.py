# -*- coding: utf-8 -*-
"""Physics pass.

Fixes a rollover I introduced, then takes the tuning work from the review.

The rollover: moving tyre forces to the contact patch was right for body roll,
but it put the moment arm 1.14 m below the centre of gravity, giving a static
stability factor of 0.90 g against tyres that pull 0.98. It tipped from
cornering alone. The fix is the couple height lever: forces still act at the
patch for translation, but the torque arm uses a shorter virtual height, 0.75 m
for lateral and 1.05 m for longitudinal. That keeps the car stable while
actually exaggerating dive, squat and roll, which is what we want to see.

The rest: a real slip angle curve with a slow post peak falloff so a slide is
somewhere you can live rather than a cliff, relaxation length so counter
steering feels like a conversation, load sensitivity, counter steer headroom in
the steering limiter, a progressive bump stop that gives energy back, and drive
and brake forces raised above the traction limit so wheelspin and lockup exist.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- constants
sub("""var SPRING_K=10400;                               /* N/m, static sits near 0.60 */
var DAMP_BUMP=1500, DAMP_REB=2650;                /* asymmetric, like a real shock */
var ARB=5200;                                     /* anti-roll bar */
var MAX_DRIVE=9600, MAX_BRAKE=8200;
var MU=0.98, MU_HAND=0.34;
var STEER_MAX=0.52;                               /* rad at crawl */""",
"""var SPRING_K=10400;                               /* N/m, static sits near 0.62 */
var DAMP_BUMP=1500, DAMP_REB=1900;                /* rebound was packing over whoops */
var DAMP_KNEE=1.8, DAMP_CLAMP=7500;               /* digressive blowoff, like a bypass */
var ARB_F=1800, ARB_R=3200;                       /* low, and rear biased, so it rolls */
var BS_ZONE=0.12, BS_K1=120000, BS_K2=1.2e6, BS_DAMP=4500, BS_REST=0.55;

/* Force acts at the contact patch, but the torque arm uses a shorter virtual
   height. Low enough to be stable, high enough to be dramatic. */
var H_ROLL=0.75, H_PITCH=1.05;

var MAX_DRIVE=15000, MAX_BRAKE=16000, BRAKE_BIAS_F=0.62;
var DRIVE_F=0.35, DRIVE_R=0.65;

/* Simplified magic formula. alphaPeak is how far you can lean on it, C is how
   sharply it lets go past the peak. At full lock sideways it still holds 65
   percent of peak, and that slow decay is what makes a drift liveable. */
var MU_LAT_F=1.00, MU_LAT_R=0.92, MU_LONG_MULT=1.08;
var TYRE_C=1.55, ALPHA_PEAK=0.140;
var TYRE_B=Math.tan(Math.PI/(2*TYRE_C))/ALPHA_PEAK;
var MU_HAND=0.34, HAND_C=1.30, HAND_B=Math.tan(Math.PI/(2*HAND_C))/0.436;
var FZ_REF=3433, RELAX=0.55;""")

# ---------------------------------------------------------------- state
sub("""      len:SUS_REST, prevLen:SUS_REST, load:0, contact:false, spin:0, slip:0,""",
    """      len:SUS_REST, prevLen:SUS_REST, load:0, contact:false, spin:0, slip:0,
      alphaF:0, locked:false,""")

sub("""  MASS/12*(1.95*1.95+1.05*1.05)*1.9   /* roll, stiffened so it does not tip on every crest */""",
    """  MASS/12*(1.95*1.95+1.05*1.05)*1.25  /* the couple lever handles stability now */""")

# ---------------------------------------------------------------- temps
sub("""var _bfwd=new THREE.Vector3(), _bup=new THREE.Vector3();""",
    """var _bfwd=new THREE.Vector3(), _bup=new THREE.Vector3(), _brgt=new THREE.Vector3();
var _rp=new THREE.Vector3(), _ra=new THREE.Vector3(), _Fl=new THREE.Vector3();""")

sub("""  _bfwd.set(0,0,1).applyQuaternion(S.q);
  _bup.set(0,1,0).applyQuaternion(S.q);""",
    """  _bfwd.set(0,0,1).applyQuaternion(S.q);
  _bup.set(0,1,0).applyQuaternion(S.q);
  _brgt.crossVectors(_bup,_bfwd).normalize();""")

# ---------------------------------------------------------------- damper + bump stop
sub("""    /* spring: zero at full droop, so static ride settles part-way down */
    var Fs=SPRING_K*(SUS_MAX-c.len);
    /* damper: closing speed along the strut axis */
    var vs=_vp.dot(_dir);
    Fs += (vs>0?DAMP_BUMP:DAMP_REB)*vs;
    if(Fs<0) Fs=0; if(Fs>34000) Fs=34000;
    c.load=Fs;""",
"""    /* spring: zero at full droop, so static ride settles part-way down */
    var Fs=SPRING_K*(SUS_MAX-c.len);

    /* Damper, digressive. A linear damper on a four metre drop produces an
       11 kN spike in one step, which feels like hitting concrete. This stays
       soft over small bumps and firms up without ever spiking. */
    var vs=_vp.dot(_dir);
    var Fd=(vs>0?DAMP_BUMP:DAMP_REB)*vs/(1+Math.abs(vs)/DAMP_KNEE);
    if(Fd>DAMP_CLAMP) Fd=DAMP_CLAMP; else if(Fd<-DAMP_CLAMP) Fd=-DAMP_CLAMP;
    Fs += Fd;

    /* Progressive bump stop instead of a wall, and it gives back 55 percent of
       what it absorbs. That is what relaunches you off a downslope landing. */
    var into=SUS_MIN+BS_ZONE-c.len;
    if(into>0){
      Fs += BS_K1*into + BS_K2*into*into;
      Fs += (vs>0? BS_DAMP*vs : BS_DAMP*vs*(1-BS_REST));
      if(into>BS_ZONE*0.55 && vs>1.2 && !c.wasBottomed){
        c.wasBottomed=true; S.shake=Math.max(S.shake,Math.min(0.7,vs*0.11));
        thump(Math.min(1,vs*0.14)); buzz([9,26,9]);
      }
    } else c.wasBottomed=false;

    /* A strut can only ever push. If rebound damping beat the spring the strut
       would pull the chassis into the ground on a crest. */
    if(Fs<0) Fs=0; if(Fs>41000) Fs=41000;
    c.load=Fs;""")

# ---------------------------------------------------------------- ARB
sub("""    var dF=ARB*(comp[ax*2]-comp[ax*2+1]);""",
    """    var dF=(ax===0?ARB_F:ARB_R)*(comp[ax*2]-comp[ax*2+1]);""")

# ---------------------------------------------------------------- tyres
old_tyre = s[s.index("  /* ---- tyres ---- */"):s.index("  /* aero + air control */")]
new_tyre = '''  /* ---- tyres ---- */
  var speed=S.v.length();

  /* Counter steer headroom. Limiting the rack by speed alone is correct for
     grip but it means the lock you need to catch a slide is more than the lock
     you are allowed, so the save becomes impossible and the player blames the
     physics. Give the limit back in proportion to how sideways the car is. */
  var vbF=S.v.dot(_bfwd), vbR=S.v.dot(_brgt);
  var beta=Math.atan2(vbR,Math.abs(vbF)+1.0);
  var dmax=0.13 + 0.47/(1+Math.pow(speed/9.0,1.6)) + Math.min(0.28,Math.abs(beta));
  var steerAng=S.steer*dmax;

  /* fake locked diff: torque only to the wheels that are actually down */
  var nF=(corners[0].contact?1:0)+(corners[1].contact?1:0);
  var nR=(corners[2].contact?1:0)+(corners[3].contact?1:0);
  var driveCurve=Math.max(0,1-Math.pow(speed/44,1.6));

  for(var i2=0;i2<4;i2++){
    var c2=corners[i2];
    if(!c2.contact){ c2.slip=0; c2.locked=false; continue; }
    var N=c2.load;
    if(N<1) continue;

    /* wheel heading, flattened onto the ground plane */
    _fwd.copy(_bfwd);
    if(c2.front) _fwd.applyAxisAngle(_bup,steerAng);
    _fwd.addScaledVector(c2.nrm,-_fwd.dot(c2.nrm));
    if(_fwd.lengthSq()<1e-6) continue;
    _fwd.normalize();
    _rgt.crossVectors(c2.nrm,_fwd).normalize();

    _r.copy(c2.cp).sub(S.p);
    _vp.copy(_wWorld).cross(_r).add(S.v);
    var vf=_vp.dot(_fwd), vr=_vp.dot(_rgt);

    /* Load sensitivity. One line, and it buys lift off oversteer, trail
       braking, and the reason hard cornering costs you total grip. */
    var D=Math.pow(FZ_REF/Math.max(200,N),0.15);
    if(D<0.80)D=0.80; else if(D>1.20)D=1.20;

    var hand=(!c2.front && S.hand>0.5);
    var muL=hand? MU_HAND : (c2.front?MU_LAT_F:MU_LAT_R);
    var Bc=hand?HAND_B:TYRE_B, Cc=hand?HAND_C:TYRE_C;
    if(c2.locked) muL*=0.55;

    /* Slip angle, filtered by distance travelled rather than by time. That
       kills terrain jitter, goes naturally sluggish at walking pace, and adds
       the small lag that makes catching a slide feel physical. */
    var alpha=Math.atan2(vr,Math.abs(vf)+0.7);
    var kRel=speed*dt/RELAX; if(kRel>1)kRel=1;
    c2.alphaF += (alpha-c2.alphaF)*kRel;
    var Flat=-N*muL*D*Math.sin(Cc*Math.atan(Bc*c2.alphaF));

    /* longitudinal */
    var Flong=0;
    var share=c2.front? DRIVE_F/Math.max(1,nF) : DRIVE_R/Math.max(1,nR);
    Flong += (S.throttle-S.rev*0.55)*MAX_DRIVE*driveCurve*share;

    var bf=MAX_BRAKE*(c2.front?BRAKE_BIAS_F:1-BRAKE_BIAS_F)*0.5*S.brake
         + (!c2.front? S.hand*4200 : 0);
    if(bf>0){
      var want=-vf*430;
      var applied=Math.max(-bf,Math.min(bf,want));
      Flong += applied;
      c2.locked = (Math.abs(want)>bf && Math.abs(vf)>0.6);
    } else c2.locked=false;
    Flong -= vf*18;                                    /* rolling resistance */

    /* Friction ellipse rather than a circle: a touch more longitudinal than
       lateral, so you can always still brake. */
    var limLong=MU_LONG_MULT*muL*N*D, limLat=muL*N*D;
    var u=Flong/Math.max(1,limLong), wq=Flat/Math.max(1,limLat);
    var m2=Math.sqrt(u*u+wq*wq);
    if(m2>1){ Flong/=m2; Flat/=m2; }

    c2.slip=Math.abs(vr)+Math.abs(c2.alphaF)*speed*0.5;

    /* Translation acts at the patch. Torque uses the shortened couple arms,
       which is what keeps it upright while still leaning hard. */
    _F.copy(_fwd).multiplyScalar(Flong).addScaledVector(_rgt,Flat);
    Fsum.add(_F);

    _rp.copy(_r).addScaledVector(_bup,-_r.dot(_bup));   /* planar part of the arm */
    _ra.copy(_rp).addScaledVector(_bup,-H_PITCH);
    _Fl.copy(_fwd).multiplyScalar(Flong);
    Tsum.add(_tmp.crossVectors(_ra,_Fl));
    _ra.copy(_rp).addScaledVector(_bup,-H_ROLL);
    _Fl.copy(_rgt).multiplyScalar(Flat);
    Tsum.add(_tmp.crossVectors(_ra,_Fl));

    c2.spin += (vf/WHEEL_R)*dt;
  }

'''
s = s.replace(old_tyre, new_tyre, 1); n += 1

# steerAng is recomputed for the visuals in sync(); keep it consistent
sub("""  var speed=S.v.length();
  var steerAng=S.steer*STEER_MAX*(0.34+0.66/(1+speed*0.075));
  for(var i=0;i<4;i++){
    var c=corners[i], st=STRUT[i];""",
"""  var speed=S.v.length();
  var vbF2=S.v.dot(_bfwd), vbR2=S.v.dot(_brgt);
  var beta2=Math.atan2(vbR2,Math.abs(vbF2)+1.0);
  var steerAng=S.steer*(0.13+0.47/(1+Math.pow(speed/9.0,1.6))+Math.min(0.28,Math.abs(beta2)));
  for(var i=0;i<4;i++){
    var c=corners[i], st=STRUT[i];""")

# ---------------------------------------------------------------- integrator
sub("var last=performance.now(), acc=0, FIXED=1/120;",
    "var last=performance.now(), acc=0, FIXED=1/200;   /* 0.2 m per step at top speed */")
sub("    while(acc>=FIXED && guard++<5){ step(FIXED); acc-=FIXED; }\n    if(acc>FIXED*5) acc=0;",
    "    while(acc>=FIXED && guard++<8){ step(FIXED); acc-=FIXED; }\n    if(acc>FIXED*8) acc=0;")

# ---------------------------------------------------------------- camera
sub("    camera.fov=70+PB()+Math.min(16,speed*0.42);",
    "    camera.fov=66+PB()+Math.min(14,speed*0.40);")
sub("    camera.fov=62+PB()+Math.min(20,speed*0.52);",
    "    camera.fov=56+PB()+Math.min(14,speed*0.40);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
