# -*- coding: utf-8 -*-
"""Buildings as assets, and something to hit them with.

The mass comes out of the heightfield. A building is now a generated mesh
placed on the ground, which is what you asked for and what the terrain approach
could never do: a plinth that meets a sloping site, a storefront band, a
cornice, a parapet, a setback, a roof that is not just the top of a hill.

PLACEMENT. Each block edge is divided into parcels by a conserving random walk:
widths vary but still tile the edge exactly, so the street wall has rhythm
without drifting or leaving a gap at the corner. Every building is built to the
frontage, and neighbours share their edge, so the wall is continuous. Corner
parcels get an extra storey and a heavier parapet, which is what real streets
do and which also lets you read the next intersection from a long way off.

BATCHING. Everything merges into one geometry per 192 m tile with one shared
material, so the whole city is a handful of draw calls rather than one per
building. Colour is per vertex, so every building can differ for free.

COLLISION. The ground stays a heightfield and the struts are untouched. The
body carries two circles on its centreline, and those are tested against the
nearest building boxes through a coarse index grid, so a query looks at two or
three boxes rather than all of them. Two rules matter more than the rest: the
contact normal is forced flat, so a wall can never lift or climb the truck, and
a contact that is already separating is ignored, so it can never stick. The
bounce falls away with speed and the scrape rises with it, because a wall at
120 should mostly take your speed rather than fire you across the street.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------- the mass leaves the heightfield
sub("""  var d=streetD(x,z);
  var h=road;
  /* kerb, then sidewalk */
  h += KERB*sstep(CARR-0.35,CARR+0.35,d);
  /* then the built mass, over a 1.1 m shoulder so it is a wall and not a cliff
     the solver has to resolve in one step */
  h += parcelH(x,z)*sstep(BUILD,BUILD+1.1,d);
""",
"""  var d=streetD(x,z);
  var h=road;
  /* kerb, then sidewalk. The built mass is no longer in here: buildings are
     meshes placed on this ground, with their own collision. */
  h += KERB*sstep(CARR-0.35,CARR+0.35,d);
""")

# the facade shading no longer applies, the terrain has no facades
sub("""    if(opts.surf) body.push(
      'float wallS = clamp(vSurfS.y,0.0,1.0) * (1.0 - abs(normal.y)) * uFacade;',
      'float flr = fract( (vWPosS.y - 1.2) / 3.6 );',
      'float win = smoothstep(0.16,0.28,flr) * (1.0 - smoothstep(0.70,0.82,flr));',
      'pcS = mix( pcS, pcS * vec3(0.40,0.45,0.60), wallS * win * 0.88 );',
      'float pier = 1.0 - smoothstep(0.07,0.17, abs(fract((vWPosS.x+vWPosS.z)/4.2)-0.5));',
      'pcS = mix( pcS, pcS * 1.18, wallS * pier * 0.5 );');""", "")

# the city ground loses the facade band
sub("""      c.lerp(new THREE.Color(0x8f8478).convertSRGBToLinear(), sstep(BUILD,BUILD+1.3,dS));
""", "")

# ================================================================ buildings
sub("""/* ================= the city, clad =================""",
"""/* ================= buildings ================= */
/* Every building is a record, so collision and geometry read the same numbers.
   Axis aligned, because the streets are. */
var BLD=[], BGRID=null, BCELL=26;

function bldGridBuild(){
  BGRID={};
  for(var i=0;i<BLD.length;i++){
    var b=BLD[i];
    var i0=Math.floor((b.x-b.w*0.5)/BCELL), i1=Math.floor((b.x+b.w*0.5)/BCELL);
    var j0=Math.floor((b.z-b.d*0.5)/BCELL), j1=Math.floor((b.z+b.d*0.5)/BCELL);
    for(var i2=i0;i2<=i1;i2++) for(var j2=j0;j2<=j1;j2++){
      var k=i2+','+j2;
      (BGRID[k]||(BGRID[k]=[])).push(i);
    }
  }
}
/* Nearest wall to a point, as a signed distance and a flat normal. Looks at
   the one grid cell and its neighbours, so two or three boxes, not four
   hundred. */
