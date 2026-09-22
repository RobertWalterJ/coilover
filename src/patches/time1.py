# -*- coding: utf-8 -*-
"""Time of day, plus the two ember.lite qualities that survive daylight.

Five hours you can pick from, each one a full lighting contract: sun angle and
colour, hemisphere fill, all five sky gradient stops, fog, and how much
anything emissive glows. They cross fade rather than snap. There is also an
optional slow drift, off by default. Note the distinction: a sun you position
is a camera setting, a sun that moves on its own could be read as a clock, so
drifting is opt in and nothing anywhere depends on it.

The dusk stops are the ones measured off ember.lite's own frames: deep royal
blue at the zenith running to dusty magenta at the horizon, which is a 96
degree hue rotation and the reason that sky looks like something rather than
like a gradient.

Also here: nearest filtered texel crunch on the sand, which is the loudest
single thing in all of your references and works at any hour, and headlights
that come up as the light goes.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- the table
sub("""/* elevation 9.3 degrees. Shadow length is height over tan(elevation), so a
   two metre truck throws a twelve metre shadow. That rake is golden hour. */
var SUN_DIR=new THREE.Vector3(-120,22,60).normalize();""",
"""/* Sun elevation drives shadow length, which is height over tan(elevation).
   At nine degrees a two metre truck throws a twelve metre shadow. */
var SUN_DIR=new THREE.Vector3(-120,22,60).normalize();

/* Each entry is a complete lighting contract. sky stops run horizon first. */
var TIMES=[
  { name:'Dawn',
    dir:[-70,16,-130], sun:0xffc0b0, sunI:1.25, hemiS:0x9fb4e8, hemiG:0x7d6a68, hemiI:0.92,
    sky:[0xe9c3b4,0xd9a89f,0xa98aa8,0x6d6f9c,0x3b4a80], fog:0xd8b0a4, fogN:60, fogF:470,
    glow:0.30, amb:0x101828 },
  { name:'Morning',
    dir:[-90,58,40], sun:0xfff0d2, sunI:1.95, hemiS:0xa9c6ef, hemiG:0xb08050, hemiI:0.85,
    sky:[0xf2e0c2,0xe3d0ae,0xb9c2cf,0x82a2cc,0x4d7ec4], fog:0xe6d6b8, fogN:110, fogF:600,
    glow:0.00, amb:0x000000 },
  { name:'Golden',
    dir:[-120,22,60], sun:0xffc98a, sunI:1.85, hemiS:0x7fa0d8, hemiG:0xc87f4a, hemiI:0.80,
    sky:[0xf5c795,0xefa875,0xc97f6e,0x8e7290,0x54658c], fog:0xe8a271, fogN:90, fogF:520,
    glow:0.12, amb:0x000000 },
  { name:'Dusk',
    dir:[-150,7,20], sun:0xff9a6a, sunI:1.05, hemiS:0x6b6ba8, hemiG:0x7a4a48, hemiI:0.70,
    sky:[0x7b3965,0x693b6d,0x513d74,0x152873,0x0a2574], fog:0x8f5a6a, fogN:50, fogF:430,
    glow:0.72, amb:0x0c1030 },
  { name:'Night',
    dir:[-150,26,20], sun:0x7f92c8, sunI:0.42, hemiS:0x2a3560, hemiG:0x201824, hemiI:0.42,
    sky:[0x1c144e,0x06094c,0x00002d,0x000018,0x000010], fog:0x241c46, fogN:35, fogF:330,
    glow:1.00, amb:0x0a0c20 }
];
var TOD={ i:2, from:2, to:2, k:1, drift:false, glow:0.12, night:0 };""")

# ---------------------------------------------------------------- applier
sub("""scene.add(new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.80));
var bounce=new THREE.DirectionalLight(sc(PAL.bounce),0.28);
bounce.position.copy(SUN_DIR).multiplyScalar(-1).setY(0.42).normalize().multiplyScalar(120);
scene.add(bounce);""",
"""var hemi=new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.80);
scene.add(hemi);
var bounce=new THREE.DirectionalLight(sc(PAL.bounce),0.28);
bounce.position.copy(SUN_DIR).multiplyScalar(-1).setY(0.42).normalize().multiplyScalar(120);
scene.add(bounce);
var ambient=new THREE.AmbientLight(0x000000,1.0);
scene.add(ambient);

var _cA=new THREE.Color(), _cB=new THREE.Color(), _dA=new THREE.Vector3(), _dB=new THREE.Vector3();
function lerpHex(a,b,k,out){ out.setHex(a); _cB.setHex(b); return out.lerp(_cB,k); }

