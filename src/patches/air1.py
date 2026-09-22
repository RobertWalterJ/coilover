# -*- coding: utf-8 -*-
"""Air control that lands rubber side down.

The measured problem: takeoff was right on the ramp and the jumps were 45 to
54 metres, but landing attitude was 0.15 to 0.36 upright, so the truck was
somersaulting the whole way. Holding gas applied 7000 Nm of pitch against a
pitch inertia of 1860 with only light damping, which settles at nearly 8 rad
per second. That is three full flips in a two and a half second jump.

Four rules, all from the physics review:
  1. A hard cap on angular rate, so no input can wind it up indefinitely.
  2. Preserve whatever the ramp gave you for the first 0.18 s, or the jump
     stops feeling physical.
  3. Self levelling ramps up by PREDICTED time to impact rather than running
     constantly. It is zero for most of the flight and becomes a firm hand in
     the last half second, so nobody reads it as assistance.
  4. Damp hard on the axes the player is not touching, lightly on the ones
     they are, so input still has authority.

Plus velocity alignment, so a long jump noses over the way a thrown object
does instead of sailing flat.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("""  if(grounded===0){
    /* classic arcade attitude control: nose up on the gas, down on the brake */
    var pitchT=-(S.throttle-S.brake)*7000;
    var yawT=S.steer*5200;
    _tmp.set(1,0,0).applyQuaternion(S.q); Tsum.addScaledVector(_tmp,pitchT);
    Tsum.addScaledVector(_bup,-yawT);
    /* gentle self-levelling so you land roughly rubber-side down */
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,2600);
    Tsum.addScaledVector(_wWorld,-900);
  }""",
"""  if(grounded===0 && S.airT>0.18){
    /* Nose up on the gas, down on the brake. Under the old value this alone
       flipped the truck three times in a long jump. */
    var inP=Math.abs(S.throttle-S.brake)>0.15, inY=Math.abs(S.steer)>0.15;
    _tmp.set(1,0,0).applyQuaternion(S.q);
    Tsum.addScaledVector(_tmp,-(S.throttle-S.brake)*4600);
    Tsum.addScaledVector(_bup,-S.steer*3600);

    /* damp hard where there is no input, lightly where there is */
    Tsum.addScaledVector(_wWorld,-((inP||inY)?520:1600));

    /* How long until the ground? Level up only as that closes. */
    var gy=height(S.p.x,S.p.z);
    var clr=Math.max(0,S.p.y-gy-1.0);
    var tImp=(S.v.y<-0.2)? clr/(-S.v.y) : 99;
    var lvl=Math.max(0,1-tImp/0.75)*3600;
    if(inP||inY) lvl*=0.25;
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,lvl);

    /* nose follows the velocity vector on a long flight, as a thrown thing does */
    if(!inP && S.v.lengthSq()>144){
      _Fl.copy(S.v).normalize();
      _ra.crossVectors(_bfwd,_Fl);
      Tsum.addScaledVector(_ra,1100);
    }
  }""")

# a hard rate cap, so nothing can wind the body up without limit
sub("""  S.w.x+=ax2*dt; S.w.y+=ay2*dt; S.w.z+=az2*dt;
  S.w.multiplyScalar(Math.exp(-0.7*dt));""",
"""  S.w.x+=ax2*dt; S.w.y+=ay2*dt; S.w.z+=az2*dt;
  S.w.multiplyScalar(Math.exp(-0.7*dt));
  var wl=S.w.length(), wcap=(grounded===0)?5.2:8.0;
  if(wl>wcap) S.w.multiplyScalar(wcap/wl);""")

# a landing within about thirty degrees of flat should count
sub("      if(_bup.y>0.90){", "      if(_bup.y>0.86){")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
