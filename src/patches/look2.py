# -*- coding: utf-8 -*-
"""Apply the style injector everywhere, rebuild the light rig, fix the truck."""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================================ terrain
sub("""var terrainMat;
(function(){
  var N=Math.round(WORLD/GRID), V=N+1;""",
"""var terrainMat;
/* texels of about 7.5 cm, so 128 of them span roughly 12 m of world */
GRAIN_TEX=grainTex(128,7,0.55,6);
var PAPER_TEX=grainTex(256,44,0.30,5);
(function(){
  var N=Math.round(WORLD/GRID), V=N+1;""")

# the old albedo quantisation now fights the lighting bands, so it goes
sub("""    /* Quantised per face value, in five steps. This is what makes one facet
       read as a different plane from the one beside it. */
    var hsh=hash2(Math.floor(mx*0.37)+fi*0.013, Math.floor(mz*0.37));
    var step=Math.round(hsh*4)/4;
    var g=0.86+step*0.28;

    var o=t*9;""",
"""    /* No value quantisation here any more. It used to be baked into the
       albedo and the lighting smoothed it straight back out. The banding now
       happens after lighting, in styleMat. */
    var o=t*9;""")

sub("""    var r=c.r*g, gg=c.g*g, bb=c.b*g;""",
    """    var r=c.r, gg=c.g, bb=c.b;""")

sub("""  terrainMat=new THREE.MeshPhongMaterial({
    vertexColors:true, specular:0x000000, shininess:0, flatShading:true});""",
"""  terrainMat=styleMat(new THREE.MeshPhongMaterial({
    vertexColors:true, specular:0x000000, shininess:0, flatShading:true}),{grain:true});""")

# rock takes over sooner, now that the rock family is a different hue
sub("    c.lerp(cRock, sstep(0.24,0.52,slope));",
    "    c.lerp(cRock, sstep(0.18,0.46,slope));")

# ================================================================ backdrop
sub("""    var cone=new THREE.Mesh(new THREE.ConeGeometry(hgt*0.85,hgt,5),
      new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,flatShading:true,
        color:new THREE.Color(0x8b5f63).lerp(FOG,0.34).convertSRGBToLinear()}));""",
"""    var cone=new THREE.Mesh(new THREE.ConeGeometry(hgt*0.85,hgt,5),
      styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
        flatShading:true, color:sc(PAL.peak)}),{}));""")

# ================================================================ scatter
sub("""  var rockM=new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,color:0x7a4b37,flatShading:true});
  var rocks=new THREE.InstancedMesh(rockG,rockM,340);""",
"""  var rockM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(PAL.rock),flatShading:true}),{});
  var rocks=new THREE.InstancedMesh(rockG,rockM,220);""")
sub("""  var bushM=new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,color:0x6b6b3a,flatShading:true});""",
"""  var bushM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(PAL.scrub),flatShading:true}),{});""")
sub("  var d=new THREE.Object3D(), k=0, b=0, guard=0;\n  while((k<340||b<300) && guard++<4000){",
    "  var d=new THREE.Object3D(), k=0, b=0, guard=0;\n  while((k<220||b<300) && guard++<4000){")
sub("    if(k<340 && _n1.y<0.93){","    if(k<220 && _n1.y<0.93){")
sub("      var s=0.7+hash2(guard,3.3)*2.3;","      var s=0.8+hash2(guard,3.3)*3.0;")

# ================================================================ gates
sub("""  var postM=new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,color:0xe8e0d0,flatShading:true});
  var barM=new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,color:0xe4432b,flatShading:true});""",
"""  var postM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe8e0d0),flatShading:true}),{});
  var barM=styleMat(new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,
    color:sc(0xe4432b),flatShading:true}),{});""")

# ================================================================ landmarks
sub("""  function m(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var k in extra) o[k]=extra[k];
    return new THREE.MeshPhongMaterial(o);
  }""",
"""  function m(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var k in extra) o[k]=extra[k];
    return styleMat(new THREE.MeshPhongMaterial(o),{});
  }""")

# ================================================================ stones
sub("""  var sm=new THREE.MeshPhongMaterial({color:sc(0x8a5a44),specular:0x000000,
    shininess:0,flatShading:true});""",
"""  var sm=styleMat(new THREE.MeshPhongMaterial({color:sc(PAL.rock),specular:0x000000,
    shininess:0,flatShading:true}),{});""")

# ================================================================ truck
old_rim = s[s.index("  /* A warm edge on the sun facing side lifts the truck off the sand without"):s.index("  var paint  = rimify(mat(PAL.body),3.0,0.55);")]
s = s.replace(old_rim, "", 1); n += 1

sub("""  var paint  = rimify(mat(PAL.body),3.0,0.55);          /* body */
  var roofM  = rimify(mat(0xf0ece0),3.2,0.34);          /* the white roof */""",
"""  /* A cyan body under a saturated warm key is a near complementary multiply
     and it cancels to grey. Measured: authored at 0.48 saturation, rendered at
     0.05. The emissive floor is a share of its own colour that the light
     cannot multiply away. */
  var paint  = styleMat(mat(PAL.body),{rim:[2.4,0.85]});
  paint.emissive=new THREE.Color(PAL.body).convertSRGBToLinear().multiplyScalar(0.30);
  TRUCK_PAINT=paint;
  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45]});""")