/* Rebuild every light, the sky and the fog from a blend of two entries. */
function applyTime(k){
  var A=TIMES[TOD.from], B=TIMES[TOD.to];
  _dA.fromArray(A.dir).normalize(); _dB.fromArray(B.dir).normalize();
  SUN_DIR.copy(_dA).lerp(_dB,k).normalize();
  _sr.set(0,1,0).cross(SUN_DIR).normalize();
  _su.crossVectors(SUN_DIR,_sr).normalize();

  sun.color.copy(lerpHex(A.sun,B.sun,k,_cA)).convertSRGBToLinear();
  sun.intensity=A.sunI+(B.sunI-A.sunI)*k;
  hemi.color.copy(lerpHex(A.hemiS,B.hemiS,k,_cA)).convertSRGBToLinear();
  hemi.groundColor.copy(lerpHex(A.hemiG,B.hemiG,k,_cA)).convertSRGBToLinear();
  hemi.intensity=A.hemiI+(B.hemiI-A.hemiI)*k;
  ambient.color.copy(lerpHex(A.amb,B.amb,k,_cA)).convertSRGBToLinear();
  bounce.intensity=0.28*(A.sunI+(B.sunI-A.sunI)*k)/1.85;

  var u=skyMat.uniforms, names=['uHorizon','uLow','uMid','uHigh','uZenith'];
  for(var i=0;i<5;i++) lerpHex(A.sky[i],B.sky[i],k,u[names[i]].value);
  u.uSunDirW.value.copy(SUN_DIR);
  lerpHex(A.sun,B.sun,k,u.uSunHalo.value);

  lerpHex(A.fog,B.fog,k,scene.fog.color);
  scene.fog.near=A.fogN+(B.fogN-A.fogN)*k;
  scene.fog.far =A.fogF+(B.fogF-A.fogF)*k;
  FOG.copy(scene.fog.color);

  TOD.glow=A.glow+(B.glow-A.glow)*k;
  TOD.night=Math.max(0,(TOD.glow-0.2)/0.8);
  if(stars) stars.material.opacity=Math.min(1,TOD.night*1.25);
  headL.intensity=headR.intensity=TOD.night*2.6;
}""")

# the shadow basis has to exist before applyTime runs
sub("""/* Snap the shadow camera to whole texels or the shadow edges crawl and
   shimmer every frame as it follows the truck. */
var _sr=new THREE.Vector3(), _su=new THREE.Vector3(), _sq=new THREE.Vector3();
_sr.set(0,1,0).cross(SUN_DIR).normalize();
_su.crossVectors(SUN_DIR,_sr).normalize();""",
"""/* Snap the shadow camera to whole texels or the shadow edges crawl and
   shimmer every frame as it follows the truck. */
var _sr=new THREE.Vector3(0,0,1), _su=new THREE.Vector3(1,0,0), _sq=new THREE.Vector3();
_sr.set(0,1,0).cross(SUN_DIR).normalize();
_su.crossVectors(SUN_DIR,_sr).normalize();""")

# ---------------------------------------------------------------- stars
sub("""  /* distant peaks so the rim has something behind it */""",
"""  /* stars, only ever visible once the sky goes dark enough to hold them */
  var sp=[], sc2=[];
  for(var si=0;si<420;si++){
    var th=Math.random()*Math.PI*2, ph=Math.acos(Math.random()*0.94+0.03);
    var R=860;
    sp.push(Math.sin(ph)*Math.cos(th)*R, Math.cos(ph)*R, Math.sin(ph)*Math.sin(th)*R);
    var b=0.55+Math.random()*0.45;
    sc2.push(b,b*0.97,b*0.9);
  }
  var sg=new THREE.BufferGeometry();
  sg.setAttribute('position',new THREE.Float32BufferAttribute(sp,3));
  sg.setAttribute('color',new THREE.Float32BufferAttribute(sc2,3));
  stars=new THREE.Points(sg,new THREE.PointsMaterial({
    size:2.6,sizeAttenuation:false,vertexColors:true,transparent:true,opacity:0,
    depthWrite:false,fog:false}));
  stars.frustumCulled=false; scene.add(stars);

  /* distant peaks so the rim has something behind it */""")

sub("""/* ================= sky, sun, backdrop ================= */
var skyMat;""",
    """/* ================= sky, sun, backdrop ================= */
var skyMat, stars=null;""")

# ---------------------------------------------------------------- headlights
sub("""/* ================= dust ================= */""",
"""/* Headlights. No shadow casting: two more shadow maps is not worth it on a
   phone, and the pool of light on the sand is what sells it anyway. */
var headL=new THREE.SpotLight(0xfff2cf,0,72,0.62,0.45,1.2);
var headR=new THREE.SpotLight(0xfff2cf,0,72,0.62,0.45,1.2);
headL.castShadow=headR.castShadow=false;
scene.add(headL,headR,headL.target,headR.target);

