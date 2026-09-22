# -*- coding: utf-8 -*-
"""The ember.lite pass.

You settled it: ember.lite is the target, and the other references only count
where they agree with it. So this stops averaging four things and builds three
properties that ember.lite actually has and Coilover did not.

ONE. Tone stops per time of day. The band lift and gain were single global
numbers shared by all five lights, which is why Night collapsed into one band
and Morning blew out. Each time now carries its own lift, gain, saturation and
exposure, crossfaded like everything else.

TWO. Aerial perspective. The frame measured 69 percent of the ground inside a
single value bucket, which is the muddiness: near ground and far ridge were the
same. Low lying ground now fills with haze at distance while ridges stay clear,
so the landscape stacks into planes the way those frames do. The haze reads off
the sky's own low colour, so distance always resolves toward the sky rather
than toward a flat wash.

THREE. The glow. There was no bloom anywhere, which for a sunset game named
after a spring is a strange omission. A proper bright pass and separable blur
at half resolution, written against plain shader materials so it stays inside
the three.js build this has to run on. Sun, sky near the horizon, headlights at
night and the rim light on the truck now all carry a halo. The threshold rides
the time of day, so Night glows from almost nothing and Morning needs real
brightness to bloom.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:100].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# =================================================================== 1. stops
sub("""    glow:0.30, amb:0x101828 },""",
    """    glow:0.30, amb:0x101828,
    lift:0.34, gain:2.15, sat:1.10, expo:1.02, bloom:0.42, bthr:0.62,
    haze:0x caa8b8 , hazeA:0.52 },""".replace('0x caa8b8 ', '0xcaa8b8'))
sub("""    glow:0.00, amb:0x000000 },
  { name:'Golden',""",
    """    glow:0.00, amb:0x000000,
    lift:0.52, gain:1.72, sat:1.02, expo:0.96, bloom:0.20, bthr:0.86,
    haze:0xd3d0dc, hazeA:0.44 },
  { name:'Golden',""")
sub("""    glow:0.16, amb:0x000000 },""",
    """    glow:0.16, amb:0x000000,
    lift:0.40, gain:2.10, sat:1.12, expo:1.03, bloom:0.46, bthr:0.66,
    haze:0xc38a92, hazeA:0.58 },""")
sub("""    glow:0.72, amb:0x0c1030 },""",
    """    glow:0.72, amb:0x0c1030,
    lift:0.26, gain:2.45, sat:1.16, expo:1.06, bloom:0.72, bthr:0.46,
    haze:0x8c5f7c, hazeA:0.62 },""")
sub("""    glow:1.00, amb:0x0a0c20 }""",
    """    glow:1.00, amb:0x0a0c20,
    lift:0.10, gain:3.30, sat:1.08, expo:1.14, bloom:0.90, bthr:0.24,
    haze:0x2b2450, hazeA:0.50 }""")

# ------------------------------------------------- haze and bloom uniforms
sub("""  uGrainAmt  :{value:1.35},   /* moves shS a third of a band at one sigma */""",
"""  uHazeC     :{value:new THREE.Color()},
  uHazeA     :{value:0.55},
  uHazeLo    :{value:-2.0}, uHazeHi:{value:26.0},
  uHazeN     :{value:34.0}, uHazeF:{value:290.0},
  uGrainAmt  :{value:1.35},   /* moves shS a third of a band at one sigma */""")

sub("""    sh.uniforms.uBandDebug=STYLE_U.uBandDebug;""",
"""    sh.uniforms.uBandDebug=STYLE_U.uBandDebug;
    sh.uniforms.uHazeC=STYLE_U.uHazeC; sh.uniforms.uHazeA=STYLE_U.uHazeA;
    sh.uniforms.uHazeLo=STYLE_U.uHazeLo; sh.uniforms.uHazeHi=STYLE_U.uHazeHi;
    sh.uniforms.uHazeN=STYLE_U.uHazeN; sh.uniforms.uHazeF=STYLE_U.uHazeF;""")

# world position on EVERY styled material, not only the grained ground, because
# the haze needs to know how high off the desert floor a surface sits
sub("""    if(opts.grain){
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')
        .replace('#include <begin_vertex>',
                 '#include <begin_vertex>\\nvWPosS=(modelMatrix*vec4(transformed,1.0)).xyz;');
    }""",
"""    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')
      .replace('#include <begin_vertex>',
               '#include <begin_vertex>\\nvWPosS=(modelMatrix*vec4(transformed,1.0)).xyz;');""")

sub("""      'const vec3 LUMA_S = vec3(0.2126,0.7152,0.0722);'];
    if(opts.grain) head.push('varying vec3 vWPosS;',
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');""",
"""      'const vec3 LUMA_S = vec3(0.2126,0.7152,0.0722);',
      'varying vec3 vWPosS;',
      'uniform vec3 uHazeC;',
      'uniform float uHazeA,uHazeLo,uHazeHi,uHazeN,uHazeF;'];
    if(opts.grain) head.push(
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');""")

