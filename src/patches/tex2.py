# -*- coding: utf-8 -*-
"""Textures across the whole environment, chosen by what a surface actually is.

Four photographs now, all public domain or CC0, all baked in as data:

  sand       Sand_public_domain.JPG                       CC0
  sandstone  Sandstone_Texture_(2650399847).jpg           CC0
  cracked    Dry_Cracked_Mud (US National Park Service)   public domain
  metal      Leaking top edge ... old metal steel texture CC0

The terrain is one mesh with one material, so it cannot simply be handed a
different texture per surface. Instead each face now carries a two component
weight attribute, written at build time from the same lake mask and slope that
already decide its colour, and the shader blends the cracked mud in on the dry
lake and the sandstone in on anything steep. So the riverbed reads as a
riverbed and the escarpments read as rock, from the same numbers the physics
uses to decide how they grip.

Everything built by people wears the weathered metal: the gates, the motel
sign, the gas station, the drive in, the water tower, the camper, the windmill.
That is the ember.lite subject matter and it was the last untextured thing.

And a small piece of style: the texture now shifts hue as well as value,
warming where it is bright and cooling where it is dark, which is what stops a
flat facet reading as a single sheet of paint.
"""
import io, base64

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

playa = base64.b64encode(open('../shots/px_playa.png', 'rb').read()).decode()
metal = base64.b64encode(open('../shots/px_metal.png', 'rb').read()).decode()

# ------------------------------------------------------------ two more tiles
sub("""  PHOTO_SAND=tex('""",
    """  PHOTO_PLAYA=tex('%PLAYA%');
  PHOTO_METAL=tex('%METAL%');
  PHOTO_SAND=tex('""".replace('%PLAYA%', playa).replace('%METAL%', metal))
sub("var PHOTO_SAND=null, PHOTO_ROCK=null;",
    "var PHOTO_SAND=null, PHOTO_ROCK=null, PHOTO_PLAYA=null, PHOTO_METAL=null;")

sub("      sh.uniforms.uGrainTex={value:(opts.tex==='rock'?PHOTO_ROCK:PHOTO_SAND)||GRAIN_TEX};",
"""      sh.uniforms.uGrainTex={value:(
        opts.tex==='rock' ? PHOTO_ROCK :
        opts.tex==='metal'? PHOTO_METAL :
        opts.tex==='playa'? PHOTO_PLAYA : PHOTO_SAND)||GRAIN_TEX};
      if(opts.surf){
        sh.uniforms.uTexPlaya={value:PHOTO_PLAYA};
        sh.uniforms.uTexRock ={value:PHOTO_ROCK};
      }""")
sub("  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':'')+(opts.tex||''); };",
    "  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':'')+(opts.tex||'')+(opts.surf?'S':''); };")

# ------------------------------------------------ the surface weight varying
sub("""    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')""",
"""    if(opts.surf){
      sh.vertexShader=sh.vertexShader
        .replace('#include <common>',
                 '#include <common>\\nattribute vec2 surfW;\\nvarying vec2 vSurfS;')
        .replace('#include <begin_vertex>','#include <begin_vertex>\\nvSurfS=surfW;');
    }
    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')""")

sub("""    if(opts.grain) head.push(
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');""",
"""    if(opts.grain) head.push(
      'uniform float uGrainAmt,uGrainPost,uGrainScale;','uniform sampler2D uGrainTex;');
    if(opts.surf) head.push('varying vec2 vSurfS;','uniform sampler2D uTexPlaya,uTexRock;');""")

# --------------------------------------- blend the right photograph per face
sub("""      'grainS -= 0.5;',
      'shS += grainS * uGrainAmt;');""",
"""      'grainS -= 0.5;'"""
+ """);
    if(opts.surf) body.push(
      /* The dry lake wears cracked mud and anything steep wears sandstone.
         One extra sample each, blended by weights the terrain builder wrote
         from the same mask and slope that set its colour. */
      'float gPl = texture2D( uTexPlaya, vWPosS.xz * uGrainScale * 0.62 ).r - 0.5;',
      'float gRk = texture2D( uTexRock,  vWPosS.xz * uGrainScale * 0.80 ).r - 0.5;',
      'grainS = mix( mix( grainS, gRk, clamp(vSurfS.y,0.0,1.0) ), gPl, clamp(vSurfS.x,0.0,1.0) );');
    if(opts.grain) body.push(
      'shS += grainS * uGrainAmt;');""")

# ------------------------------------- style: the texture moves hue, not only value
sub("    if(opts.grain) body.push('pcS *= 1.0 + grainS * uGrainPost;');",
"""    if(opts.grain) body.push(
      'pcS *= 1.0 + grainS * uGrainPost;',
      /* a flat facet reads as one sheet of paint if the only thing varying
         across it is brightness, so the texture warms the light side and
         cools the dark side as well */
      'pcS *= vec3( 1.0 + grainS * 0.30, 1.0, 1.0 - grainS * 0.26 );');""")

# ------------------------------------------------- terrain writes the weights
sub("""  var TRIS=N*N*2;
  var pos=new Float32Array(TRIS*9), col=new Float32Array(TRIS*9);""",
"""  var TRIS=N*N*2;
  var pos=new Float32Array(TRIS*9), col=new Float32Array(TRIS*9);
  var sw=new Float32Array(TRIS*6);       /* per face: how much lake, how much rock */""")

sub("""    var o=t*9;
    pos[o]=ax; pos[o+1]=ay; pos[o+2]=az;""",
"""    var lkw=lakeMask(mx,mz), rkw=sstep(0.16,0.44,slope);
    var so=t*6;
    sw[so]=lkw; sw[so+1]=rkw; sw[so+2]=lkw; sw[so+3]=rkw; sw[so+4]=lkw; sw[so+5]=rkw;

    var o=t*9;
    pos[o]=ax; pos[o+1]=ay; pos[o+2]=az;""")

sub("""  g2.setAttribute('color',new THREE.BufferAttribute(col,3));""",
    """  g2.setAttribute('color',new THREE.BufferAttribute(col,3));
  g2.setAttribute('surfW',new THREE.BufferAttribute(sw,2));""")

sub("""  terrainMat=styleMat(new THREE.MeshPhongMaterial({
    vertexColors:true, specular:0x000000, shininess:0, flatShading:true}),{grain:true});""",
"""  terrainMat=styleMat(new THREE.MeshPhongMaterial({
    vertexColors:true, specular:0x000000, shininess:0, flatShading:true}),
    {grain:true, surf:true});""")

# ------------------------------------ everything people built wears the metal
sub("""  var post=m(0x6b5a52), panel=m(0xd8cec0), rust=m(0x8a4a34), metal=m(0x8d939a),
      dark=m(0x2f2a30), wood=m(0x7a5c40), white=m(0xe8e2d4);""",
"""  function mM(col){
    return styleMat(new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true}),{tex:'metal'});
  }
  var post=mM(0x6b5a52), panel=mM(0xd8cec0), rust=mM(0x8a4a34), metal=mM(0x8d939a),
      dark=mM(0x2f2a30), wood=mM(0x7a5c40), white=mM(0xe8e2d4);""")

sub("""  var postM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe8e0d0),flatShading:true}),{});
  var barM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe4432b),flatShading:true}),{});""",
"""  var postM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe8e0d0),flatShading:true}),{tex:'metal'});
  var barM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe4432b),flatShading:true}),{tex:'metal'});""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n, '| KB:', len(s)//1024)
