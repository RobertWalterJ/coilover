# -*- coding: utf-8 -*-
"""A Veloce that is lofted rather than stacked, and brakes you can see.

THE MODELLING. Every panel on every car in this game is an axis aligned box,
which is why they read as boxy no matter how carefully the boxes are placed.
No amount of adding more boxes fixes that; the corners are still right angles.

So there is now a `loft`: a run of cross sections down the length of the car,
each one a rounded rectangle whose corner radius, width, roof height and floor
height are all set per station, skinned together and given smooth normals. It
is the way a real body is drawn and it stays low poly (nine stations of sixteen
points is 144 vertices for a whole flank). Because the normals are smooth, the
posterised lighting bands sweep around the curve instead of stopping dead at an
edge, which is exactly what the ember.lite look does with a curved surface.

Wheel arches are `TorusGeometry` arcs, so the lip over each wheel is a real
radius. The greenhouse is a second, smaller loft in glass with a lofted roof
panel over it, so the screen wraps into the sides rather than meeting them at
a corner.

THE BRAKES. They were already four wheel and always have been: 62 percent
front, 38 rear, both axles saturating under a hard stop, 100 to 0 in 30.7 m.
What was missing is that you could not SEE it. Every corner now carries a
drilled disc that turns with the wheel and a caliper that does not, on all four
wheels of all five cars. The bias also moves from 62/38 to 56/44, which is
about right for a car with this much rear weight and makes the back axle do
real work instead of trailing.

THE TEXTURES. The car sampled the same metal photograph as everything else.
There are now two baked procedurally at load: a paint with fine flake and the
faint horizontal orange peel a real panel has, and a carbon twill for the
splitter, the diffuser and the wing. Both are sampled in the body's own
coordinates like the rest of the vehicle, so they stick to the panel.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ==================================================== 1. two baked car textures
sub("var PHOTO_SAND=null, PHOTO_ROCK=null, PHOTO_PLAYA=null, PHOTO_METAL=null;",
    "var PHOTO_SAND=null, PHOTO_ROCK=null, PHOTO_PLAYA=null, PHOTO_METAL=null;\n"
    "var PHOTO_PAINT=null, PHOTO_CARBON=null;\n"
    "/* The car sampled the same photograph as the rock and the sand. These two\n"
    "   are drawn rather than photographed, because paint flake and carbon twill\n"
    "   are regular structures and a photograph of them tiles badly. */\n"
    "(function(){\n"
    "  function cv(n){ var c=document.createElement('canvas'); c.width=c.height=n; return c; }\n"
    "  function fin(c){\n"
    "    var t=new THREE.CanvasTexture(c);\n"
    "    t.wrapS=t.wrapT=THREE.RepeatWrapping;\n"
    "    t.magFilter=THREE.NearestFilter;\n"
    "    t.minFilter=THREE.LinearMipmapLinearFilter;\n"
    "    t.generateMipmaps=true; t.anisotropy=4;\n"
    "    return t;\n"
    "  }\n"
    "  /* paint: metallic flake, plus the faint horizontal orange peel a panel\n"
    "     picks up off the spray gun */\n"
    "  var a=cv(128), g=a.getContext('2d');\n"
    "  var im=g.createImageData(128,128), d=im.data;\n"
    "  for(var y=0;y<128;y++) for(var x=0;x<128;x++){\n"
    "    var i=(y*128+x)*4;\n"
    "    var flake=(Math.random()<0.055)? (Math.random()*74+40) : 0;\n"
    "    var peel=Math.sin(y*0.62)*5 + Math.sin(x*0.21+y*0.07)*4;\n"
    "    var v=138+peel+flake*0.55;\n"
    "    v=Math.round(Math.max(0,Math.min(255,v))/32)*32;   /* sit with the bands */\n"
    "    d[i]=d[i+1]=d[i+2]=v; d[i+3]=255;\n"
    "  }\n"
    "  g.putImageData(im,0,0); PHOTO_PAINT=fin(a);\n"
    "  /* carbon: a 2x2 twill, which is the weave you actually see on a splitter */\n"
    "  var b=cv(64), h=b.getContext('2d');\n"
    "  h.fillStyle='#6e6e6e'; h.fillRect(0,0,64,64);\n"
    "  for(var yy=0;yy<8;yy++) for(var xx=0;xx<8;xx++){\n"
    "    var over=((xx+yy)%4)<2;\n"
    "    h.fillStyle=over?'#9a9a9a':'#4c4c4c';\n"
    "    h.fillRect(xx*8,yy*8,8,8);\n"
    "    h.fillStyle='rgba(0,0,0,.18)';\n"
    "    h.fillRect(xx*8,yy*8,over?8:1,over?1:8);\n"
    "  }\n"
    "  PHOTO_CARBON=fin(b);\n"
    "})();")

sub("        opts.tex==='playa'? PHOTO_PLAYA : PHOTO_SAND)||GRAIN_TEX};",
    "        opts.tex==='playa'? PHOTO_PLAYA :\n"
    "        opts.tex==='paint'? PHOTO_PAINT :\n"
    "        opts.tex==='carbon'? PHOTO_CARBON : PHOTO_SAND)||GRAIN_TEX};")

# ============================================================ 2. the loft tool
sub("  function cyl(r,h,seg,m,x,y,z,rx,rz){",
    "  /* ---- loft ----------------------------------------------------------\n"
    "     A body drawn the way a body is drawn: a run of cross sections down the\n"
    "     length, skinned. Each section is a superellipse, so `n` sets how square\n"
    "     the corners are (2 is an ellipse, 8 is nearly a box) and the roof and\n"
    "     floor heights are separate, which is what a car section actually looks\n"
    "     like. Normals are smoothed, so the posterised bands sweep around the\n"
    "     curve instead of stopping at an edge.\n"
    "\n"
    "     secs: [{z, w, y, up, dn, n}]   a0/a1: an arc in turns, for roof panels\n"
    "  */\n"
    "  var LOFT_SEG=16;\n"
    "  function loftGeo(secs,a0,a1,cap){\n"
    "    var closed=(a0===undefined);\n"
    "    if(closed){ a0=0; a1=1; }\n"
    "    var N=closed?LOFT_SEG:Math.max(3,Math.round(LOFT_SEG*(a1-a0))+1);\n"
    "    var pos=[], idx=[];\n"
    "    for(var si=0;si<secs.length;si++){\n"
    "      var S0=secs[si], e=2/(S0.n||4);\n"
    "      for(var k=0;k<N;k++){\n"
    "        var t=(a0+(a1-a0)*(closed? k/N : k/(N-1)))*Math.PI*2;\n"
    "        var ct=Math.cos(t), st=Math.sin(t);\n"
    "        var sx=ct<0?-1:1, sy=st<0?-1:1;\n"
    "        var hh=(st>=0? S0.up : S0.dn);\n"
    "        pos.push(S0.w*sx*Math.pow(Math.abs(ct),e),\n"
    "                 S0.y + hh*sy*Math.pow(Math.abs(st),e),\n"
    "                 S0.z);\n"
    "      }\n"
    "    }\n"
    "    var ring=N;\n"
    "    for(var si2=0;si2<secs.length-1;si2++){\n"
    "      var A=si2*ring, B=(si2+1)*ring;\n"
    "      var lim=closed?N:N-1;\n"
    "      for(var k2=0;k2<lim;k2++){\n"
    "        var k3=(k2+1)%N;\n"
    "        idx.push(A+k2,B+k2,B+k3, A+k2,B+k3,A+k3);\n"
    "      }\n"
    "    }\n"
    "    if(cap!==false && closed){        /* close the nose and the tail */\n"
    "      var c0=pos.length/3;\n"
    "      var f=secs[0], l=secs[secs.length-1];\n"
    "      pos.push(0,f.y,f.z); pos.push(0,l.y,l.z);\n"
    "      var c1=c0+1, last=(secs.length-1)*ring;\n"
    "      for(var k4=0;k4<N;k4++){\n"
    "        var k5=(k4+1)%N;\n"
    "        idx.push(c0,k5,k4);\n"
    "        idx.push(c1,last+k4,last+k5);\n"
    "      }\n"
    "    }\n"
    "    var gg=new THREE.BufferGeometry();\n"
    "    gg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));\n"
    "    gg.setIndex(idx);\n"
    "    gg.computeVertexNormals();\n"
    "    return gg;\n"
    "  }\n"
    "  function loft(secs,m,a0,a1,cast,cap){\n"
    "    return add(new THREE.Mesh(loftGeo(secs,a0,a1,cap),m),0,0,0,cast);\n"
    "  }\n"
    "  /* a wheel arch with a real radius over it, rather than a slab */\n"
    "  function archT(m,x,y,z,R,tube,arc){\n"
    "    var g=new THREE.TorusGeometry(R,tube,6,14,arc||Math.PI);\n"
    "    var t=new THREE.Mesh(g,m);\n"
    "    t.rotation.y=Math.PI/2;\n"
    "    return add(t,x,y,z,false);\n"
    "  }\n"
    "  function cyl(r,h,seg,m,x,y,z,rx,rz){")

# ============================================================= 3. the new shell
old_shell_start = "  function shellVeloce(V){\n    W=V.W;\n    box(W,0.34,4.30, paint, 0,-0.08, 0.00);"
assert old_shell_start in s, 'shellVeloce anchor moved'
i0 = s.index("  /* ---- Veloce GT:")
i1 = s.index("  var SHELLS={bracken:shellBracken,")
new_shell = """  /* ---- Veloce GT ------------------------------------------------------
     Lofted, not stacked. Nine stations down the flank, each a rounded
     rectangle: narrow and low at the nose, widest and squarest over the rear
     axle, tapering into a cut off tail. The greenhouse is its own loft so the
     screen wraps into the sides, and the arches are torus arcs so the lip over
     each wheel is a radius. Smooth normals throughout, which is what lets the
     light band sweep around a haunch. */
  function shellVeloce(V){
    W=V.W;
    var hw=W/2;
    /* the hull: {z along the car, w half width, y centre, up roof, dn floor,
       n how square the section is} */
    loft([
      {z: 2.16, w:hw*0.56, y:-0.10, up:0.10, dn:0.09, n:2.6},
      {z: 1.88, w:hw*0.80, y:-0.05, up:0.17, dn:0.15, n:3.0},
      {z: 1.44, w:hw*0.94, y: 0.00, up:0.24, dn:0.19, n:3.4},
      {z: 0.86, w:hw*0.99, y: 0.03, up:0.28, dn:0.22, n:3.8},
      {z: 0.10, w:hw*1.00, y: 0.04, up:0.30, dn:0.24, n:4.2},
      {z:-0.72, w:hw*1.00, y: 0.06, up:0.32, dn:0.24, n:4.4},
      {z:-1.42, w:hw*0.98, y: 0.05, up:0.30, dn:0.22, n:4.0},
      {z:-1.94, w:hw*0.88, y: 0.02, up:0.24, dn:0.18, n:3.4},
      {z:-2.16, w:hw*0.72, y: 0.00, up:0.18, dn:0.14, n:3.0}
    ], paint);

    /* the greenhouse, its own loft, so the screen turns into the side glass */
    loft([
      {z: 1.18, w:hw*0.60, y: 0.30, up:0.05, dn:0.14, n:2.6},
      {z: 0.76, w:hw*0.70, y: 0.40, up:0.15, dn:0.20, n:3.0},
      {z: 0.14, w:hw*0.76, y: 0.45, up:0.20, dn:0.24, n:3.6},
      {z:-0.48, w:hw*0.74, y: 0.43, up:0.18, dn:0.24, n:3.6},
      {z:-1.02, w:hw*0.62, y: 0.34, up:0.09, dn:0.20, n:2.8}
    ], glass, undefined, undefined, false);
    /* and a roof panel over the top third of it, in body colour */
    loft([
      {z: 0.52, w:hw*0.70, y: 0.41, up:0.17, dn:0.20, n:3.0},
      {z: 0.14, w:hw*0.77, y: 0.45, up:0.21, dn:0.24, n:3.6},
      {z:-0.48, w:hw*0.75, y: 0.43, up:0.19, dn:0.24, n:3.6},
      {z:-0.94, w:hw*0.64, y: 0.35, up:0.11, dn:0.20, n:2.8}
    ], paint, 0.15, 0.35, false);

    /* arches with a radius over them */
    var ay=V.wheelR*0.36-V.bodyY-0.30;
    [[1.42],[-1.44]].forEach(function(a){
      archT(flare, -hw*0.99, ay, a[0], V.wheelR*1.12, 0.075);
      archT(flare,  hw*0.99, ay, a[0], V.wheelR*1.12, 0.075);
    });

    /* aero, in carbon: splitter, side skirts, diffuser, wing */
    box(W+0.16,0.05,0.60, carbon, 0,-0.20, 1.92, false);
    box(0.10,0.11,2.36, carbon, -hw-0.02,-0.20, 0.05, false);
    box(0.10,0.11,2.36, carbon,  hw+0.02,-0.20, 0.05, false);
    var dif=box(W-0.10,0.16,0.52, carbon, 0,-0.19,-1.96, false);
    dif.rotation.x=-0.30;
    for(var f=-2;f<=2;f++) box(0.05,0.15,0.50, trim, f*0.34,-0.18,-1.96, false);
    [[-0.60],[0.60]].forEach(function(pp){
      var st=box(0.06,0.32,0.11, carbon, pp[0],0.60,-1.84, false);
      st.rotation.x=0.12;
    });
    var wing=box(W+0.18,0.055,0.42, carbon, 0, 0.80,-1.86, false);
    wing.rotation.x=0.13;
    box(W+0.18,0.05,0.13, carbon, 0, 0.735,-1.70, false);

    /* lamps: slim, set into the nose, and a light bar across the tail */
    cyl(0.085,0.10,10, lampM, -0.62,0.13,2.00, Math.PI/2);
    cyl(0.085,0.10,10, lampM,  0.62,0.13,2.00, Math.PI/2);
    box(0.46,0.055,0.06, lampM, -0.50,0.19,1.99, false);
    box(0.46,0.055,0.06, lampM,  0.50,0.19,1.99, false);
    box(W-0.30,0.075,0.05, tailM, 0, 0.20,-2.14, false);
    box(0.13,0.09,0.05, tailM, 0,-0.10,-2.12, false);

    /* mirrors and an intake behind the door, which is what says mid engine */
    [[-1],[1]].forEach(function(sd){
      var st2=box(0.05,0.05,0.20, trim, sd[0]*(hw*0.80), 0.40, 0.66, false);
      box(0.16,0.09,0.09, second, sd[0]*(hw*0.94), 0.42, 0.60, false);
      return st2;
    });
    box(0.05,0.20,0.52, trim, -hw*1.00, 0.16,-0.62, false);
    box(0.05,0.20,0.52, trim,  hw*1.00, 0.16,-0.62, false);
  }

