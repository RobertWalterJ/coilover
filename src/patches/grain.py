# -*- coding: utf-8 -*-
"""The grain, actually switched on.

The tile was built, blended and then multiplied by 0.13, which moved the shade
term by 0.0077 against a band 0.25 wide. Three percent of a band. It never
crossed a band edge, so it never appeared. Ten times the amplitude puts it at
about a third of a band, which is the amount that makes a posterised edge break
up into texture instead of reading as a contour line on a map.

Second, a post quantise multiply, so the grain also textures the INSIDE of a
band. Before, the only place it could ever show was at an edge.

Third, three octaves chosen by view distance. A 7.5 cm texel is under a screen
pixel past about seven metres, which is why everything beyond the bonnet went
smooth. The mid tile holds at forty metres and the coarse one at the horizon,
so the texel stays roughly seven pixels the whole way out.

And the paper. PAPER_TEX was built at startup and never referenced by anything,
so the paper tooth you associate with this look was in the file and not on the
screen. It now runs over the whole frame in the post pass, replacing a hash
noise that was four times too quiet.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# --------------------------------------------------------------- amplitude
sub("""  uGrainAmt  :{value:0.13},
  uGrainScale:{value:1/12},""",
"""  uGrainAmt  :{value:1.35},   /* moves shS a third of a band at one sigma */
  uGrainPost :{value:0.55},   /* and textures the inside of the band too */
  uGrainScale:{value:1/12},""")

sub("""      sh.uniforms.uGrainAmt=STYLE_U.uGrainAmt;
      sh.uniforms.uGrainScale=STYLE_U.uGrainScale;""",
"""      sh.uniforms.uGrainAmt=STYLE_U.uGrainAmt;
      sh.uniforms.uGrainPost=STYLE_U.uGrainPost;
      sh.uniforms.uGrainScale=STYLE_U.uGrainScale;""")

sub("""    if(opts.grain) head.push('varying vec3 vWPosS;','uniform float uGrainAmt,uGrainScale;','uniform sampler2D uGrainTex;');""",
"""    if(opts.grain) head.push('varying vec3 vWPosS;',
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');""")

# ------------------------------------------------------- three octave blend
sub("""      'float gA = texture2D( uGrainTex, vWPosS.xz * uGrainScale ).r;',
      'float gB = texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.235 + 0.37 ).r;',
      'float grainS = ( gA*0.65 + gB*0.35 ) - 0.5;',
      'grainS *= 1.0 - smoothstep( 55.0, 130.0, length( vViewPosition ) );',
      'shS += grainS * uGrainAmt;');""",
"""      /* Pick the octave whose texel is still several screen pixels wide at
         this distance. Fine holds to about sixteen metres, mid to ninety,
         coarse to the horizon. Crossfaded, so there is no visible seam. */
      'float dS = length( vViewPosition );',
      'float w0S = 1.0 - smoothstep( 5.0, 18.0, dS );',
      'float w2S = smoothstep( 34.0, 95.0, dS );',
      'float w1S = max( 0.0, 1.0 - w0S - w2S );',
      'float grainS = texture2D( uGrainTex, vWPosS.xz * uGrainScale ).r * w0S',
      '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.222 + 0.37 ).r * w1S',
      '  + texture2D( uGrainTex, vWPosS.xz * uGrainScale * 0.059 - 0.19 ).r * w2S;',
      'grainS -= 0.5;',
      'shS += grainS * uGrainAmt;');""")

# ------------------------------------------------------ post quantise tooth
sub("""      'float qS = clamp( floor( shS * 4.0 ), 0.0, 3.0 );',
      'vec3 pcS = albS * ( 0.46 + qS * 0.18 );',""",
"""      'float qS = clamp( floor( shS * 4.0 ), 0.0, 3.0 );',
      'vec3 pcS = albS * ( 0.46 + qS * 0.18 );'""" + """);
    /* the same tile again, this time multiplying the banded colour, so a flat
       band carries tooth rather than being a dead area of paint */
    if(opts.grain) body.push('pcS *= 1.0 + grainS * uGrainPost;');
    body.push(""")

# ------------------------------------------------------------- paper, alive
sub("""        uSat:{value:1.08}, uVig:{value:0.22}, uGrain:{value:0.018}""",
"""        uSat:{value:1.08}, uVig:{value:0.22}, uGrain:{value:0.075},
        tPaper:{value:PAPER_TEX}, uPaperPx:{value:2.0*dpr}""")

sub("""        'uniform vec3 uShadow,uHigh; uniform float uSat,uVig,uGrain;',""",
"""        'uniform vec3 uShadow,uHigh; uniform float uSat,uVig,uGrain,uPaperPx;',
        'uniform sampler2D tPaper;',""")

sub("""        '  c += (h21(floor(gl_FragCoord.xy*0.5)+uTime) - 0.5)*uGrain;',""",
"""        /* paper tooth, held at a couple of screen pixels per texel and
           normalised so the amount means the same thing it did before */
        '  float pg = texture2D(tPaper, gl_FragCoord.xy/(256.0*uPaperPx)).r;',
        '  c += (pg - 0.5)*3.3*uGrain*(0.55 + 0.45*smoothstep(0.02,0.32,lum));',
        '  c += (h21(floor(gl_FragCoord.xy*0.5)+uTime) - 0.5)*uGrain*0.18;',""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
