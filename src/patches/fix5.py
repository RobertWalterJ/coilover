# -*- coding: utf-8 -*-
"""Three things.

1. It still rolled in a hard corner at 55 km/h. Cornering alone cannot tip it
   now, but sliding sideways into a dune face trips it instantly, and instantly
   is not fun. Add the catch window: heavy roll damping between 40 and 75
   degrees so a tip takes about a second, and let steering push back during it.
   A save you nearly did not make is the story the player wants.

2. Dust was rendering as big pale slabs. Smaller, warmer, and much softer.

3. Colour. You asked for more of it, and the measured study of the references
   agrees: those artists run median saturation around 0.5, not the muted amber
   I had. Saturate the sand and rock, and lift the shadows so they read as
   coloured rather than as holes.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------- 1. rollover catch
sub("""var H_ROLL=0.75, H_PITCH=1.05;""",
    """var H_ROLL=0.68, H_PITCH=1.05;""")

# Must be applied while Tsum is still being accumulated, so it goes in just
# before integration rather than next to the flip check further down.
sub("""  /* ---- integrate ---- */""",
"""  /* Rollovers should be survivable stories, not instant losses. Between 40
     and 75 degrees of lean, damp the roll hard so a tip stretches out to about
     a second, and let steering shove back against it. */
  var lean=Math.acos(Math.max(-1,Math.min(1,_bup.y)));
  if(lean>0.70 && lean<1.31){
    var rollRate=_wWorld.dot(_bfwd);
    Tsum.addScaledVector(_bfwd,-rollRate*4200 - S.steer*2200);
  }
  if(lean>0.96){
    _tmp.crossVectors(_bup,_up);
    Tsum.addScaledVector(_tmp,2500*Math.min(1,(lean-0.96)/0.44));
  }

  /* ---- integrate ---- */""")

# ---------------------------------------------------------- 2. dust
sub("""  dustPts=new THREE.Points(g,new THREE.PointsMaterial({
    size:1.5,sizeAttenuation:true,vertexColors:true,transparent:true,opacity:0.62,depthWrite:false}));""",
"""  dustPts=new THREE.Points(g,new THREE.PointsMaterial({
    size:0.62,sizeAttenuation:true,vertexColors:true,transparent:true,opacity:0.30,
    depthWrite:false,blending:THREE.NormalBlending}));""")

sub("""    _dc.setRGB(0.91,0.79,0.63).lerp(FOG,1-t);""",
    """    _dc.setRGB(0.93,0.80,0.60).lerp(FOG,1-t*0.85);""")

# fewer, calmer puffs
sub("""    if(c.contact && (speed>4.5 || c.slip>1.6) && Math.random()<0.55){""",
    """    if(c.contact && (speed>6 || c.slip>2.2) && Math.random()<0.34){""")

# ---------------------------------------------------------- 3. colour
sub("""var PAL={
  low:0xb4703f, mid:0xd69a5c, high:0xedc48a, rock:0x8c5340, playa:0xd8cbb0,
  scrub:0x6e7048, fog:0xe3ac83,""",
"""var PAL={
  /* Saturated on purpose. The measured reference work sits near 0.5 median
     saturation, and washed out sand reads as unfinished rather than tasteful. */
  low:0xb85f2c, mid:0xe09242, high:0xf5c877, rock:0x99452c, playa:0xe0cfa8,
  scrub:0x6e7048, fog:0xe8a271,""")

# lift the shadows: they should read as coloured, not as holes
sub("scene.add(new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.55));",
    "scene.add(new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.80));")
sub("var sun=new THREE.DirectionalLight(sc(PAL.sun),2.1);",
    "var sun=new THREE.DirectionalLight(sc(PAL.sun),1.85);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