sub("""  function mat(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var kk in extra) o[kk]=extra[kk];
    return new THREE.MeshPhongMaterial(o);
  }""",
"""  function mat(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var kk in extra) o[kk]=extra[kk];
    return new THREE.MeshPhongMaterial(o);
  }
  function smat(col,extra){ return styleMat(mat(col,extra),{}); }""")

for a,b in [("var trim   = mat(0x24313a);","var trim   = smat(0x24313a);"),
            ("var tyreM  = mat(0x231f28);","var tyreM  = smat(PAL.tyre);"),
            ("var lugM   = mat(0x1a171f);","var lugM   = smat(0x1a171f);"),
            ("var rimM   = mat(0xd6cbba);","var rimM   = smat(PAL.wheel);"),
            ("var chrome = mat(0x9aa0a8);","var chrome = smat(0x8f8b86);"),
            ("var spring = mat(0xe8862c);","var spring = smat(PAL.spring);"),
            ("var canvasM= mat(0xc9b489);","var canvasM= smat(0xc9b489);")]:
    sub(a,b)

sub("var truck=new THREE.Group(); scene.add(truck);\nvar corners=[], STRUT=[], GLOW=[], RIMMED=[];",
    "var truck=new THREE.Group(); scene.add(truck);\nvar corners=[], STRUT=[], GLOW=[];\nvar TRUCK_PAINT=null;")

# the rim uniform is shared now, so one assignment replaces the loop
sub("""  /* the rim needs the sun in view space, which changes as the camera moves */
  _sunV.copy(SUN_DIR).transformDirection(camera.matrixWorldInverse);
  for(var ri=0;ri<RIMMED.length;ri++){
    var sh=RIMMED[ri].userData.shader;
    if(sh) sh.uniforms.uSunV.value.copy(_sunV);
  }""",
"""  /* the rim needs the sun in view space, and the uniform is shared */
  STYLE_U.uSunV.value.copy(SUN_DIR).transformDirection(camera.matrixWorldInverse);""")

# ================================================================ light rig
sub("var hemi=new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.80);",
    "var hemi=new THREE.HemisphereLight(sc(PAL.skyFill),sc(PAL.groundFill),0.42);")
sub("  bounce.intensity=0.28*(A.sunI+(B.sunI-A.sunI)*k)/1.85;",
    "  bounce.intensity=0.18*(A.sunI+(B.sunI-A.sunI)*k)/1.55;")

# the truck keeps its colour as the light goes
sub("""  TOD.glow=A.glow+(B.glow-A.glow)*k;""",
"""  TOD.glow=A.glow+(B.glow-A.glow)*k;
  if(TRUCK_PAINT) TRUCK_PAINT.emissive.copy(sc(PAL.body))
    .multiplyScalar(0.30+0.28*Math.max(0,(A.glow+(B.glow-A.glow)*k-0.2)/0.8));""")

# ================================================================ times
sub("""  { name:'Dawn',
    dir:[-70,16,-130], sun:0xffc0b0, sunI:1.45, hemiS:0xa8a8d0, hemiG:0x8f7266, hemiI:0.72,
    sky:[0xe9c3b4,0xd9a89f,0xa98aa8,0x6d6f9c,0x3b4a80], fog:0xd8b0a4, fogN:60, fogF:470,
    glow:0.30, amb:0x101828 },
  { name:'Morning',
    dir:[-90,58,40], sun:0xfff0d2, sunI:2.05, hemiS:0xbcc4e0, hemiG:0xbb8a5c, hemiI:0.70,
    sky:[0xf2e0c2,0xe3d0ae,0xb9c2cf,0x82a2cc,0x4d7ec4], fog:0xe6d6b8, fogN:110, fogF:600,
    glow:0.00, amb:0x000000 },
  { name:'Golden',
    dir:[-120,22,60], sun:0xffc98a, sunI:2.05, hemiS:0xb0a6c4, hemiG:0xd8944e, hemiI:0.76,
    sky:[0xf5c795,0xefa875,0xc97f6e,0x8e7290,0x54658c], fog:0xe8a271, fogN:90, fogF:520,
    glow:0.12, amb:0x000000 },""",
"""  { name:'Dawn',
    dir:[-70,16,-130], sun:0xffc0b0, sunI:1.20, hemiS:0xa8a8d0, hemiG:0x8f7266, hemiI:0.46,
    sky:[0xe9c3b4,0xd9a89f,0xa98aa8,0x6d6f9c,0x3b4a80], fog:0xc8a0b4, fogN:60, fogF:470,
    glow:0.30, amb:0x101828 },
  { name:'Morning',
    dir:[-90,58,40], sun:0xfff0d2, sunI:1.70, hemiS:0xbcc4e0, hemiG:0xbb8a5c, hemiI:0.44,
    sky:[0xf2e0c2,0xe3d0ae,0xb9c2cf,0x82a2cc,0x4d7ec4], fog:0xcfcadc, fogN:110, fogF:600,
    glow:0.00, amb:0x000000 },
  { name:'Golden',
    /* about 110 degrees of sky hue rotation, against the 49 that was measured */
    dir:[-120,22,60], sun:0xffb870, sunI:1.55, hemiS:0x8e7aa8, hemiG:0xb0603a, hemiI:0.42,
    sky:[0xffc87a,0xf59a62,0xd9705f,0xa85e7e,0x6b4c86], fog:0xb98498, fogN:70, fogF:560,
    glow:0.16, amb:0x000000 },""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
print('rimify gone:', 'rimify' not in s)
print('RIMMED gone:', 'RIMMED' not in s)
