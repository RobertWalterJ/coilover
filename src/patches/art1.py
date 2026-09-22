# -*- coding: utf-8 -*-
"""Art direction pass one.

The big levers, in the order they matter:
  1. Terrain triangle count down by two thirds, with the grid jittered and the
     quad diagonals flipped, so facets read as facets instead of as noise and
     the heightmap stops showing its herringbone grain.
  2. A real golden hour rig: one low warm key, a cool hemisphere fill so
     shadows go violet rather than grey, and a dim cool bounce. No ambient.
     Plus the r128 colour space rules, which are the reason a good palette
     comes out washed out otherwise.
  3. The sky as a dithered gradient shader. Banding in a big soft sky is the
     single loudest tell of a browser 3D scene.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

def cut(start, end):
    """return the block from start marker up to (not including) end marker"""
    a = s.index(start); b = s.index(end)
    return s[a:b]

# ================= palette constants =================
sub("""/* ---- world ---- */
var WORLD=512, HALF=WORLD/2, GRID=2.0;      /* metres, and the mesh cell size */
var RIM=196;                                 /* the basin wall starts here */""",
"""/* ---- world ---- */
var WORLD=560, HALF=WORLD/2, GRID=4.0;      /* metres, and the mesh cell size */
var RIM=196;                                 /* the basin wall starts here */

/* Colour space, r128. Material and light colours feed linear lighting maths so
   they must be converted. Fog and the sky shader are composited in display
   space, so those stay as authored. Getting this backwards is what makes a
   good palette look washed out. */
function sc(hex){ return new THREE.Color(hex).convertSRGBToLinear(); }

var PAL={
  low:0xb4703f, mid:0xd69a5c, high:0xedc48a, rock:0x8c5340, playa:0xd8cbb0,
  scrub:0x6e7048, fog:0xe3ac83,
  sun:0xffc98a, skyFill:0x7fa0d8, groundFill:0xc87f4a, bounce:0x6e7fa8,
  body:0x2f7a86, bone:0xf0e6d2, spring:0xe0553f, tyre:0x2b2733, wheel:0xd9cfc0,
  dust:0xe8c79a
};
/* elevation 9.3 degrees. Shadow length is height over tan(elevation), so a
   two metre truck throws a twelve metre shadow. That rake is golden hour. */
var SUN_DIR=new THREE.Vector3(-120,22,60).normalize();""")

# ================= renderer =================
sub("""renderer.outputEncoding=THREE.sRGBEncoding;""",
    """renderer.outputEncoding=THREE.sRGBEncoding;
/* No filmic curve. It would desaturate exactly the amber to cream range the
   whole palette is built on, and the colours here are already final. */
renderer.toneMapping=THREE.NoToneMapping;""")

# ================= fog =================
sub("""var FOG=new THREE.Color(0xe0925c);
scene.fog=new THREE.FogExp2(FOG.getHex(),0.0040);
camera=new THREE.PerspectiveCamera(64,1,0.4,1400);""",
"""var FOG=new THREE.Color(PAL.fog);
/* Linear, not exponential: it guarantees an unfogged near field, so the truck
   and the dunes you are actually reading keep their full colour. Far is past
   the terrain edge so distant ground never fully dissolves into the sky. */
