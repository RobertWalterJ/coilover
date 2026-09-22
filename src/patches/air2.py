# -*- coding: utf-8 -*-
"""Air control, second attempt: hold an attitude instead of accelerating a spin.

Rate control was the wrong model. Torque proportional to input means holding
the gas winds the body up without limit, so a natural player input produced
three somersaults. Measured landing attitude was 0.16 upright, and halving the
authority only got it to 0.30.

Now the truck flies to a TARGET attitude through a PD controller. Gas means
nose up about twenty five degrees and stay there. With no input the nose
follows the flight path, so a long jump noses over on the way down the way a
thrown object does. Steering still yaws by rate, because yaw does not ruin a
landing.

The controller runs at thirty percent authority through the flight, which is
enough to stop a runaway, and ramps to full as the ground closes, so the last
half second is a firm hand that nobody reads as assistance. Whatever the ramp
imparts in the first 0.18 s is preserved untouched.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("""var _rp=new THREE.Vector3(), _ra=new THREE.Vector3(), _Fl=new THREE.Vector3();""",
    """var _rp=new THREE.Vector3(), _ra=new THREE.Vector3(), _Fl=new THREE.Vector3();
var _qT=new THREE.Quaternion(), _qE=new THREE.Quaternion(), _qI=new THREE.Quaternion();
var _eul=new THREE.Euler();""")

old_air = s[s.index("  if(grounded===0 && S.airT>0.18){"):s.index("  /* ---- integrate ---- */")]
new_air = """  if(grounded===0 && S.airT>0.18){
    var inP=Math.abs(S.throttle-S.brake)>0.15;

    /* Where do we want the nose? On the gas it lifts. Hands off, it follows
       the flight path, which is what makes a long jump look thrown. */
    var wantPitch;
    if(inP) wantPitch=(S.throttle-S.brake)*0.44;
    else {
      var fpa=Math.atan2(S.v.y,Math.max(0.5,Math.hypot(S.v.x,S.v.z)));
      wantPitch=Math.max(-0.5,Math.min(0.30,fpa*0.65));
    }

    /* target attitude: current heading, wanted pitch, no roll */
    _Fl.set(_bfwd.x,0,_bfwd.z);
    if(_Fl.lengthSq()<1e-5) _Fl.set(0,0,1);
    _Fl.normalize();
    _qT.setFromEuler(_eul.set(wantPitch,Math.atan2(_Fl.x,_Fl.z),0,'YXZ'));

    /* shortest rotation from where we are to where we want to be */
    _qE.copy(_qT).multiply(_qI.copy(S.q).invert());
    if(_qE.w<0){ _qE.x=-_qE.x; _qE.y=-_qE.y; _qE.z=-_qE.z; _qE.w=-_qE.w; }
    var sw=Math.sqrt(Math.max(1e-9,1-_qE.w*_qE.w));
    var angE=2*Math.acos(Math.max(-1,Math.min(1,_qE.w)));
    _ra.set(_qE.x/sw,_qE.y/sw,_qE.z/sw);

    /* Thirty percent through the flight, full as the ground closes. */
    var gy=height(S.p.x,S.p.z);
    var clr=Math.max(0,S.p.y-gy-1.0);
    var tImp=(S.v.y<-0.2)? clr/(-S.v.y) : 99;
    var auth=0.30+0.70*Math.max(0,1-tImp/1.20);

    Tsum.addScaledVector(_ra, angE*11000*auth);
    Tsum.addScaledVector(_wWorld, -2400*auth);

    /* steering still yaws, and yaw never ruins a landing */
    Tsum.addScaledVector(_bup,-S.steer*3000);
  }

"""
s = s.replace(old_air, new_air, 1); n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
