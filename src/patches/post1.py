# -*- coding: utf-8 -*-
"""A single grading pass, a rim light, and a testable rev counter.

POST. One fullscreen pass: a gentle warm split tone, a shadow lift so nothing
crushes to black, a touch of saturation, a soft shoulder so the sun rolls off
instead of clipping flat, a vignette, static grain, and an ordered dither.
The grain and the dither are the crunch, and the dither is what stops the sky
and the fogged distance from contouring into bands.

It renders into a multisampled target, because hard edged flat shaded geometry
needs antialiasing more than smooth geometry does. If the browser cannot give
us a multisampled target, the whole pass is skipped and we draw straight to the
canvas, since an ungraded sharp image beats a graded aliased one.

RIM. A warm edge on the truck's sun facing side, which is what separates it
from the sand without resorting to an outline.

REVS. The gear and rpm simulation was living inside the audio tick, so it only
ran when sound was on and could not be tested at all. It is its own function
now, called every frame.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- revs out of audio
sub("""var TOPS=[9,17,25,33,44];
function audioTick(dt){
  if(!A) return;
  var t=A.ctx.currentTime;
  var speed=S.v.length();

  /* gears, so the note rises and falls instead of droning */
  var g=0; while(g<4 && speed>TOPS[g]) g++;
  var lo=g===0?0:TOPS[g-1];
  var frac=Math.max(0,Math.min(1,(speed-lo)/(TOPS[g]-lo)));
  if(g+1!==A.gear){
    /* a shift you can hear: cut the note, chuff the exhaust */
    A.eg.gain.setTargetAtTime(0.010,t,0.012);
    pop(0.11,300);
    A.gear=g+1;
  }

  if(S.crank>0){ S.crank=Math.max(0,S.crank-dt); }

  var idle=760;
  var target=idle+frac*5600+(S.throttle>0.5?280:0);
  if(S.grounded===0) target=idle+3600+frac*1400;      /* free revs in the air */
  if(S.crank>0.25) target=210+Math.random()*90;        /* still cranking */
  S.rpm += (target-S.rpm)*Math.min(1,dt*(S.throttle>0.4?7.0:3.4));
""",
"""var TOPS=[9,17,25,33,44];

/* The drivetrain note. Kept out of the audio tick so it runs with the sound
   off, and so it can be measured. */
function revs(dt){
  var speed=S.v.length();
  var g=0; while(g<4 && speed>TOPS[g]) g++;
  var lo=g===0?0:TOPS[g-1];
  S.gearFrac=Math.max(0,Math.min(1,(speed-lo)/(TOPS[g]-lo)));
  S.shifted=(g+1!==S.gear); S.gear=g+1;
  if(S.crank>0) S.crank=Math.max(0,S.crank-dt);

  var idle=760;
  var target=idle+S.gearFrac*5600+(S.throttle>0.5?280:0);
  if(S.grounded===0) target=idle+3600+S.gearFrac*1400;   /* free revs in the air */
  if(S.crank>0.25) target=210+Math.random()*90;          /* still cranking */
  S.rpm += (target-S.rpm)*Math.min(1,dt*(S.throttle>0.4?7.0:3.4));
}

function audioTick(dt){
  if(!A) return;
  var t=A.ctx.currentTime;
  var speed=S.v.length();
  var frac=S.gearFrac;
  if(S.shifted){
    /* a shift you can hear: cut the note, chuff the exhaust */
    A.eg.gain.setTargetAtTime(0.010,t,0.012);
    pop(0.11,300);
  }
""")

sub("  steer:0, throttle:0, brake:0, hand:0, rev:0, haptics:true, dip:0, susAct:0, crank:0,",
    "  steer:0, throttle:0, brake:0, hand:0, rev:0, haptics:true, dip:0, susAct:0, crank:0,\n  gearFrac:0, shifted:false,")

sub("    hud(dt); audioTick(dt);", "    revs(dt); hud(dt); audioTick(dt);")

# ---------------------------------------------------------------- rim light
sub("""  var paint =mat(PAL.body);
  var paint2=mat(0x14606b);                 /* a darker teal for the lower body */
  var bone  =mat(PAL.bone);""",
"""  /* A warm edge on the sun facing side. This is what lifts the truck off the
     sand without resorting to an outline, which would fight the facets. */
  function rimify(mm,power,amount){
    mm.onBeforeCompile=function(sh){
      sh.uniforms.uSunV={value:new THREE.Vector3()};
      sh.uniforms.uRimC={value:sc(0xffd9a0)};
      sh.uniforms.uRimP={value:power}; sh.uniforms.uRimA={value:amount};
      mm.userData.shader=sh;
      sh.fragmentShader=sh.fragmentShader
        .replace('#include <common>',
          '#include <common>\\nuniform vec3 uSunV,uRimC;\\nuniform float uRimP,uRimA;')
        .replace('vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;',
          [ 'vec3 Vv = normalize( vViewPosition );',
            'float rim = pow( 1.0 - clamp( dot( normal, Vv ), 0.0, 1.0 ), uRimP );',
            'rim *= smoothstep( -0.25, 0.55, dot( normal, uSunV ) );',
            'vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance + uRimC * rim * uRimA;'
          ].join('\\n'));
    };
    RIMMED.push(mm);
    return mm;
  }
  var paint =rimify(mat(PAL.body),3.0,0.55);
  var paint2=rimify(mat(0x14606b),3.0,0.42);   /* a darker teal for the lower body */
  var bone  =rimify(mat(PAL.bone),3.4,0.34);""")

sub("var corners=[], STRUT=[], GLOW=[];", "var corners=[], STRUT=[], GLOW=[], RIMMED=[];")

sub("""  /* lamps and tail lights come up as the light goes */""",
"""  /* the rim needs the sun in view space, which changes as the camera moves */
  _sunV.copy(SUN_DIR).transformDirection(camera.matrixWorldInverse);
  for(var ri=0;ri<RIMMED.length;ri++){
    var sh=RIMMED[ri].userData.shader;
    if(sh) sh.uniforms.uSunV.value.copy(_sunV);
  }

  /* lamps and tail lights come up as the light goes */""")

sub("var _v3=new THREE.Vector3();", "var _v3=new THREE.Vector3(), _sunV=new THREE.Vector3();")

# ---------------------------------------------------------------- post pass
sub("""function resize(){""",
"""/* ================= grade ================= */
var POST=null;
(function(){
  try{
    if(!renderer.capabilities.isWebGL2 || !THREE.WebGLMultisampleRenderTarget) return;
    var dpr=renderer.getPixelRatio();
    var rt=new THREE.WebGLMultisampleRenderTarget(
      Math.max(2,Math.floor(innerWidth*dpr)), Math.max(2,Math.floor(innerHeight*dpr)),
      {minFilter:THREE.LinearFilter, magFilter:THREE.LinearFilter,
       format:THREE.RGBAFormat, type:THREE.UnsignedByteType,
       stencilBuffer:false, depthBuffer:true});
    rt.samples=4;
    /* r128 honours this and encodes the scene into the target, so the pass
       below works in display space, which is where dither and vignette live */
    rt.texture.encoding=THREE.sRGBEncoding;

    var mtl=new THREE.ShaderMaterial({
      depthTest:false, depthWrite:false,
      uniforms:{
        tDiffuse:{value:rt.texture},
        uRes:{value:new THREE.Vector2(1,1)},
        uTime:{value:0},
        uShadow:{value:new THREE.Vector3(0.93,0.95,1.05)},
        uHigh:{value:new THREE.Vector3(1.06,1.00,0.93)},
        uSat:{value:1.07}, uVig:{value:0.30}, uGrain:{value:0.020}
      },
      vertexShader:[
        'varying vec2 vUv;',
        'void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }'
      ].join('\\n'),
      fragmentShader:[
        'precision highp float;',
        'uniform sampler2D tDiffuse; uniform vec2 uRes; uniform float uTime;',
        'uniform vec3 uShadow,uHigh; uniform float uSat,uVig,uGrain;',
        'varying vec2 vUv;',
        'float bayer2(vec2 a){ a=floor(a); return fract(a.x/2.0 + a.y*a.y*0.75); }',
        'float bayer4(vec2 a){ return bayer2(0.5*a)*0.25 + bayer2(a); }',
        'float h21(vec2 p){ return fract(sin(dot(p,vec2(41.0,289.0)))*43758.5453); }',
        'void main(){',
        '  vec3 c = texture2D(tDiffuse,vUv).rgb;',
        '  float lum = dot(c,vec3(0.2126,0.7152,0.0722));',
        '  c *= mix(uShadow,uHigh,smoothstep(0.0,0.70,lum));',
        '  c = c*0.95 + 0.05*vec3(0.10,0.075,0.11);',      /* lift, never crush */
        '  float l2 = dot(c,vec3(0.2126,0.7152,0.0722));',
        '  c = mix(vec3(l2),c,uSat);',
        '  c = c/(1.0 + max(vec3(0.0), c-0.88)*0.55);',    /* soft shoulder */
        '  vec2 pp = (vUv-0.5)*vec2(uRes.x/uRes.y,1.0);',
        '  c *= clamp(1.0 - uVig*dot(pp,pp), 0.0, 1.0);',
        '  c += (h21(floor(gl_FragCoord.xy*0.5)+uTime) - 0.5)*uGrain;',
        '  c += (bayer4(gl_FragCoord.xy) - 0.46875)*(1.0/255.0);',
        '  gl_FragColor = vec4(c,1.0);',
        '}'
      ].join('\\n')
    });
    var sc2=new THREE.Scene();
    sc2.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),mtl));
    POST={rt:rt, mat:mtl, scene:sc2, cam:new THREE.OrthographicCamera(-1,1,1,-1,0,1)};
  }catch(e){ POST=null; }
})();

