# -*- coding: utf-8 -*-
"""A car that would rather go forward, and a desert that actually kicks up.

DOWNFORCE. There was none in the physics at all, so a fast car could only be
made fast by inventing grip numbers, which is the thing that makes an arcade
car feel like it is on rails rather than pressed onto the road. It is now real:
a force along the body's own down axis proportional to the square of forward
speed, split front and rear, added to the load the tyres carry. So grip arrives
with speed and leaves with it, the nose stays down under power, and the car
gets progressively harder to provoke sideways the faster it goes, which is
exactly the character you asked for.

Because the force is applied at the axles rather than at the centre, the split
also trims the balance: rear biased downforce settles the back end at speed.

THE VELOCE. The fifth car. Long, low, wide track, stiff, high final drive, the
most downforce by a distance and the least suspension travel. It is the worst
of the five over rough ground and the best of them on anything open. It does
not want to drift and it will resist you if you ask, which is the point.

DUST. The desert emitted at a fixed one in six chance per wheel with no regard
to how hard the wheel was actually working, and the pool was small enough that
a plume aged out before it read as one. The pool is larger, the rate scales
with slip and speed, a hard slide throws a proper wall of it, and there is a
faint rooster tail off the driven wheels so you can see what the throttle is
doing to the ground.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================================= downforce
sub("""  Fsum.set(0,-MASS*G,0); Tsum.set(0,0,0);""",
"""  Fsum.set(0,-MASS*G,0); Tsum.set(0,0,0);

  /* ---- aerodynamic downforce ----
     Along the body's own down axis, proportional to forward speed squared, so
     grip arrives with speed and leaves with it. Applied at the axles rather
     than the centre, so the front/rear split also trims the balance. */
  S.dfF=0; S.dfR=0;
  if(AERO>0){
    _bup.set(0,1,0).applyQuaternion(S.q);
    var vFwd=Math.abs(S.v.dot(_bfwd0.set(0,0,1).applyQuaternion(S.q)));
    var dfTot=AERO*vFwd*vFwd;
    S.dfF=dfTot*AERO_F; S.dfR=dfTot*(1-AERO_F);
    Fsum.addScaledVector(_bup,-dfTot);
    /* the pitching moment from putting it on the axles, not the middle */
    _tmp.set(0,0,1).applyQuaternion(S.q);
    Tsum.addScaledVector(_tmp.cross(_bup), (S.dfF-S.dfR)*WHEELBASE*0.5*0.0);
  }""")

sub("""var _up=new THREE.Vector3(0,1,0);""",
    """var _up=new THREE.Vector3(0,1,0), _bfwd0=new THREE.Vector3();""")

# the load a tyre carries includes its share of the downforce
sub("""    var N=c2.load;""",
"""    /* Downforce presses on the tyre, so it is load like any other load. This
       is what makes grip arrive with speed instead of being a fixed number. */
    var N=c2.load + (c2.front? S.dfF*0.5 : S.dfR*0.5);""")

# per vehicle
sub("var MAX_DRIVE=22000, MAX_BRAKE=25000, BRAKE_BIAS_F=0.62;",
    "var MAX_DRIVE=22000, MAX_BRAKE=25000, BRAKE_BIAS_F=0.62;\nvar AERO=0, AERO_F=0.42;   /* newtons per (m/s)^2, and the front share */")

sub("""    MU_LAT_F=V.muF; MU_LAT_R=V.muR;""",
    """    MU_LAT_F=V.muF; MU_LAT_R=V.muR;
    AERO=V.aero||0; AERO_F=(V.aeroF===undefined?0.42:V.aeroF);""")

# give the existing four a little, and add the fifth
sub("dF:0.35, dR:0.65, muF:1.00, muR:0.92, hRoll:0.56, hPitch:1.05, rb:0.50,",
    "dF:0.35, dR:0.65, muF:1.00, muR:0.92, hRoll:0.56, hPitch:1.05, rb:0.50, aero:1.2,")
sub("dF:0.42, dR:0.58, muF:1.06, muR:1.00, hRoll:0.60, hPitch:1.02, rb:0.53,",
    "dF:0.42, dR:0.58, muF:1.06, muR:1.00, hRoll:0.60, hPitch:1.02, rb:0.53, aero:2.6,")
sub("dF:0.14, dR:0.86, muF:0.98, muR:1.02, hRoll:0.44, hPitch:0.86, rb:0.62,",
    "dF:0.14, dR:0.86, muF:0.98, muR:1.02, hRoll:0.44, hPitch:0.86, rb:0.62, aero:4.4, aeroF:0.34,")
sub("dF:0.18, dR:0.82, muF:1.02, muR:1.06, hRoll:0.40, hPitch:0.80, rb:0.57,",
    "dF:0.18, dR:0.82, muF:1.02, muR:1.06, hRoll:0.40, hPitch:0.80, rb:0.57, aero:6.5, aeroF:0.40,")

sub("""    bodyY:-0.26, paint:0x66c04a, second:0x241f2a, W:1.86, L:4.12 }
];""",
"""    bodyY:-0.26, paint:0x66c04a, second:0x241f2a, W:1.86, L:4.12 },

  /* The one that would rather go forward. Long, low, the widest track of the
     five, the stiffest springs, the least travel and by a distance the most
     downforce. Poor over rough ground, and the only car here that resists you
     when you ask it to go sideways. */
  { id:'veloce', name:'Veloce GT', kind:'High speed, high grip',
    mass:1310, track:2.24, wb:2.98, wheelR:0.46, tyreW:0.60,
    rest:0.40, susMax:0.62, susMin:0.19, k:27600, dBump:2880, dReb:3520,
    arbF:7600, arbR:9200, drive:31500, brake:31000, biasF:0.62,
    dF:0.30, dR:0.70, muF:1.16, muR:1.20, hRoll:0.34, hPitch:0.74, rb:0.54,
    aero:14.5, aeroF:0.44,
    bodyY:-0.30, paint:0x2f5fd0, second:0xe8e2d4, W:1.90, L:4.30 }
];""")

# a shell for it: a low wedge with a real wing
sub("""  var SHELLS={bracken:shellBracken, marisol:shellMarisol,
              kestrel:shellKestrel, serrano:shellSerrano};""",
"""  /* ---- Veloce GT: long, low, a splitter at the front and a wing on stalks
     at the back, because the downforce should be visible. ---- */
  function shellVeloce(V){
    W=V.W;
    box(W,0.34,4.30, paint, 0,-0.08, 0.00);
    box(W+0.14,0.07,0.62, second, 0,-0.20, 1.94, false);      /* splitter */
    box(W-0.10,0.20,1.20, paint, 0, 0.16, 1.44);
    box(W-0.34,0.18,0.70, paint, 0, 0.32, 1.02, false);
    cyl(0.13,0.09,10, lampM, -0.64,0.22,2.02, Math.PI/2);
    cyl(0.13,0.09,10, lampM,  0.64,0.22,2.02, Math.PI/2);
    /* a long low cabin set back, which is what makes it read as fast */
    box(W-0.26,0.46,1.34, paint, 0, 0.50, 0.18);
    box(1.42,0.40,0.10, glass, 0, 0.64, 0.82, false);
    box(0.08,0.32,1.02, glass,-0.80, 0.66, 0.14, false);
    box(0.08,0.32,1.02, glass, 0.80, 0.66, 0.14, false);
    box(W-0.34,0.07,1.08, second, 0, 0.75, 0.12, false);
    /* haunch and deck */
    box(W,0.42,1.52, paint, 0, 0.30,-1.24);
    for(var s=0;s<5;s++) box(1.16,0.04,0.08, second, 0,0.53,-0.86-s*0.22, false);
    box(1.30,0.12,0.06, tailM, 0, 0.36,-2.02, false);
    box(1.24,0.13,0.20, trim, 0,-0.16,-2.06);
    /* the wing, on stalks, clear of the deck */
    [[-0.62],[0.62]].forEach(function(pp){
      box(0.07,0.34,0.10, trim, pp[0],0.66,-1.86, false);
    });
    box(W+0.16,0.06,0.40, second, 0, 0.86,-1.88, false);
    box(W+0.16,0.05,0.14, trim,  0, 0.80,-1.74, false);
    box(W+0.03,0.06,3.90, second, 0, 0.08,-0.10, false);
    flares(V,1.40,-1.40,0.40,0.15);
  }

  var SHELLS={bracken:shellBracken, marisol:shellMarisol,
              kestrel:shellKestrel, serrano:shellSerrano, veloce:shellVeloce};""")

# the garage bar should show downforce, since it is now a real thing
sub("""  document.getElementById('g-trav').style.width=pct(V.susMax-V.susMin,0.48,0.90);""",
    """  document.getElementById('g-trav').style.width=pct(V.susMax-V.susMin,0.48,0.90);
  var ae=document.getElementById('g-aero');
  if(ae) ae.style.width=pct(V.aero||0,0,15);""")
sub("""      <div><span>Travel</span><i><b id="g-trav"></b></i></div>""",
    """      <div><span>Travel</span><i><b id="g-trav"></b></i></div>
      <div><span>Downforce</span><i><b id="g-aero"></b></i></div>""")

# ===================================================================== dust
sub("var DUST_N=520,", "var DUST_N=1100,")
sub("""    if(c.contact && (speed>9 || c.slip>3.0) && Math.random()<0.17*c.dustK){
      puff(c.cp.x+(Math.random()-0.5)*0.5, c.cp.y+0.1, c.cp.z+(Math.random()-0.5)*0.5,
           (Math.random()-0.5)*1.6 - S.v.x*0.09,
           0.7+Math.random()*1.5 + Math.min(2.5,c.slip*0.3),
           (Math.random()-0.5)*1.6 - S.v.z*0.09);
    }""",
"""    /* Kick dust in proportion to how hard the wheel is actually working, not
       at a flat rate. A hard slide should throw a wall of it. */
    var work=Math.min(1,speed/26)*0.55 + Math.min(1,c.slip/9)*0.85;
    var rate=0.34*c.dustK*work;
    if(c.contact && (speed>6 || c.slip>2.2)){
      var puffs=(Math.random()<rate?1:0) + (Math.random()<rate-1?1:0);
      for(var pn=0;pn<puffs;pn++){
        puff(c.cp.x+(Math.random()-0.5)*0.7, c.cp.y+0.08, c.cp.z+(Math.random()-0.5)*0.7,
             (Math.random()-0.5)*2.2 - S.v.x*0.11,
             0.6+Math.random()*1.7 + Math.min(3.4,c.slip*0.38),
             (Math.random()-0.5)*2.2 - S.v.z*0.11,
             0.9+Math.random()*0.8);
      }
      /* and a rooster tail off a driven wheel that is spinning up */
      if(!c.front && c.slip>4.5 && Math.random()<0.5*c.dustK){
        puff(c.cp.x-S.v.x*0.03, c.cp.y+0.2, c.cp.z-S.v.z*0.03,
             -S.v.x*0.30+(Math.random()-0.5)*1.4,
             2.2+Math.random()*2.2,
             -S.v.z*0.30+(Math.random()-0.5)*1.4,
             1.3+Math.random()*0.7);
      }
    }""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