# dS is needed by the haze whether or not this material carries grain
sub("""    var body=[
      'vec3 albS = max( diffuseColor.rgb, vec3(1e-4) );',""",
"""    var body=[
      'float dS = length( vViewPosition );',
      'vec3 albS = max( diffuseColor.rgb, vec3(1e-4) );',""")
sub("""      'float dS = length( vViewPosition );',
      'float w0S = 1.0 - smoothstep( 5.0, 18.0, dS );',""",
"""      'float w0S = 1.0 - smoothstep( 5.0, 18.0, dS );',""")

# the haze itself, applied to the banded colour just before the rim light
sub("""      'pcS = mix( pcS, pcS * uSunTint, step( 2.5, qS ) * 0.28 );');""",
"""      'pcS = mix( pcS, pcS * uSunTint, step( 2.5, qS ) * 0.28 );',
      /* Aerial perspective. Low ground fills with haze as it recedes and
         ridges stay clear, so the landscape stacks into planes instead of
         reading as one continuous sheet of the same value. */
      'float hzH = 1.0 - smoothstep( uHazeLo, uHazeHi, vWPosS.y );',
      'float hzD = smoothstep( uHazeN, uHazeF, dS );',
      'pcS = mix( pcS, uHazeC, hzD * ( 0.30 + 0.70 * hzH ) * uHazeA );');""")

# --------------------------------------------------------------- applyTime
sub("""  TOD.glow=A.glow+(B.glow-A.glow)*k;""",
"""  /* tone stops, per time of day, so no light collapses or blows out */
  var LF=function(a,b){ return a+(b-a)*k; };
  STYLE_U.uShadeLift.value=LF(A.lift,B.lift);
  STYLE_U.uShadeGain.value=LF(A.gain,B.gain);
  lerpHex(A.haze,B.haze,k,STYLE_U.uHazeC.value); STYLE_U.uHazeC.value.convertSRGBToLinear();
  STYLE_U.uHazeA.value=LF(A.hazeA,B.hazeA);
  if(POST){
    POST.mat.uniforms.uSat.value=LF(A.sat,B.sat);
    POST.mat.uniforms.uExpo.value=LF(A.expo,B.expo);
    POST.mat.uniforms.uBloom.value=LF(A.bloom,B.bloom);
    BLOOM.thr.uniforms.uThr.value=LF(A.bthr,B.bthr);
  }

  TOD.glow=A.glow+(B.glow-A.glow)*k;""")

# ===================================================================== bloom
sub("""        uSat:{value:1.08}, uVig:{value:0.22}, uGrain:{value:0.075},""",
"""        uSat:{value:1.08}, uVig:{value:0.22}, uGrain:{value:0.075},
        uExpo:{value:1.0}, uBloom:{value:0.46}, tBloom:{value:null},""")

sub("""        'uniform vec3 uShadow,uHigh; uniform float uSat,uVig,uGrain,uPaperPx;',
        'uniform sampler2D tPaper;',""",
"""        'uniform vec3 uShadow,uHigh; uniform float uSat,uVig,uGrain,uPaperPx;',
        'uniform float uExpo,uBloom; uniform sampler2D tPaper,tBloom;',""")

sub("""        '  vec3 c = texture2D(tDiffuse,vUv).rgb;',
        '  float lum = dot(c,vec3(0.2126,0.7152,0.0722));',""",
"""        '  vec3 c = texture2D(tDiffuse,vUv).rgb;',
        /* the ember: add the blurred bright pass before grading, so the halo
           is graded and grained along with everything else and does not sit
           on top of the picture like a sticker */
        '  c += texture2D(tBloom,vUv).rgb * uBloom;',
        '  c *= uExpo;',
        '  float lum = dot(c,vec3(0.2126,0.7152,0.0722));',""")