scene.fog=new THREE.Fog(PAL.fog,90,520);
camera=new THREE.PerspectiveCamera(54,1,0.4,1600);""")

# ================= sky =================
old_sky = cut("/* ================= sky, sun, backdrop ================= */",
              "var sun=new THREE.DirectionalLight")
new_sky = '''/* ================= sky, sun, backdrop ================= */
var skyMat;
(function(){
  /* A canvas gradient bands badly and cannot carry a sun. Do it in a shader,
     with an ordered dither so the shallow gradients never contour. */
  skyMat=new THREE.ShaderMaterial({
    side:THREE.BackSide, depthWrite:false, fog:false,
    uniforms:{
      uHorizon:{value:new THREE.Color(0xf5c795)},   /* raw, display space */
      uLow    :{value:new THREE.Color(0xefa875)},
      uMid    :{value:new THREE.Color(0xc97f6e)},
      uHigh   :{value:new THREE.Color(0x8e7290)},
      uZenith :{value:new THREE.Color(0x54658c)},
      uSunCore:{value:new THREE.Color(0xfff0cf)},
      uSunHalo:{value:new THREE.Color(0xffb871)},
      uSunDirW:{value:SUN_DIR.clone()}
    },
    vertexShader:[
      'varying vec3 vDirW;',
      'void main(){',
      '  vec4 wp = modelMatrix * vec4( position, 1.0 );',
      '  vDirW = wp.xyz - cameraPosition;',
      '  gl_Position = projectionMatrix * viewMatrix * wp;',
      '}'].join('\\n'),
    fragmentShader:[
      'precision highp float;',
      'uniform vec3 uHorizon,uLow,uMid,uHigh,uZenith,uSunCore,uSunHalo,uSunDirW;',
      'varying vec3 vDirW;',
      'float bayer2(vec2 a){ a=floor(a); return fract( a.x/2.0 + a.y*a.y*0.75 ); }',
      'float bayer4(vec2 a){ return bayer2(0.5*a)*0.25 + bayer2(a); }',
      'void main(){',
      '  vec3 d = normalize(vDirW);',
      '  float h = clamp(d.y,-0.15,1.0);',
      '  vec3 sky = uHorizon;',
      '  sky = mix(sky,uLow,    smoothstep(-0.02,0.07,h));',
      '  sky = mix(sky,uMid,    smoothstep( 0.05,0.21,h));',
      '  sky = mix(sky,uHigh,   smoothstep( 0.18,0.46,h));',
      '  sky = mix(sky,uZenith, smoothstep( 0.42,0.95,h));',
      '  float sd = max(dot(d,uSunDirW),0.0);',
      '  sky += uSunCore * pow(sd,260.0) * 1.25;',
      '  sky += uSunHalo * pow(sd,  9.0) * 0.34;',
      '  sky += uSunHalo * pow(sd,  2.0) * 0.09;',
      '  sky += (bayer4(gl_FragCoord.xy) - 0.46875) * (1.4/255.0);',
      '  gl_FragColor = vec4(sky,1.0);',
      '}'].join('\\n')
  });
  var sky=new THREE.Mesh(new THREE.SphereGeometry(900,32,16),skyMat);
  sky.frustumCulled=false; sky.renderOrder=-1;
  scene.add(sky);
  window.__sky=sky;

  /* distant peaks so the rim has something behind it */
  var pk=new THREE.Group();
  for(var i=0;i<22;i++){
    var a=i/22*Math.PI*2+0.21, r=430+vnoise(i*3.1,0)*130;
    var hgt=64+vnoise(i*1.7,5.5)*95;
    var cone=new THREE.Mesh(new THREE.ConeGeometry(hgt*0.85,hgt,5),
      new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,flatShading:true,
        color:new THREE.Color(0x8b5f63).lerp(FOG,0.34).convertSRGBToLinear()}));
    cone.position.set(Math.sin(a)*r, hgt*0.34, Math.cos(a)*r);
    cone.rotation.y=a; pk.add(cone);
  }
  scene.add(pk);
})();

'''
s = s.replace(old_sky, new_sky, 1); n += 1

# ================= lights =================
old_light = cut("var sun=new THREE.DirectionalLight", "/* ================= scatter")
new_light = '''var sun=new THREE.DirectionalLight(sc(PAL.sun),2.1);
sun.castShadow=true;
var SM=mobile?1024:2048;
var SHADOW_H=mobile?40:60;                   /* half extent, metres */
sun.shadow.mapSize.set(SM,SM);
sun.shadow.camera.near=1; sun.shadow.camera.far=340;
sun.shadow.camera.left=-SHADOW_H; sun.shadow.camera.right=SHADOW_H;
sun.shadow.camera.top=SHADOW_H; sun.shadow.camera.bottom=-SHADOW_H;
/* A nine degree sun means most ground is near grazing to the light, the worst
   case for acne. Do the work with normalBias: a big depth bias would detach
   shadows from the hard facet edges, which looks broken on faceted geometry. */
sun.shadow.bias=-0.0004; sun.shadow.normalBias=0.07;
scene.add(sun); scene.add(sun.target);

/* The cool fill is what makes a shadow violet instead of grey, and warm light
   against violet shadow is the entire golden hour read. No AmbientLight: it
   raises the black point flat and removes all form from the shadow side. */
scene.add(new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.55));
var bounce=new THREE.DirectionalLight(sc(PAL.bounce),0.28);
bounce.position.copy(SUN_DIR).multiplyScalar(-1).setY(0.42).normalize().multiplyScalar(120);
scene.add(bounce);

/* Snap the shadow camera to whole texels or the shadow edges crawl and
   shimmer every frame as it follows the truck. */
var _sr=new THREE.Vector3(), _su=new THREE.Vector3(), _sq=new THREE.Vector3();
_sr.set(0,1,0).cross(SUN_DIR).normalize();
_su.crossVectors(SUN_DIR,_sr).normalize();
var TEXEL=(2*SHADOW_H)/SM;
function aimSun(at){
  var a=Math.round(at.dot(_sr)/TEXEL)*TEXEL;
  var b=Math.round(at.dot(_su)/TEXEL)*TEXEL;
  var c=at.dot(SUN_DIR);
  _sq.copy(_sr).multiplyScalar(a).addScaledVector(_su,b).addScaledVector(SUN_DIR,c);
  sun.target.position.copy(_sq);
  sun.position.copy(_sq).addScaledVector(SUN_DIR,170);
  sun.target.updateMatrixWorld();
}

'''
s = s.replace(old_light, new_light, 1); n += 1

# ================= terrain =================
old_terr = cut("var C_LAKE=new THREE.Color(0xd9cdb2)", "/* ================= sky, sun, backdrop")
new_terr = '''var terrainMat;
(function(){
  var N=Math.round(WORLD/GRID), V=N+1;
  var pos=new Float32Array(V*V*3);
  var xz=new Float32Array(V*V*2);

  /* Jitter x and z before sampling height. This is the single biggest thing
     separating a landscape from an obvious heightmap: it kills the regular
     grid without touching the physics, which reads the analytic function. */
  for(var j=0;j<V;j++) for(var i=0;i<V;i++){
    var edge=(i===0||j===0||i===N||j===N);
    var x=-HALF+i*GRID, z=-HALF+j*GRID;
    if(!edge){
      x += (hash2(i*1.7,j*3.1)-0.5)*GRID*0.70;
      z += (hash2(i*5.3,j*2.9)-0.5)*GRID*0.70;
    }
    var k=(j*V+i);
    pos[k*3]=x; pos[k*3+1]=height(x,z); pos[k*3+2]=z;
    xz[k*2]=x; xz[k*2+1]=z;
  }

  /* Pick each quad's diagonal along the smaller height difference. A uniform
     diagonal puts a herringbone grain across the whole basin; choosing it this
     way also keeps dune crests crisp instead of sawtoothed. */
  var idx=new Uint32Array(N*N*6), t=0;
  for(var jj=0;jj<N;jj++) for(var ii=0;ii<N;ii++){
    var a=jj*V+ii, b=a+1, d=a+V, e2=d+1;
    if(Math.abs(pos[a*3+1]-pos[e2*3+1]) <= Math.abs(pos[b*3+1]-pos[d*3+1])){
      idx[t++]=a; idx[t++]=d; idx[t++]=e2;
      idx[t++]=a; idx[t++]=e2; idx[t++]=b;
    }else{
      idx[t++]=a; idx[t++]=d; idx[t++]=b;
      idx[t++]=b; idx[t++]=d; idx[t++]=e2;
    }
  }

  var g2=new THREE.BufferGeometry();
  g2.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g2.setIndex(new THREE.BufferAttribute(idx,1));
  g2.computeVertexNormals();

  terrainMat=new THREE.MeshPhongMaterial({
    color:0xffffff, specular:0x000000, shininess:0, flatShading:true});

  /* Colour from height and slope in the shader, so there is no vertex colour
     buffer and the mesh stays indexed. The patch tint is quantised to a grid
     that deliberately does not line up with the triangles, so two frequencies
     overlap and large sand flats stop reading as dead. */
  terrainMat.onBeforeCompile=function(sh){
    sh.uniforms.uLow  ={value:sc(PAL.low)};
    sh.uniforms.uMid  ={value:sc(PAL.mid)};
    sh.uniforms.uHigh ={value:sc(PAL.high)};
    sh.uniforms.uRock ={value:sc(PAL.rock)};
    sh.uniforms.uPlaya={value:sc(PAL.playa)};
    sh.uniforms.uCell ={value:GRID};
    terrainMat.userData.shader=sh;
    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPos;')
      .replace('#include <begin_vertex>',
               '#include <begin_vertex>\\n vWPos=(modelMatrix*vec4(transformed,1.0)).xyz;');
    sh.fragmentShader=sh.fragmentShader
      .replace('#include <common>',[
        '#include <common>',
        'varying vec3 vWPos;',
        'uniform vec3 uLow,uMid,uHigh,uRock,uPlaya;',
        'uniform float uCell;',
        'float hash21(vec2 p){ p=fract(p*vec2(123.34,345.45)); p+=dot(p,p+34.345); return fract(p.x*p.y); }'
      ].join('\\n'))
      .replace('#include <color_fragment>',[
        'vec3 fn = normalize(cross(dFdx(vWPos),dFdy(vWPos)));',
        'float slope = 1.0 - abs(fn.y);',
        'float wy = vWPos.y;',
        'vec3 c = mix(uLow,uMid,smoothstep(-11.0,-2.0,wy));',
        'c = mix(c,uHigh,smoothstep(1.0,13.0,wy));',
        'c = mix(c,uPlaya,smoothstep(-3.4,-4.4,wy)*(1.0-smoothstep(0.05,0.13,slope)));',
        'c = mix(c,uRock,smoothstep(0.34,0.60,slope));',
        'float nq = hash21(floor(vWPos.xz/uCell));',
        'c *= 0.94 + 0.12*nq;',
        'diffuseColor.rgb = c;'
      ].join('\\n'));
  };

  var mesh=new THREE.Mesh(g2,terrainMat);
  /* Dunes do not cast. A nine degree sun already bands them beautifully
     through N dot L, for free and with no acne, and keeping a forty thousand
     triangle sheet out of the shadow pass pays for everything else. */
  mesh.castShadow=false; mesh.receiveShadow=true;
  scene.add(mesh);
})();

'''
s = s.replace(old_terr, new_terr, 1); n += 1

# whoops need a wavelength the mesh can actually resolve at a four metre cell
sub("""  /* the whoop run: 9 m wavelength, straight, ~1.9 m peak to trough */
  var wc=band(z,-48,10,8)*band(x,26,86,26);
  h += Math.sin(x*0.698)*0.95*wc;""",
    """  /* The whoop run. Sixteen metre wavelength so the four metre mesh resolves
     it, which matters because what you see has to match what you feel. */
  var wc=band(z,-48,11,9)*band(x,26,92,28);
  h += Math.sin(x*0.393)*1.15*wc;""")

# the rim formula runs away past the mesh edge, so cap it
sub("""  if(r>RIM) h += Math.pow((r-RIM)*0.052,2.2)*11;""",
    """  if(r>RIM) h += Math.min(60,Math.pow((r-RIM)*0.052,2.2)*11);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
