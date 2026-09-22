# -*- coding: utf-8 -*-
"""Let the light's colour reach the paint, and put the truck in the world.

THE ROOT CAUSE. The style injector collapsed the whole lighting result to a
single brightness number and then multiplied the raw albedo by it. Every bit of
chroma in the sun, the sky fill and the ambient was discarded at that line. So
five carefully authored times of day rendered as the same orange desert with
different amounts of grey on it, and no amount of palette tuning could ever
have changed that. Proof: forcing the sun and the sky to pure saturated green
moved the frame by 10.8 percent and the sand stayed orange.

The fix is to carry the light's chroma through the band. The luma of the light
still drives which band a surface lands in, exactly as before, so the posterised
look is untouched; but the band is then tinted by the colour of the light that
is actually falling on it. A blue dusk sky now makes a blue shadow because the
sky is blue, not because I hand painted a shadow tint to match.

THE TRUCK. It was excluded from the texture and grain path entirely, which is
why the largest object on screen was flat untextured colour sitting in front of
sand carrying three octaves of photographic tooth. It could not simply be
switched on, because the world grain is projected in world space and would swim
across a moving object. So there is now an object space path: the same
photograph, sampled in the vehicle's own coordinates, so it sticks to the panel
and moves with it.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ======================================================== 1. light chroma
sub("""      'float shS = pow( max( ( dot( litS / albS, LUMA_S ) - uShadeLift ) * uShadeGain, 0.0 ), uShadeCurve );'];""",
"""      'float shS = pow( max( ( dot( litS / albS, LUMA_S ) - uShadeLift ) * uShadeGain, 0.0 ), uShadeCurve );',
      /* The colour of the light that is actually falling here, normalised so
         it tints without changing brightness. Luma still picks the band; this
         only says what colour that band is. */
      'float lumL = max( dot( litS, LUMA_S ), 1e-4 );',
      'vec3 lchr = clamp( litS / lumL, 0.0, 3.0 );'];""")

sub("      'vec3 pcS = albS * ( uBandLo + qS * uBandSt );');",
"""      'vec3 pcS = albS * ( uBandLo + qS * uBandSt );',
      /* and here is the line that was missing the whole time */
      'pcS *= mix( vec3(1.0), lchr, uLightChroma );');""")

sub("  uFacade    :{value:0.0},",
    "  uFacade    :{value:0.0},\n  uLightChroma:{value:0.70},")
sub("      'uniform float uFacBase,uFacLit;'];",
    "      'uniform float uFacBase,uFacLit,uLightChroma;'];")
sub("    sh.uniforms.uFacBase=STYLE_U.uFacBase;",
    "    sh.uniforms.uFacBase=STYLE_U.uFacBase;\n    sh.uniforms.uLightChroma=STYLE_U.uLightChroma;")

# the hand painted tints can now step back, the light is doing that work
sub("'pcS = mix( pcS, mix( pcS, vec3(dot(pcS,LUMA_S)), 0.08 ) * uShadowTint, sTS*0.44 );',",
    "'pcS = mix( pcS, mix( pcS, vec3(dot(pcS,LUMA_S)), 0.06 ) * uShadowTint, sTS*0.26 );',")

# and the highlight tint must actually follow the time of day
sub("""  lerpHex(A.shad,B.shad,k,STYLE_U.uShadowTint.value); STYLE_U.uShadowTint.value.convertSRGBToLinear();""",
"""  lerpHex(A.shad,B.shad,k,STYLE_U.uShadowTint.value); STYLE_U.uShadowTint.value.convertSRGBToLinear();
  /* these two were set once at boot and never written again, so the highlight
     tint and the truck's rim light were warm cream at midnight */
  lerpHex(A.sun,B.sun,k,STYLE_U.uSunTint.value); STYLE_U.uSunTint.value.convertSRGBToLinear();
  lerpHex(A.sun,B.sun,k,STYLE_U.uRimC.value); STYLE_U.uRimC.value.convertSRGBToLinear();""")

# ============================================ 2. object space grain for the truck
sub("""    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')""",
"""    if(opts.obj){
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>','#include <common>\\nvarying vec3 vObjS;')
        .replace('#include <begin_vertex>','#include <begin_vertex>\\nvObjS=transformed;');
    }
    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')""")

sub("""    if(opts.grain) head.push(
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');""",
"""    if(opts.grain) head.push(
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');
    if(opts.obj) head.push('varying vec3 vObjS;');""")

# object space samples the same photograph in the vehicle's own coordinates
sub("""      'float grainS = texture2D( uGrainTex, vWPosS.xz * uGrainScale ).r * w0S',
      '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.222 + 0.37 ).r * w1S',
      '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.059 - 0.19 ).r * w2S;',
      'grainS -= 0.5;'""",
"""      (opts.obj
        ? 'vec2 guv = ( abs(normal.y) > 0.5 ? vObjS.xz : ( abs(normal.x) > 0.5 ? vObjS.zy : vObjS.xy ) ) * 0.55;'
        : 'vec2 guv = vWPosS.xz * uGrainScale;'),
      (opts.obj
        ? 'float grainS = texture2D( uGrainTex, guv ).r * 0.62 + texture2D( uGrainTex, guv*0.31 + 0.4 ).r * 0.38;'
        : 'float grainS = texture2D( uGrainTex, guv ).r * w0S'),
      (opts.obj ? '' : '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.222 + 0.37 ).r * w1S'),
      (opts.obj ? '' : '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.059 - 0.19 ).r * w2S;'),
      'grainS -= 0.5;'""")

# ---- and the truck opts in, with its own gentler amount
sub("""  function smat(col,extra){ return styleMat(mat(col,extra),{nograin:true}); }""",
    """  function smat(col,extra){ return styleMat(mat(col,extra),{obj:true,tex:'metal'}); }""")
sub("""  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95],nograin:true});""",
    """  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95],obj:true,tex:'metal'});""")
sub("""  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});""",
    """  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],obj:true,tex:'metal'});""")
sub("""  var second = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});""",
    """  var second = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],obj:true,tex:'metal'});""")

sub("  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':'')+(opts.tex||'')+(opts.surf?'S':'')+(opts.facade?'F':''); };",
    "  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':'')+(opts.tex||'')+(opts.surf?'S':'')+(opts.facade?'F':'')+(opts.obj?'O':''); };")

# ---------------------------------- 3. the grain crossed whole bands
sub("grain:1.10, gpost:0.50,", "grain:0.46, gpost:0.72,")
sub("grain:0.95, gpost:0.42,", "grain:0.40, gpost:0.62,")
sub("grain:1.05, gpost:0.46,", "grain:0.44, gpost:0.68,")
sub("grain:1.36, gpost:0.56,", "grain:0.56, gpost:0.86,")
sub("grain:1.30, gpost:0.54,", "grain:0.52, gpost:0.82,")

# and give the tiles a mip chain so the far field stops aliasing
sub("""    t.magFilter=THREE.NearestFilter;
    t.minFilter=THREE.LinearFilter;
    t.generateMipmaps=false;""",
"""    t.magFilter=THREE.NearestFilter;      /* chunky up close, as asked */
    t.minFilter=THREE.LinearMipmapLinearFilter;
    t.generateMipmaps=true;                /* and stable at distance */
    t.anisotropy=4;""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