sub("""    var sc2=new THREE.Scene();
    sc2.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),mtl));
    POST={rt:rt, mat:mtl, scene:sc2, cam:new THREE.OrthographicCamera(-1,1,1,-1,0,1)};""",
"""    var sc2=new THREE.Scene();
    sc2.add(new THREE.Mesh(new THREE.PlaneGeometry(2,2),mtl));
    POST={rt:rt, mat:mtl, scene:sc2, cam:new THREE.OrthographicCamera(-1,1,1,-1,0,1)};

    /* ---- bloom, at half resolution ----
       Bright pass into A, blur across into B, blur down back into A. Two
       plain shader materials and two ordinary render targets, so none of it
       depends on the example post processing that this build cannot load. */
    function half(){
      return new THREE.WebGLRenderTarget(2,2,{minFilter:THREE.LinearFilter,
        magFilter:THREE.LinearFilter, format:THREE.RGBAFormat,
        type:THREE.UnsignedByteType, depthBuffer:false, stencilBuffer:false});
    }
    var VS=['varying vec2 vUv;',
            'void main(){ vUv=uv; gl_Position=vec4(position.xy,0.0,1.0); }'].join('\\n');
    var thr=new THREE.ShaderMaterial({depthTest:false,depthWrite:false,
      uniforms:{tDiffuse:{value:rt.texture},uThr:{value:0.62}},
      vertexShader:VS,
      fragmentShader:['precision highp float;',
        'uniform sampler2D tDiffuse; uniform float uThr; varying vec2 vUv;',
        'void main(){',
        '  vec3 c=texture2D(tDiffuse,vUv).rgb;',
        '  float l=dot(c,vec3(0.2126,0.7152,0.0722));',
        '  float w=smoothstep(uThr,uThr+0.30,l);',
        /* keep the hue of what is glowing, an ember is orange not white */
        '  gl_FragColor=vec4(c*w,1.0);',
        '}'].join('\\n')});
    var blr=new THREE.ShaderMaterial({depthTest:false,depthWrite:false,
      uniforms:{tDiffuse:{value:null},uDir:{value:new THREE.Vector2(1,0)},
                uTexel:{value:new THREE.Vector2(1/512,1/512)}},
      vertexShader:VS,
      fragmentShader:['precision highp float;',
        'uniform sampler2D tDiffuse; uniform vec2 uDir,uTexel; varying vec2 vUv;',
        'void main(){',
        '  vec2 o=uDir*uTexel;',
        '  vec3 c=texture2D(tDiffuse,vUv).rgb*0.2270270270;',
        '  c+=texture2D(tDiffuse,vUv+o*1.3846153846).rgb*0.3162162162;',
        '  c+=texture2D(tDiffuse,vUv-o*1.3846153846).rgb*0.3162162162;',
        '  c+=texture2D(tDiffuse,vUv+o*3.2307692308).rgb*0.0702702703;',
        '  c+=texture2D(tDiffuse,vUv-o*3.2307692308).rgb*0.0702702703;',
        '  gl_FragColor=vec4(c,1.0);',
        '}'].join('\\n')});
    BLOOM={a:half(), b:half(), thr:thr, blur:blr,
           scene:new THREE.Scene(), quad:new THREE.Mesh(new THREE.PlaneGeometry(2,2),thr)};
    BLOOM.scene.add(BLOOM.quad);
    mtl.uniforms.tBloom.value=BLOOM.a.texture;""")

sub("""var POST=null;
(function(){""",
"""var POST=null, BLOOM=null;
(function(){""")

# ---------------------------------------------------------------- the passes
sub("""  renderer.setRenderTarget(POST.rt);
  renderer.render(scene,camera);
  renderer.setRenderTarget(null);
  renderer.render(POST.scene,POST.cam);
}""",
"""  renderer.setRenderTarget(POST.rt);
  renderer.render(scene,camera);
  if(BLOOM){
    var q=BLOOM.quad, sc3=BLOOM.scene, cm=POST.cam;
    q.material=BLOOM.thr;
    renderer.setRenderTarget(BLOOM.a); renderer.render(sc3,cm);
    q.material=BLOOM.blur;
    BLOOM.blur.uniforms.tDiffuse.value=BLOOM.a.texture;
    BLOOM.blur.uniforms.uDir.value.set(1,0);
    renderer.setRenderTarget(BLOOM.b); renderer.render(sc3,cm);
    BLOOM.blur.uniforms.tDiffuse.value=BLOOM.b.texture;
    BLOOM.blur.uniforms.uDir.value.set(0,1);
    renderer.setRenderTarget(BLOOM.a); renderer.render(sc3,cm);
  }
  renderer.setRenderTarget(null);
  renderer.render(POST.scene,POST.cam);
}""")

# ------------------------------------------------------------------ sizing
BLOOM_SIZE = """    POST.rt.setSize(Math.max(2,Math.floor(w*dpr)),Math.max(2,Math.floor(h*dpr)));
    POST.mat.uniforms.uRes.value.set(w,h);"""
BLOOM_SIZE_NEW = """    POST.rt.setSize(Math.max(2,Math.floor(w*dpr)),Math.max(2,Math.floor(h*dpr)));
    POST.mat.uniforms.uRes.value.set(w,h);
    if(BLOOM){
      var bw=Math.max(2,Math.floor(w*dpr*0.5)), bh=Math.max(2,Math.floor(h*dpr*0.5));
      BLOOM.a.setSize(bw,bh); BLOOM.b.setSize(bw,bh);
      BLOOM.blur.uniforms.uTexel.value.set(1/bw,1/bh);
    }"""
s = s.replace(BLOOM_SIZE, BLOOM_SIZE_NEW)   # both resize() and the debug setSize
n += 2

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
