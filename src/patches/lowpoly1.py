# -*- coding: utf-8 -*-
"""The actual low poly look: one flat colour per triangle.

This is the thing that was missing. The terrain colour was computed per
fragment from world position, so even with flat shading the colour gradated
smoothly across every triangle. Flat LIGHTING is not flat SHADING. The facets
were there and you could not see them, which is why it read as a smooth
stylised wash rather than as low poly.

The fix is the way everyone does it: a non indexed mesh, colour baked per face
on the CPU, all three vertices of a triangle carrying the same value, so the
interpolation across the face is constant. Adjacent facets now differ from each
other in a visible step, and that step is the whole look.

While in here: cells go from 4 m to 5 m so the facets are bigger and countable,
face to face value variation is pushed from plus or minus six percent to plus
or minus fourteen so neighbours actually read as separate planes, and the
whoops lengthen to twenty metres so a five metre mesh can still resolve them.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("var WORLD=560, HALF=WORLD/2, GRID=4.0;", "var WORLD=560, HALF=WORLD/2, GRID=5.0;")

sub("""  /* The whoop run. Sixteen metre wavelength so the four metre mesh resolves
     it, which matters because what you see has to match what you feel. */
  var wc=band(z,-48,11,9)*band(x,26,92,28);
  h += Math.sin(x*0.393)*1.15*wc;""",
"""  /* The whoop run. Twenty metre wavelength so a five metre mesh resolves it,
     which matters because what you see has to match what you feel. */
  var wc=band(z,-48,12,10)*band(x,26,96,30);
  h += Math.sin(x*0.314)*1.35*wc;""")

# ---------------------------------------------------------------- terrain
a = s.index("var terrainMat;")
b = s.index("/* ================= sky, sun, backdrop ================= */")
new_terrain = '''var terrainMat;
(function(){
  var N=Math.round(WORLD/GRID), V=N+1;

  /* Vertex grid first. Jitter x and z before sampling height: it kills the
     regular grid without touching the physics, which reads the analytic
     function and never sees the mesh. */
  var gx=new Float32Array(V*V), gy=new Float32Array(V*V), gz=new Float32Array(V*V);
  for(var j=0;j<V;j++) for(var i=0;i<V;i++){
    var edge=(i===0||j===0||i===N||j===N);
    var x=-HALF+i*GRID, z=-HALF+j*GRID;
    if(!edge){
      x += (hash2(i*1.7,j*3.1)-0.5)*GRID*0.66;
      z += (hash2(i*5.3,j*2.9)-0.5)*GRID*0.66;
    }
    var k=j*V+i;
    gx[k]=x; gz[k]=z; gy[k]=height(x,z);
  }

  var TRIS=N*N*2;
  var pos=new Float32Array(TRIS*9), col=new Float32Array(TRIS*9);
  var cLow=sc(PAL.low), cMid=sc(PAL.mid), cHigh=sc(PAL.high),
      cRock=sc(PAL.rock), cPlaya=sc(PAL.playa);
  var c=new THREE.Color(), t=0;

  function face(i0,i1,i2,fi){
    var ax=gx[i0],ay=gy[i0],az=gz[i0];
    var bx2=gx[i1],by=gy[i1],bz2=gz[i1];
    var cx2=gx[i2],cy2=gy[i2],cz2=gz[i2];

    /* the face's own normal, for slope */
    var e1x=bx2-ax, e1y=by-ay, e1z=bz2-az;
    var e2x=cx2-ax, e2y=cy2-ay, e2z=cz2-az;
    var nx=e1y*e2z-e1z*e2y, ny=e1z*e2x-e1x*e2z, nz=e1x*e2y-e1y*e2x;
    var nl=Math.sqrt(nx*nx+ny*ny+nz*nz)||1;
    var slope=1-Math.abs(ny/nl);

    var mx=(ax+bx2+cx2)/3, my=(ay+by+cy2)/3, mz=(az+bz2+cz2)/3;

    c.copy(cLow).lerp(cMid, sstep(-11,-2,my));
    c.lerp(cHigh, sstep(1,13,my));
    c.lerp(cPlaya, lakeMask(mx,mz));
    c.lerp(cRock, sstep(0.24,0.52,slope));

    /* Quantised per face value, in five steps. This is what makes one facet
       read as a different plane from the one beside it. */
    var hsh=hash2(Math.floor(mx*0.37)+fi*0.013, Math.floor(mz*0.37));
    var step=Math.round(hsh*4)/4;
    var g=0.86+step*0.28;

    var o=t*9;
    pos[o]=ax; pos[o+1]=ay; pos[o+2]=az;
    pos[o+3]=bx2; pos[o+4]=by; pos[o+5]=bz2;
    pos[o+6]=cx2; pos[o+7]=cy2; pos[o+8]=cz2;
    var r=c.r*g, gg=c.g*g, bb=c.b*g;
    col[o]=r; col[o+1]=gg; col[o+2]=bb;
    col[o+3]=r; col[o+4]=gg; col[o+5]=bb;
    col[o+6]=r; col[o+7]=gg; col[o+8]=bb;
    t++;
  }

  /* pick each quad's diagonal along the smaller height difference, or the
     whole basin shows a herringbone grain */
  var fi=0;
  for(var jj=0;jj<N;jj++) for(var ii=0;ii<N;ii++){
    var q0=jj*V+ii, q1=q0+1, q2=q0+V, q3=q2+1;
    if(Math.abs(gy[q0]-gy[q3]) <= Math.abs(gy[q1]-gy[q2])){
      face(q0,q2,q3,fi++); face(q0,q3,q1,fi++);
    }else{
      face(q0,q2,q1,fi++); face(q1,q2,q3,fi++);
    }
  }

  var g2=new THREE.BufferGeometry();
  g2.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g2.setAttribute('color',new THREE.BufferAttribute(col,3));
  g2.computeVertexNormals();

  /* Phong shades per fragment, so flatShading can take the facet normal from
     screen space derivatives. The colour is already constant per face. */
  terrainMat=new THREE.MeshPhongMaterial({
    vertexColors:true, specular:0x000000, shininess:0, flatShading:true});

  var mesh=new THREE.Mesh(g2,terrainMat);
  /* Dunes do not cast. A nine degree sun already bands them through N dot L
     for free, and keeping the sheet out of the shadow pass pays for the rest. */
  mesh.castShadow=false; mesh.receiveShadow=true;
  scene.add(mesh);
})();

'''
s = s[:a] + new_terrain + s[b:]
n += 1

# the detail texture block sat inside the replaced range, so it is already gone

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
print('detailTex left over:', 'detailTex' in s)