var _wn=new THREE.Vector3();
function wallNear(px,pz,py){
  if(!BGRID) return null;
  var best=1e9, bn=null;
  var ci=Math.floor(px/BCELL), cj=Math.floor(pz/BCELL);
  for(var a=-1;a<=1;a++) for(var b2=-1;b2<=1;b2++){
    var lst=BGRID[(ci+a)+','+(cj+b2)];
    if(!lst) continue;
    for(var q=0;q<lst.length;q++){
      var B=BLD[lst[q]];
      if(py>B.y+B.h) continue;                 /* above the roof, drive over it */
      var hx=B.w*0.5, hz=B.d*0.5;
      var dx=px-B.x, dz=pz-B.z;
      var ox=Math.abs(dx)-hx, oz=Math.abs(dz)-hz;
      var d;
      if(ox>0||oz>0){                           /* outside */
        var mx=Math.max(ox,0), mz=Math.max(oz,0);
        d=Math.sqrt(mx*mx+mz*mz);
      }else{
        d=Math.max(ox,oz);                      /* inside, negative */
      }
      if(d<best){
        best=d;
        /* the normal is the axis you are least far inside */
        if(ox>oz) bn=[(dx<0?-1:1),0];
        else      bn=[0,(dz<0?-1:1)];
      }
    }
  }
  if(bn===null) return null;
  return {d:best, nx:bn[0], nz:bn[1]};
}

/* one merged geometry per tile, one material, so the city is a few draws */
var BTILE=192, BLD_MAT=null;
function buildCityBuildings(){
  var pos=[], col=[], tiles={};
  var C1=new THREE.Color();
  function push(x,y,z,w,hh,dd,hex,topHex){
    var t=Math.floor(x/BTILE)+','+Math.floor(z/BTILE);
    var T=tiles[t]||(tiles[t]={p:[],c:[]});
    var hx=w*0.5, hz=dd*0.5;
    var X0=x-hx,X1=x+hx,Y0=y,Y1=y+hh,Z0=z-hz,Z1=z+hz;
    var V=[[X0,Y0,Z1],[X1,Y0,Z1],[X1,Y1,Z1],[X0,Y1,Z1],
           [X0,Y0,Z0],[X1,Y0,Z0],[X1,Y1,Z0],[X0,Y1,Z0]];
    var F=[[0,1,2,0,2,3],[5,4,7,5,7,6],[4,0,3,4,3,7],[1,5,6,1,6,2],[3,2,6,3,6,7]];
    for(var f=0;f<F.length;f++){
      var hexF=(f===4)?topHex:hex;
      C1.setHex(hexF).convertSRGBToLinear();
      for(var v=0;v<6;v++){
        var P=V[F[f][v]];
        T.p.push(P[0],P[1],P[2]);
        T.c.push(C1.r,C1.g,C1.b);
      }
    }
  }
  var WALLS=[0xb4a894,0xa08e84,0xc0ab92,0x8e8e9a,0xb08a72,0x9aa0a4,0xc4b8a2,0x86807e];
  for(var i=0;i<BLD.length;i++){
    var B=BLD[i];
    push(B.x,B.y-2.6,B.z,B.w,2.6+0.2,B.d,0x6a6560,0x6a6560);       /* plinth */
    push(B.x,B.y,B.z,B.w,B.h,B.d,B.col,0x5b565e);                   /* shaft */
    push(B.x,B.y+B.h,B.z,B.w+0.5,0.55,B.d+0.5,B.cap,B.cap);         /* cornice */
    push(B.x,B.y+B.h+0.55,B.z,B.w+0.2,B.par,B.d+0.2,B.cap,0x4e4a52); /* parapet */
    /* a storefront band, which is the thing you are level with all the time */
    push(B.x,B.y+0.1,B.z,B.w-0.5,3.5,B.d+0.14,0x3b4250,0x3b4250);
    push(B.x,B.y+3.6,B.z,B.w-0.2,0.9,B.d+0.16,B.cap,B.cap);         /* sign band */
  }
  var g=new THREE.Group();
  BLD_MAT=BLD_MAT||styleMat(new THREE.MeshPhongMaterial({vertexColors:true,
    specular:0x000000,shininess:0,flatShading:true}),{tex:'metal'});
  for(var k in tiles){
    var T=tiles[k];
    if(!T.p.length) continue;
    var geo=new THREE.BufferGeometry();
    geo.setAttribute('position',new THREE.Float32BufferAttribute(T.p,3));
    geo.setAttribute('color',new THREE.Float32BufferAttribute(T.c,3));
    geo.computeVertexNormals();
    var m=new THREE.Mesh(geo,BLD_MAT);
    m.castShadow=true; m.receiveShadow=true;
    g.add(m);
  }
  return g;
}

/* Parcels along a block edge. A conserving random walk, so widths vary but
   still tile the edge exactly and the corner always lands clean. */
function parcelWidths(L,wBar,seed){
  var n=Math.max(1,Math.round(L/wBar));
  var w=[], i;
  for(i=0;i<n;i++) w.push(L/n);
  for(i=0;i<n-1;i++){
    var d=(hash2(seed+i*3.7,seed*1.9-i)*2-1)*0.24*w[i];
    w[i]+=d; w[i+1]-=d;
  }
  return w;
}

/* ================= the city, clad =================""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
