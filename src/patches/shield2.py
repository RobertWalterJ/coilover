# -*- coding: utf-8 -*-
"""Pike Narrows, stage two: what is standing on it.

Built on demand from setMap with MAP already 2, never as an IIFE at load, which
is the mistake that put every city building at desert elevation.

BUSH. Spruce and birch as instanced meshes, three draw calls for about nine
hundred trees. Spruce are stacked cones with a bare trunk and they crowd the
low wet ground; birch are pale and stand in clumps on the drier slopes. Nothing
grows on bare granite, in the water, on the road or on the esker, which is what
makes those things read as clearings rather than as painted stripes.

ERRATICS. Boulders the ice dropped, on and around the domes.

WATER. One disc per lake at the shared level, sitting just under the shoreline
so the ground meets it rather than ending at it.

THE PLACES PEOPLE ARE. Camps on the shore, each one a gable cottage with lit
windows, a dock out into the water with a canoe on it, a woodpile, a propane
tank and an outhouse. A general store with a hand painted sign at the road
junction. A pickup on blocks. A fire tower on the highest dome. Hydro poles
following the haul road with the wire slung between them.

Cottages, the store, the tower legs and the bigger trunks all go into the same
BLD collision list the city uses, so they are solid, and the windows go into
LGLOW flagged `shield` so the light pool picks them up at dusk and so a rebuild
does not leave the city's lamps behind.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

CODE = r"""
/* ================= Pike Narrows, built =================
   On demand from setMap, with MAP already 2 so every height() call below reads
   the Shield's ground and not the desert's. */
