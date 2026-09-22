# -*- coding: utf-8 -*-
"""Light sources that actually light things.

You were right that this was missing, and it is the heart of the ember read.
Every lit thing in the world was emissive material only: the motel sign, the
gas station canopy, the drive in, the camp lantern and the water tower all
glowed on their own surface and threw nothing onto the ground. So the world had
bright objects in it but no pools of light, which is the one thing an ember
picture is made of.

There is now a pool of real point lights that follows you. The pool is a fixed
size so the shader never recompiles, and each frame the nearest lit landmarks
claim a light, ramped by how dark the sky is. Drive up to the motel sign at
dusk and the sand under it goes warm.

Headlights were on a night only switch, so at dusk, which is the best light in
the game, the truck drove with them off. They now come up from late golden hour
and are considerably stronger, with a proper falloff so the pool on the sand
reads instead of washing flat.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------- collect every lit point's world spot
sub("""/* the windmill rotor got pushed on as a bare entry; pull it back out */""",
"""/* Every material registered as lit belongs to a mesh somewhere in a landmark
   group. Find those meshes and remember where they are in the world, so a real
   light can be put there. Done by traversal rather than by hand so a new
   landmark lights itself with no extra wiring. */
var LIGHTPTS=[];
(function(){
  var lut=[];
  for(var i=0;i<LGLOW.length;i++) lut.push(LGLOW[i]);
  function look(m){
    for(var i=0;i<lut.length;i++) if(lut[i].m===m) return lut[i];
    return null;
  }
  for(var li=0;li<LANDMARKS.length;li++){
    var L=LANDMARKS[li];
    if(!L.g) continue;
    L.g.updateMatrixWorld(true);
    L.g.traverse(function(o){
      if(!o.material) return;
      var g=look(o.material); if(!g) return;
      var wp=new THREE.Vector3(); o.getWorldPosition(wp);
      LIGHTPTS.push({p:wp, c:g.c, s:g.s});
    });
  }
})();

/* the windmill rotor got pushed on as a bare entry; pull it back out */""")

# ------------------------------------------------------------ the light pool
sub("""var headL=new THREE.SpotLight(0xfff2cf,0,72,0.62,0.45,1.2);
var headR=new THREE.SpotLight(0xfff2cf,0,72,0.62,0.45,1.2);
headL.castShadow=headR.castShadow=false;
scene.add(headL,headR,headL.target,headR.target);""",
"""var headL=new THREE.SpotLight(0xfff2cf,0,86,0.60,0.42,1.35);
var headR=new THREE.SpotLight(0xfff2cf,0,86,0.60,0.42,1.35);
headL.castShadow=headR.castShadow=false;
scene.add(headL,headR,headL.target,headR.target);

/* A fixed pool, so the light count never changes and no material ever has to
   recompile. Unused lights sit at zero intensity rather than being removed. */
var LPOOL=[], LPOOL_N=mobile?3:5;
for(var _lp=0;_lp<LPOOL_N;_lp++){
  var _pl=new THREE.PointLight(0xffffff,0,54,1.7);
  _pl.castShadow=false; scene.add(_pl); LPOOL.push(_pl);
}
var _lpBest=[];
function updateLightPool(){
  /* how much the world wants artificial light at all */
  var want=Math.max(0,Math.min(1,(TOD.glow-0.10)/0.55));
  if(want<=0.001){
    for(var i=0;i<LPOOL.length;i++) LPOOL[i].intensity=0;
    return;
  }
  /* nearest lit points to the truck, which is what the player is looking at */
  _lpBest.length=0;
  for(var k=0;k<LIGHTPTS.length;k++){
    var L=LIGHTPTS[k];
    var d=L.p.distanceToSquared(S.p);
    if(d>150*150) continue;
    _lpBest.push({d:d,L:L});
  }
  _lpBest.sort(function(a,b){ return a.d-b.d; });
  for(var i=0;i<LPOOL.length;i++){
    var pl=LPOOL[i], e=_lpBest[i];
    if(!e){ pl.intensity=0; continue; }
    pl.position.copy(e.L.p);
    pl.color.copy(e.L.c).convertSRGBToLinear();
    /* fade the far ones out so a light never pops in at the edge of range */
    var f=1-Math.min(1,Math.sqrt(e.d)/150);
    pl.intensity=2.5*want*e.L.s*f*f;
  }
}""")

# ------------------------------------------- headlights from late golden hour
sub("  headL.intensity=headR.intensity=TOD.night*2.6;",
"""  /* Dusk is the best light in this game and the truck used to drive through
     it with the headlights off, because they were on a night only switch. */
  var hw=Math.max(0,Math.min(1,(TOD.glow-0.12)/0.50));
  headL.intensity=headR.intensity=hw*4.6;""")

# --------------------------------------------------------- drive it per frame
sub("""  sync(dt);
  updateCam(dt);
  renderFrame(dt);""",
"""  sync(dt);
  updateLightPool();
  updateCam(dt);
  renderFrame(dt);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
