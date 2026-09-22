# -*- coding: utf-8 -*-
"""The low poly look, finally, plus the palette and the truck.

THE MECHANISM, measured: adjacent facets differed by 0.006 luma. The faceting
was invisible. The cause was that the value quantisation was baked into the
ALBEDO, and then N dot L, the hemisphere fill, the fog, the shadow map and the
grade all ran continuously on top of it and smoothed it straight back into a
gradient. Quantising the input to a system whose job is continuous output does
nothing. So the posterise moves into the fragment shader and runs on the
computed lighting term instead. Four bands. Target adjacent facet delta 0.06.

THE PALETTE, measured: 76 to 82 percent of every daylight frame sat within 15
degrees of one hue, and the ground hue spread across the whole of one frame was
one degree. The single biggest cause is that the fog was the same hue as the
sand, so everything past 90 m was painted the colour of the ground three metres
away and nothing receded. Fog, rock and the backdrop peaks all move to a rose
and mauve family. That is the depth and the colour in one change.

THE TRUCK, measured: authored at saturation 0.48, rendered at 0.05. A cyan
surface multiplied by a saturated warm key is a near complementary multiply and
it cancels to grey. It gets an emissive floor of its own colour so a share of
its chroma cannot be multiplied away. Also the highest contrast thing on the
whole vehicle was the spare wheel hub, so it read as a bullseye. That is one
hex value.

Grain goes in as an offset to the shade term BEFORE the floor, not into the
albedo. Inside a face it does nothing at all; at a band boundary it breaks the
edge into chunky texels. It strengthens the faceting instead of fighting it.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================================ palette
sub("""var PAL={
  /* Saturated on purpose. The measured reference work sits near 0.5 median
     saturation, and washed out sand reads as unfinished rather than tasteful. */
  low:0xb85f2c, mid:0xe09242, high:0xf5c877, rock:0x8a4a38, playa:0xe0cfa8,
  scrub:0x6e7048, fog:0xe8a271,
  sun:0xffc98a, skyFill:0x7fa0d8, groundFill:0xc87f4a, bounce:0x6e7fa8,
  body:0x2f7a86, bone:0xf0e6d2, spring:0xe0553f, tyre:0x2b2733, wheel:0xd9cfc0,
  dust:0xe8c79a
};""",
"""/* Four hue families. Sand 20 to 42, rock and distance 285 to 340, a sparse
   green, and the truck as the only thing above 0.45 saturation that is not
   sand. The rock family is the change: it used to be the same orange as the
   sand, so it did nothing, and the fog agreed with the ground so the whole
   basin was one hue with a value ramp on it. */
var PAL={
  low:0xc0703c, mid:0xde9a50, high:0xf0c67c, playa:0xd9c9a4,
  rock:0x8e5566, peak:0x7a5c82, fog:0xb98498,
  scrub:0x5e6b4a,
  sun:0xffb870, skyFill:0x8e7aa8, groundFill:0xb0603a, bounce:0x7a6aa0,
  body:0x2f7a86, bone:0xf0e6d2, spring:0xe85a2c, tyre:0x241f2a, wheel:0x8a8070,
  dust:0xe8c79a
};""")

# ================================================================ the ramp
sub("""function sc(hex){ return new THREE.Color(hex).convertSRGBToLinear(); }""",
"""function sc(hex){ return new THREE.Color(hex).convertSRGBToLinear(); }

/* One quantised noise tile, magnified with no filtering at all. Used as an
   offset to the shade term, never multiplied into albedo. */
function grainTex(size,cells,contrast,levels){
  var c=document.createElement('canvas'); c.width=c.height=size;
  var g=c.getContext('2d'), img=g.createImageData(size,size), d=img.data;
  for(var i=0;i<size*size;i++){
    var x=(i%size)/size*cells, y=Math.floor(i/size)/size*cells;
    var v=fbm(x,y,3);
    v=Math.round(v*levels)/levels;
    var b=Math.max(0,Math.min(255,Math.round(128+(v-0.5)*255*contrast)));
    d[i*4]=d[i*4+1]=d[i*4+2]=b; d[i*4+3]=255;
  }
  g.putImageData(img,0,0);
  var t=new THREE.CanvasTexture(c);
  t.wrapS=t.wrapT=THREE.RepeatWrapping;
  t.magFilter=t.minFilter=THREE.NearestFilter;
  t.generateMipmaps=false;
  return t;
}