"""
s = s[:i0] + new_shell + s[i1:]
n += 1

# ============================================ 4. materials for the new surfaces
sub("  var flare  = smat(0x6f6675);",
    "  var flare  = smat(0x6f6675);\n"
    "  /* drawn textures rather than the rock photograph everything else uses */\n"
    "  var carbon = styleMat(mat(0x2b2d31),{obj:true,tex:'carbon'});\n"
    "  var discM  = styleMat(mat(0x8a8378),{obj:true,tex:'metal'});\n"
    "  var calM   = styleMat(mat(0xc4452c),{obj:true,tex:'metal'});")

# the body paint should use the paint texture, and curve smoothly
sub("  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95],obj:true,tex:'metal'});",
    "  var paint  = styleMat(mat(0x3f9dab,{flatShading:false}),\n"
    "                        {rim:[2.4,0.95],obj:true,tex:'paint'});")

# ================================================ 5. brakes you can see, x4
sub("            rim:C(R*0.63,Wd*1.06,8), hub:C(R*0.20,Wd*1.16,6)};",
    "            rim:C(R*0.63,Wd*1.06,8), hub:C(R*0.20,Wd*1.16,6),\n"
    "            disc:C(R*0.62,Wd*0.14,14), cal:new THREE.BoxGeometry(Wd*0.30,R*0.34,R*0.20)};")

sub("    hubg.add(new THREE.Mesh(hubGeo,chrome));",
    "    hubg.add(new THREE.Mesh(hubGeo,chrome));\n"
    "    /* A disc that turns with the wheel and a caliper that does not, on all\n"
    "       four corners. The braking was always on all four; you could not see\n"
    "       it. Appended last so the STRUT indices above still hold. */\n"
    "    var disc=new THREE.Mesh(WG.disc,discM); hubg.add(disc);\n"
    "    var cal=new THREE.Mesh(WG.cal,calM);\n"
    "    cal.position.set(0,WHEEL_R*0.44,-WHEEL_R*0.30); grp.add(cal);")

sub("    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim,",
    "    STRUT.push({disc:disc,cal:cal,\n"
    "                grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim,")

sub("      st.rim.geometry=g.rim;    st.hubc.geometry=g.hub;",
    "      st.rim.geometry=g.rim;    st.hubc.geometry=g.hub;\n"
    "      st.disc.geometry=g.disc;  st.cal.geometry=g.cal;\n"
    "      st.cal.position.set(0,V.wheelR*0.44,-V.wheelR*0.30);")

# ============================== 6. and let the rear axle do some of the work
sub("arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.62,",
    "arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.56,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