function buildShieldProps(){
  while(G_SHIELD.children.length){
    var old=G_SHIELD.children[0];
    old.traverse(function(o){ if(o.geometry) o.geometry.dispose(); });
    G_SHIELD.remove(old);
  }
  BLD.length=0;
  LGLOW=LGLOW.filter(function(e){ return !e.shield; });

  function m(col,tex){
    return styleMat(new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true}),{tex:tex||'rock'});
  }
  function lit(col,em,strength){
    var mm=new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true});
    mm.emissive=new THREE.Color(0x000000);
    LGLOW.push({m:mm,c:new THREE.Color(em),s:strength===undefined?0.9:strength,shield:true});
    return mm;
  }
  var spruceM=m(0x2f4a35), spruce2M=m(0x3c5a3e), trunkM=m(0x4a3b30),
      birchM=m(0xd8d4c4), leafM=m(0x6f8a44),
      graniteM=m(0x8a8076,'rock'), woodM=m(0x8a6a48), roofM2=m(0x6a4a3c),
      tinM=m(0x9aa0a2,'metal'), rustM=m(0x8c5a3a,'metal'), poleM=m(0x5a4a3c),
      wireM=m(0x2e2a28,'metal'), dockM=m(0x9a8a72), canoeM=m(0xc4562f),
      steelM=m(0x6d6a66,'metal'), tankM=m(0xc9c5b4,'metal'),
      winM=lit(0xfff0cc,0xffcf92,0.95);

  /* ---- water: one disc per lake, just under the shoreline ---- */
  var waterM=styleMat(new THREE.MeshPhongMaterial({color:sc(0x25454a),
    specular:0x000000, shininess:0, flatShading:true,
    transparent:true, opacity:0.90}),{});
  for(var li=0;li<SH_LAKES.length;li++){
    var L=SH_LAKES[li];
    var wg=new THREE.CircleGeometry(1,26);
    var wm=new THREE.Mesh(wg,waterM);
    wm.rotation.x=-Math.PI/2;
    wm.scale.set(L[2]*1.06,L[3]*1.06,1);
    wm.position.set(L[0],SH_WATER,L[1]);
    wm.rotation.z=-L[4];
    wm.receiveShadow=true;
    G_SHIELD.add(wm);
  }

  /* ---- somewhere a thing may stand ---- */
  function clear(x,z,needRoad){
    if(Math.hypot(x,z)>206) return false;
    if(shLakeD(x,z)<1.05) return false;
    var onRoad=(shRoadD(x,z)<8.5 || shEskerD(x,z)<13);
    if(needRoad) return onRoad;
    return !onRoad;
  }

  /* ---- the bush ---- */
  var NS=560, NB=300;
  var coneG=new THREE.ConeGeometry(1,1,7);
  var cylG=new THREE.CylinderGeometry(1,1,1,6);
  var crownG=new THREE.IcosahedronGeometry(1,0);
  var spruceI=new THREE.InstancedMesh(coneG,spruceM,NS);
  var spruce2I=new THREE.InstancedMesh(coneG,spruce2M,NS);
  var trunkI=new THREE.InstancedMesh(cylG,trunkM,NS+NB);
  var crownI=new THREE.InstancedMesh(crownG,leafM,NB);
  var birchI=new THREE.InstancedMesh(cylG,birchM,NB);
  spruceI.castShadow=spruce2I.castShadow=crownI.castShadow=true;
  trunkI.castShadow=birchI.castShadow=true;
  var d=new THREE.Object3D(), ns=0, nb=0, nt=0, guard=0;

  while((ns<NS||nb<NB) && guard++<9000){
    var x=(hash2(guard*1.7,4.1)-0.5)*2*202, z=(hash2(guard*2.3,9.7)-0.5)*2*202;
    if(!clear(x,z)) continue;
    if(shDome(x,z)>0.34) continue;                  /* nothing grows on bare rock */
    normalAt(x,z,_n1);
    if(_n1.y<0.80) continue;                        /* nor on a cliff */
    var y=height(x,z);
    var wet=shBog(x,z);
    var isSpruce = (hash2(guard,5.5) < 0.62+wet*0.3);
    if(isSpruce && ns<NS){
      var hgt=5.0+hash2(guard,1.3)*7.5-wet*1.6;
      var rad=hgt*0.20;
      d.position.set(x,y+hgt*0.52,z); d.scale.set(rad,hgt*0.66,rad);
      d.rotation.set(0,hash2(guard,3.9)*6,0); d.updateMatrix();
      spruceI.setMatrixAt(ns,d.matrix);
      d.position.set(x,y+hgt*0.86,z); d.scale.set(rad*0.66,hgt*0.42,rad*0.66);
      d.updateMatrix(); spruce2I.setMatrixAt(ns,d.matrix);
      d.position.set(x,y+hgt*0.14,z); d.scale.set(0.17,hgt*0.30,0.17);
      d.rotation.set(0,0,0); d.updateMatrix(); trunkI.setMatrixAt(nt++,d.matrix);
      /* the big ones are solid; the saplings are not worth the collision */
      if(hgt>9.0) BLD.push({x:x,z:z,w:0.9,d:0.9,y:y-1,h:hgt});
      ns++;
    }else if(nb<NB){
      var bh=6.0+hash2(guard,7.1)*5.0;
      d.position.set(x,y+bh*0.46,z); d.scale.set(0.13,bh*0.5,0.13);
      d.rotation.set(0,0,(hash2(guard,2.7)-0.5)*0.20); d.updateMatrix();
      birchI.setMatrixAt(nb,d.matrix);
      var cr=1.5+hash2(guard,6.3)*1.4;
      d.position.set(x,y+bh*0.92,z); d.scale.set(cr,cr*0.80,cr);
      d.rotation.set(hash2(guard,8.1)*2,hash2(guard,4.4)*6,0); d.updateMatrix();
      crownI.setMatrixAt(nb,d.matrix);
      nb++;
    }
  }
  spruceI.count=ns; spruce2I.count=ns; trunkI.count=nt;
  birchI.count=nb; crownI.count=nb;
  [spruceI,spruce2I,trunkI,birchI,crownI].forEach(function(o){
    o.instanceMatrix.needsUpdate=true; G_SHIELD.add(o); });

  /* ---- erratics: what the ice left behind ---- */
  var errG=new THREE.DodecahedronGeometry(1,0);
  var errI=new THREE.InstancedMesh(errG,graniteM,190);
  errI.castShadow=errI.receiveShadow=true;
  var ne=0; guard=0;
  while(ne<190 && guard++<4000){
    var ex=(hash2(guard*3.1,11.3)-0.5)*2*200, ez=(hash2(guard*1.9,17.7)-0.5)*2*200;
    if(!clear(ex,ez)) continue;
    if(shDome(ex,ez)<0.10 && hash2(guard,9.1)<0.6) continue;   /* they cluster on rock */
    var ey=height(ex,ez), es=0.9+hash2(guard,2.2)*3.4;
    d.position.set(ex,ey-es*0.30,ez); d.scale.set(es,es*0.76,es*1.12);
    d.rotation.set(hash2(guard,1.4)*3,hash2(guard,5.2)*6,hash2(guard,3.6)*3);
    d.updateMatrix(); errI.setMatrixAt(ne++,d.matrix);
  }
  errI.count=ne; errI.instanceMatrix.needsUpdate=true; G_SHIELD.add(errI);

  /* ---- a thing built out of boxes, with collision ---- */
  function put(g,w,h,dp,mat,x,y,z,cast){
    var b=new THREE.Mesh(new THREE.BoxGeometry(w,h,dp),mat);
    b.position.set(x,y,z); if(cast!==false) b.castShadow=true;
    b.receiveShadow=true; g.add(b); return b;
  }

  /* ---- a camp on the shore ---- */
  function camp(cx,cz,ang){
    var g=new THREE.Group();
    var gy=height(cx,cz);
    g.position.set(cx,gy,cz); g.rotation.y=ang; G_SHIELD.add(g);
    /* the cottage: gable roof, screened porch, lit windows */
    put(g,6.2,2.9,4.6, woodM, 0,1.45,0);
    var r1=put(g,4.0,0.22,4.9, roofM2, -1.6,3.28,0); r1.rotation.z= 0.62;
    var r2=put(g,4.0,0.22,4.9, roofM2,  1.6,3.28,0); r2.rotation.z=-0.62;
    put(g,0.9,1.1,0.14, winM, -1.7,1.75, 2.33, false);
    put(g,0.9,1.1,0.14, winM,  1.7,1.75, 2.33, false);
    put(g,0.14,1.1,0.9, winM, -3.13,1.75, 0.6, false);
    put(g,2.4,2.2,2.0, woodM, 0,1.10, 3.20);          /* porch */
    put(g,2.6,0.14,2.2, tinM, 0,2.26, 3.24, false);
    put(g,0.9,0.16,1.2, dockM, 0,0.08, 4.50, false);  /* step */
    /* woodpile, propane, outhouse: the three things every camp has */
    for(var wl=0;wl<10;wl++)
      put(g,1.9,0.20,0.20, trunkM, -4.6,0.16+Math.floor(wl/5)*0.22,
          -1.4+(wl%5)*0.24, false);
    var tk=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,1.5,10),tankM);
    tk.rotation.z=Math.PI/2; tk.position.set(4.3,0.52,-1.1); tk.castShadow=true; g.add(tk);
    put(g,1.1,2.0,1.1, woodM, 5.0,1.00, 2.6);
    put(g,1.3,0.14,1.3, tinM, 5.0,2.06, 2.6, false);
    BLD.push({x:cx,z:cz,w:7.0,d:5.4,y:gy-1,h:3.6});
    return g;
  }

  /* ---- a dock, reaching from a shore out over the water ---- */
  function dock(sx,sz,dirX,dirZ){
    var g=new THREE.Group(); G_SHIELD.add(g);
    var len=0, px=sx, pz=sz;
    /* walk out until the water is properly under it */
    for(var st=0;st<14;st++){
      px+=dirX*1.6; pz+=dirZ*1.6; len+=1.6;
      if(shLakeD(px,pz)<0.90) break;
    }
    var n2=Math.max(3,Math.round(len/1.6));
    for(var q=0;q<n2;q++){
      var qx=sx+dirX*1.6*q, qz=sz+dirZ*1.6*q;
      put(g,1.9,0.14,1.7, dockM, qx, SH_WATER+0.62, qz, false);
      put(g,0.15,1.5,0.15, poleM, qx-0.75, SH_WATER-0.10, qz);
      put(g,0.15,1.5,0.15, poleM, qx+0.75, SH_WATER-0.10, qz);
    }
    /* a canoe, upside down, because that is how they live */
    var cn=new THREE.Mesh(new THREE.CylinderGeometry(0.42,0.42,4.6,6),canoeM);
    cn.rotation.z=Math.PI/2; cn.rotation.y=Math.atan2(dirX,dirZ);
    cn.scale.set(1,1,0.42);
    cn.position.set(sx+dirX*3.0, SH_WATER+0.86, sz+dirZ*3.0);
    cn.castShadow=true; g.add(cn);
    return g;
  }

  /* Put the camps where camps go: on a shore, off the road, facing the water.
     Walk out from each lake centre until the shoreline, then step back. */
  var CAMPS=[[0,0.9],[0,2.4],[1,0.4],[1,3.5],[2,1.9],[3,2.8],[4,5.4],[4,1.2]];
  for(var ci=0;ci<CAMPS.length;ci++){
    var LK=SH_LAKES[CAMPS[ci][0]], th=CAMPS[ci][1];
    var ux=Math.cos(th), uz=Math.sin(th);
    var cs2=Math.cos(LK[4]), sn2=Math.sin(LK[4]);
    var fx=0,fz=0,found=false;
    for(var rr=0.95;rr<1.60;rr+=0.02){
      var lx=ux*LK[2]*rr, lz=uz*LK[3]*rr;
      var wx=LK[0]+lx*cs2-lz*sn2, wz=LK[1]+lx*sn2+lz*cs2;
      if(shLakeD(wx,wz)>1.06){ fx=wx; fz=wz; found=true; break; }
    }
    if(!found) continue;
    var inX=(LK[0]-fx), inZ=(LK[1]-fz), il=Math.hypot(inX,inZ)||1;
    inX/=il; inZ/=il;
    camp(fx+inX*-7, fz+inZ*-7, Math.atan2(-inX,-inZ));
    dock(fx+inX*1.5, fz+inZ*1.5, inX, inZ);
  }

  /* ---- the general store, at the road junction, with a painted sign ---- */
  (function(){
    var sx=-34, sz=108;
    for(var t2=0;t2<40 && shRoadD(sx,sz)<14;t2++) sx+=2;
    var gy=height(sx,sz);
    var g=new THREE.Group(); g.position.set(sx,gy,sz); G_SHIELD.add(g);
    put(g,11.0,4.0,7.0, woodM, 0,2.00,0);
    put(g,11.6,0.30,7.6, tinM, 0,4.15,0, false);
    put(g,11.2,1.7,0.30, rustM, 0,5.05,-0.2, false);      /* false front */
    put(g,1.4,1.9,0.16, winM, -3.0,2.10, 3.55, false);
    put(g,1.4,1.9,0.16, winM,  3.0,2.10, 3.55, false);
    put(g,1.3,2.4,0.18, woodM, 0,1.30, 3.58, false);
    put(g,12.0,0.20,2.6, tinM, 0,3.30, 4.40, false);      /* the awning */
    put(g,0.16,3.2,0.16, poleM, -5.2,1.65, 5.60);
    put(g,0.16,3.2,0.16, poleM,  5.2,1.65, 5.60);
    /* two pumps under it, because the store is also the gas */
    put(g,0.7,1.5,0.5, rustM, -2.0,0.75, 5.10);
    put(g,0.7,1.5,0.5, rustM,  0.2,0.75, 5.10);
    /* the sign on its own posts by the road */
    put(g,3.4,1.5,0.18, tinM, 0,3.30, 9.0, false);
    put(g,0.16,3.4,0.16, poleM, -1.5,1.70, 9.0);
    put(g,0.16,3.4,0.16, poleM,  1.5,1.70, 9.0);
    BLD.push({x:sx,z:sz,w:11.6,d:7.6,y:gy-1,h:5.2});
  })();

  /* ---- a pickup that has not moved in some years ---- */
  (function(){
    var px=-58, pz=64;
    var gy=height(px,pz);
    var g=new THREE.Group(); g.position.set(px,gy,pz); g.rotation.y=0.8; G_SHIELD.add(g);
    put(g,1.9,0.9,4.4, rustM, 0,0.85,0);
    put(g,1.7,0.8,1.5, rustM, 0,1.60,0.7);
    put(g,1.5,0.5,0.10, m(0x3a4a52), 0,1.72,1.45, false);
    for(var bk=0;bk<4;bk++)
      put(g,0.7,0.45,0.7, graniteM, (bk%2?1:-1)*0.8,0.22,(bk<2?1.4:-1.4), false);
    BLD.push({x:px,z:pz,w:2.6,d:4.8,y:gy-1,h:2.2});
  })();

  /* ---- the fire tower, on the highest dome I can find ---- */
  (function(){
    var bx=0,bz=0,bd=-1;
    for(var t3=0;t3<900;t3++){
      var tx=(hash2(t3*4.3,2.9)-0.5)*2*170, tz=(hash2(t3*6.1,8.3)-0.5)*2*170;
      var dd=shDome(tx,tz);
      if(dd>bd && shLakeD(tx,tz)>1.3){ bd=dd; bx=tx; bz=tz; }
    }
    var gy=height(bx,bz);
    var g=new THREE.Group(); g.position.set(bx,gy,bz); G_SHIELD.add(g);
    var H=17;
    [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(c3){
      var lg=put(g,0.22,H,0.22, steelM, c3[0]*1.5, H/2, c3[1]*1.5);
      lg.rotation.z=-c3[0]*0.085; lg.rotation.x=c3[1]*0.085;
    });
    for(var br=1;br<6;br++){
      var yy=br*H/6, ww=3.4*(1-yy/H*0.42);
      put(g,ww,0.12,0.12, steelM, 0,yy,-ww/2, false);
      put(g,ww,0.12,0.12, steelM, 0,yy, ww/2, false);
      put(g,0.12,0.12,ww, steelM, -ww/2,yy,0, false);
      put(g,0.12,0.12,ww, steelM,  ww/2,yy,0, false);
    }
    put(g,3.2,0.16,3.2, steelM, 0,H,0);
    put(g,2.6,1.7,2.6, woodM, 0,H+0.95,0);
    put(g,2.4,0.7,0.12, winM, 0,H+1.25,1.32, false);
    put(g,3.0,0.20,3.0, tinM, 0,H+1.95,0, false);
    BLD.push({x:bx,z:bz,w:3.6,d:3.6,y:gy-1,h:H});
  })();

  /* ---- hydro poles down the haul road, with the wire slung between ---- */
  (function(){
    var prev=null;
    for(var pz2=-190; pz2<=190; pz2+=26){
      var px2=Math.sin(pz2*0.0125)*86 + Math.sin(pz2*0.0041+1.2)*54 - 34;
      px2 += 11;                                        /* off the shoulder */
      if(Math.hypot(px2,pz2)>200 || shLakeD(px2,pz2)<1.1){ prev=null; continue; }
      var gy=height(px2,pz2);
      var g=new THREE.Group(); g.position.set(px2,gy,pz2); G_SHIELD.add(g);
      put(g,0.24,9.4,0.24, poleM, 0,4.70,0);
      put(g,2.2,0.14,0.14, poleM, 0,9.00,0, false);
      var top={x:px2,y:gy+9.0,z:pz2};
      if(prev){
        /* one straight span with a sag in the middle reads as a catenary and
           costs two boxes instead of a curve */
        var mx2=(prev.x+top.x)/2, mz2=(prev.z+top.z)/2;
        var span=Math.hypot(top.x-prev.x, top.z-prev.z);
        var sag=(prev.y+top.y)/2 - 1.1;
        [[prev,{x:mx2,y:sag,z:mz2}],[{x:mx2,y:sag,z:mz2},top]].forEach(function(seg){
          var a2=seg[0], b3=seg[1];
          var len2=Math.hypot(b3.x-a2.x, b3.y-a2.y, b3.z-a2.z);
          var w2=new THREE.Mesh(new THREE.BoxGeometry(0.07,0.07,len2),wireM);
          w2.position.set((a2.x+b3.x)/2,(a2.y+b3.y)/2,(a2.z+b3.z)/2);
          w2.lookAt(b3.x,b3.y,b3.z);
          G_SHIELD.add(w2);
        });
      }
      prev=top;
    }
  })();

  bldGridBuild();
}
"""

sub("/* ================= the city, built =================", CODE +
    "\n/* ================= the city, built =================")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