var STYLE_U={
  uShadeGain :{value:3.10},
  uShadowTint:{value:sc(0xe0a8ae)},
  uSunTint   :{value:sc(0xffd9a0)},
  uGrainAmt  :{value:0.13},
  uGrainScale:{value:1/12},
  uBandDebug :{value:0},
  uRimC      :{value:sc(0xffd9a0)},
  uSunV      :{value:new THREE.Vector3()}
};
var GRAIN_TEX=null;
var STYLED=[];

/* The one style injector. Posterises the LIGHTING, not the albedo, and
   optionally adds a rim and the grain. Both jobs go through a single
   onBeforeCompile because two of them on one material would overwrite. */
function styleMat(mm,opts){
  opts=opts||{};
  mm.onBeforeCompile=function(sh){
    sh.uniforms.uShadeGain=STYLE_U.uShadeGain;
    sh.uniforms.uShadowTint=STYLE_U.uShadowTint;
    sh.uniforms.uSunTint=STYLE_U.uSunTint;
    sh.uniforms.uBandDebug=STYLE_U.uBandDebug;
    if(opts.grain){
      sh.uniforms.uGrainAmt=STYLE_U.uGrainAmt;
      sh.uniforms.uGrainScale=STYLE_U.uGrainScale;
      sh.uniforms.uGrainTex={value:GRAIN_TEX};
    }
    if(opts.rim){
      sh.uniforms.uRimC=STYLE_U.uRimC;
      sh.uniforms.uSunV=STYLE_U.uSunV;
      sh.uniforms.uRimP={value:opts.rim[0]};
      sh.uniforms.uRimA={value:opts.rim[1]};
    }
    mm.userData.shader=sh;

    if(opts.grain){
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')
        .replace('#include <begin_vertex>',
                 '#include <begin_vertex>\\nvWPosS=(modelMatrix*vec4(transformed,1.0)).xyz;');
    }

    var head=['#include <common>',
      'uniform float uShadeGain, uBandDebug;',
      'uniform vec3 uShadowTint, uSunTint;',
      'const vec3 LUMA_S = vec3(0.2126,0.7152,0.0722);'];
    if(opts.grain) head.push('varying vec3 vWPosS;','uniform float uGrainAmt,uGrainScale;','uniform sampler2D uGrainTex;');
    if(opts.rim) head.push('uniform vec3 uRimC,uSunV;','uniform float uRimP,uRimA;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>',head.join('\\n'));

    var body=[
      'vec3 albS = max( diffuseColor.rgb, vec3(1e-4) );',
      'vec3 litS = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;',
      'float shS = dot( litS / albS, LUMA_S ) * uShadeGain;'];
    if(opts.grain) body.push(
      'float gA = texture2D( uGrainTex, vWPosS.xz * uGrainScale ).r;',
      'float gB = texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.235 + 0.37 ).r;',
      'float grainS = ( gA*0.65 + gB*0.35 ) - 0.5;',
      'grainS *= 1.0 - smoothstep( 55.0, 130.0, length( vViewPosition ) );',
      'shS += grainS * uGrainAmt;');
    body.push(
      'float qS = clamp( floor( shS * 4.0 ), 0.0, 3.0 );',
      'vec3 pcS = albS * ( 0.46 + qS * 0.18 );',
      /* shadow keeps the hue and loses a little chroma, it does not go violet */
      'float sTS = 1.0 - smoothstep( 0.6, 2.4, qS );',
      'pcS = mix( pcS, mix( pcS, vec3(dot(pcS,LUMA_S)), 0.20 ) * uShadowTint, sTS*0.80 );',
      'pcS = mix( pcS, pcS * uSunTint, step( 2.5, qS ) * 0.28 );');
    if(opts.rim) body.push(
      'vec3 VvS = normalize( vViewPosition );',
      'float rimS = pow( 1.0 - clamp( dot( normal, VvS ), 0.0, 1.0 ), uRimP );',
      'rimS *= smoothstep( -0.25, 0.55, dot( normal, uSunV ) );',
      'pcS += uRimC * rimS * uRimA;');
    body.push(
      'if( uBandDebug > 0.5 ) pcS = vec3( qS / 3.0 );',
      'vec3 outgoingLight = pcS + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;');

    sh.fragmentShader=sh.fragmentShader.replace(
      'vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;',
      body.join('\\n'));
  };
  /* Without this r128 can hand two materials with identical parameters the
     same cached program and the injection silently vanishes on one of them. */
  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':''); };
  STYLED.push(mm);
  return mm;
}""")

sub("""var GRAIN_TEX=null;""",
    """var GRAIN_TEX=null;   /* built after fbm is available, see below */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