/* ================= dust ================= */""")

sub("""  /* keep the shadow box on the truck */
  sun.position.set(S.p.x-58, S.p.y+52, S.p.z-36);
  sun.target.position.copy(S.p);""",
"""  /* headlights sit on the nose and look where the truck is pointed */
  if(TOD.night>0.01){
    _v3.set(-0.62,0.22,2.30).applyQuaternion(S.q).add(S.p); headL.position.copy(_v3);
    _v3.set( 0.62,0.22,2.30).applyQuaternion(S.q).add(S.p); headR.position.copy(_v3);
    _v3.set(-1.5,-1.4,26).applyQuaternion(S.q).add(S.p); headL.target.position.copy(_v3);
    _v3.set( 1.5,-1.4,26).applyQuaternion(S.q).add(S.p); headR.target.position.copy(_v3);
    headL.target.updateMatrixWorld(); headR.target.updateMatrixWorld();
  }

  /* aimSun snaps the shadow camera to whole texels, which stops the shadow
     edges crawling as it follows the truck. It was defined but never called. */
  aimSun(S.p);""")

# ---------------------------------------------------------------- texel crunch
sub("""    sh.uniforms.uCell ={value:GRID};""",
"""    sh.uniforms.uCell ={value:GRID};
    sh.uniforms.uDetail={value:detailTex};""")

sub("""        'uniform float uCell;',""",
    """        'uniform float uCell;',
        'uniform sampler2D uDetail;',""")

sub("""        'float nq = hash21(floor(vWPos.xz/uCell));',
        'c *= 0.94 + 0.12*nq;',""",
"""        'float nq = hash21(floor(vWPos.xz/uCell));',
        'c *= 0.94 + 0.12*nq;',
        // Two nearest filtered lookups at different scales. The crunchy texel
        // grid is the loudest thing in the reference work, and the second
        // octave stops the first one reading as obvious tiling.
        'float d1 = texture2D(uDetail, vWPos.xz*0.084).r;',
        'float d2 = texture2D(uDetail, vWPos.xz*0.0213 + 0.37).r;',
        'c *= 0.80 + 0.26*d1 + 0.16*d2;',""")

sub("""var terrainMat;
(function(){""",
"""var terrainMat;
/* A small quantised noise tile, magnified with no filtering at all. */
var detailTex=(function(){
  var N=64, cv=document.createElement('canvas'); cv.width=cv.height=N;
  var g=cv.getContext('2d'), img=g.createImageData(N,N);
  for(var j=0;j<N;j++) for(var i=0;i<N;i++){
    var v=(vnoise(i*0.34,j*0.34)*0.62 + vnoise(i*0.9,j*0.9)*0.38);
    v=Math.round(v*5)/5;                        /* five steps, deliberately */
    var q=Math.round(120+v*135), k=(j*N+i)*4;
    img.data[k]=img.data[k+1]=img.data[k+2]=q; img.data[k+3]=255;
  }
  g.putImageData(img,0,0);
  var t=new THREE.CanvasTexture(cv);
  t.magFilter=THREE.NearestFilter; t.minFilter=THREE.NearestMipmapNearestFilter;
  t.wrapS=t.wrapT=THREE.RepeatWrapping; t.anisotropy=1; t.generateMipmaps=true;
  return t;
})();
(function(){""")

# ---------------------------------------------------------------- controls
sub("""    <button class="go ghost" id="b-cam">Camera</button>""",
    """    <button class="go ghost" id="b-cam">Camera</button>
    <button class="go ghost" id="b-time">Light: Golden</button>
    <button class="go ghost" id="b-drift">Let it drift: off</button>""")

sub("""document.getElementById('b-sound').addEventListener('click',function(){""",
"""document.getElementById('b-time').addEventListener('click',function(){
  TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0;
  this.textContent='Light: '+TIMES[TOD.to].name;
});
document.getElementById('b-drift').addEventListener('click',function(){
  TOD.drift=!TOD.drift; this.textContent='Let it drift: '+(TOD.drift?'on':'off');
});
document.getElementById('b-sound').addEventListener('click',function(){""")

# ---------------------------------------------------------------- tick
sub("""  sync(dt);
  updateCam(dt);""",
"""  if(TOD.k<1){ TOD.k=Math.min(1,TOD.k+dt*0.55); applyTime(TOD.k); }
  else if(TOD.drift){
    TOD.k+=dt*0.0055;                       /* a full hour every three minutes */
    if(TOD.k>=1){ TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; }
    applyTime(TOD.k);
  }
  sync(dt);
  updateCam(dt);""")

sub("""resize();
S.camMode=0;""",
    """resize();
applyTime(1);
S.camMode=0;""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