var grainT=0;
function renderFrame(dt){
  if(!POST){ renderer.render(scene,camera); return; }
  grainT+=dt||0.016;
  POST.mat.uniforms.uTime.value=Math.floor(grainT*11);   /* hold the grain, do not shimmer */
  renderer.setRenderTarget(POST.rt);
  renderer.render(scene,camera);
  renderer.setRenderTarget(null);
  renderer.render(POST.scene,POST.cam);
}

function resize(){""")

sub("""  renderer.setSize(w,h,false);
  camera.aspect=w/h;
  camera.updateProjectionMatrix();""",
"""  renderer.setSize(w,h,false);
  camera.aspect=w/h;
  camera.updateProjectionMatrix();
  if(POST){
    var dpr=renderer.getPixelRatio();
    POST.rt.setSize(Math.max(2,Math.floor(w*dpr)),Math.max(2,Math.floor(h*dpr)));
    POST.mat.uniforms.uRes.value.set(w,h);
  }""")

sub("  renderer.render(scene,camera);\n}\n\n/* ================= grade ================= */",
    "  renderFrame(dt);\n}\n\n/* ================= grade ================= */")

# the debug tick should draw through the same path
sub("      sync(1/60); updateCam(1/60); renderer.render(scene,camera);",
    "      sync(1/60); updateCam(1/60); revs(1/60); renderFrame(1/60);")

# expose the audio entry point so the graph can be built in a test
sub("    TOD:TOD,TIMES:TIMES,applyTime:applyTime,drawMap:drawMap,IN:IN,",
    "    TOD:TOD,TIMES:TIMES,applyTime:applyTime,drawMap:drawMap,IN:IN,\n    audioOn:audioOn,getAudio:function(){return A;},revs:revs,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
