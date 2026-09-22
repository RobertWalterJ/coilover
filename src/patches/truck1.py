# -*- coding: utf-8 -*-
"""Rebuild the truck.

It was a stack of boxes and read as a teal slab with a hole under it. The body
is now a lofted hull: five cross sections down the length, each a hexagonal
profile, stitched into about sixty triangles. That gives it a nose, a waist and
a tail, and every edge is a real crease.

Two rules from the art direction. The truck must have FEWER and LARGER facets
than the terrain, or it stops reading as a designed object sitting in a
landscape and becomes another lump of the same material. And its value has to
be dark against bright sand, which is what makes it pop, with the hue as the
secondary pleasure.

Wheels go to fourteen sides. Below twelve they visibly wobble when they spin,
above eighteen they read as smooth cylinders and stop matching the ground.

Lamps, tail lights and the light bar are wired to the time of day, so they come
up as the light goes.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

start = "/* ================= the truck ================= */"
end = "/* Headlights."
a = s.index(start); b = s.index(end)

new_truck = '''/* ================= the truck ================= */
var truck=new THREE.Group(); scene.add(truck);
var corners=[], STRUT=[], GLOW=[];

/* Loft a hull through a set of cross sections. Each section is a hexagon, so
   the body gets a chamfer along the top and bottom edges rather than reading
   as a box. Winding is checked against the centroid and flipped if needed. */
function hull(sections){
  function prof(sec){
    var mid=(sec.yb+sec.yt)*0.5, w=sec.hw*0.78;
    return [[-sec.hw,mid],[-w,sec.yt],[w,sec.yt],[sec.hw,mid],[w,sec.yb],[-w,sec.yb]];
  }
  var v=[];
  function tri(p1,p2,p3){ v.push(p1[0],p1[1],p1[2],p2[0],p2[1],p2[2],p3[0],p3[1],p3[2]); }
  var i,j,k;
  for(i=0;i<sections.length-1;i++){
    var A=prof(sections[i]), B=prof(sections[i+1]);
    var za=sections[i].z, zb=sections[i+1].z;
    for(j=0;j<6;j++){
      k=(j+1)%6;
      tri([A[j][0],A[j][1],za],[A[k][0],A[k][1],za],[B[k][0],B[k][1],zb]);
      tri([A[j][0],A[j][1],za],[B[k][0],B[k][1],zb],[B[j][0],B[j][1],zb]);
    }
  }
  var F=prof(sections[0]), zf=sections[0].z;
  for(j=1;j<5;j++) tri([F[0][0],F[0][1],zf],[F[j+1][0],F[j+1][1],zf],[F[j][0],F[j][1],zf]);
  var L=prof(sections[sections.length-1]), zl=sections[sections.length-1].z;
  for(j=1;j<5;j++) tri([L[0][0],L[0][1],zl],[L[j][0],L[j][1],zl],[L[j+1][0],L[j+1][1],zl]);

  /* does triangle one face outward? if not, reverse every triangle */
  var cx=0,cy=0,cz=0, N=v.length/3;
  for(i=0;i<N;i++){ cx+=v[i*3]; cy+=v[i*3+1]; cz+=v[i*3+2]; }
  cx/=N; cy/=N; cz/=N;
  var e1=[v[3]-v[0],v[4]-v[1],v[5]-v[2]], e2=[v[6]-v[0],v[7]-v[1],v[8]-v[2]];
  var nx=e1[1]*e2[2]-e1[2]*e2[1], ny=e1[2]*e2[0]-e1[0]*e2[2], nz=e1[0]*e2[1]-e1[1]*e2[0];
  var fx=(v[0]+v[3]+v[6])/3-cx, fy=(v[1]+v[4]+v[7])/3-cy, fz=(v[2]+v[5]+v[8])/3-cz;
  if(nx*fx+ny*fy+nz*fz < 0){
    for(i=0;i<v.length;i+=9){
      var t0=v[i+3],t1=v[i+4],t2=v[i+5];
      v[i+3]=v[i+6]; v[i+4]=v[i+7]; v[i+5]=v[i+8];
      v[i+6]=t0; v[i+7]=t1; v[i+8]=t2;
    }
  }
  var g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(v,3));
  g.computeVertexNormals();
  return g;
}

(function(){
  function mat(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var kk in extra) o[kk]=extra[kk];
    return new THREE.MeshPhongMaterial(o);
  }
  var paint =mat(PAL.body);
  var paint2=mat(0x14606b);                 /* a darker teal for the lower body */
  var bone  =mat(PAL.bone);
  var dark  =mat(0x2a2530);
  var tyre  =mat(PAL.tyre);
  var rimM  =mat(PAL.wheel);
  var chrome=mat(0x9aa0a8);
  var spring=mat(0xe8862c);                 /* the one hot accent on the truck */
  var glass =mat(0x33475c,{transparent:true,opacity:0.55});

  function glowMat(col,em){
    var m=mat(col); m.emissive=new THREE.Color(0x000000);
    GLOW.push({m:m,c:new THREE.Color(em)}); return m;
  }
  var lampM=glowMat(0xfff3d0,0xfff0c0);
  var tailM=glowMat(0x8c2a22,0xff4530);

  function add(mesh,x,y,z,cast){
    mesh.position.set(x,y,z);
    if(cast!==false) mesh.castShadow=true;
    truck.add(mesh); return mesh;
  }
  function box(w,h,d,m,x,y,z,cast){ return add(new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m),x,y,z,cast); }

  /* ---- body ---- */
  add(new THREE.Mesh(hull([
    {z: 2.32, hw:0.60, yb:-0.16, yt: 0.06},   /* nose tip */
    {z: 1.48, hw:0.84, yb:-0.24, yt: 0.30},   /* over the front axle */
    {z: 0.30, hw:0.86, yb:-0.26, yt: 0.44},   /* cowl, the tallest point */
    {z:-1.05, hw:0.86, yb:-0.24, yt: 0.34},   /* over the rear axle */
    {z:-2.08, hw:0.70, yb:-0.14, yt: 0.22}    /* tail */
  ]),paint),0,0.14,0);

  /* a darker sill along the bottom edge, so the silhouette has a base */
  box(1.66,0.16,3.9,paint2, 0,-0.12,0.05);
  box(1.50,0.10,0.62,dark,  0,-0.20,2.16);         /* bash plate */

  /* flared fenders. This is what makes it read as an off roader. */
  [[-0.98,1.48],[0.98,1.48],[-0.98,-1.62],[0.98,-1.62]].forEach(function(f){
    var fen=box(0.34,0.20,1.34,paint, f[0],0.16,f[1]);
    fen.rotation.z=(f[0]<0?1:-1)*0.22;
  });

  /* ---- cage and cab ---- */
  var tube=new THREE.CylinderGeometry(0.055,0.055,1.16,6);
  [[-0.74,0.62],[0.74,0.62],[-0.74,-0.86],[0.74,-0.86]].forEach(function(pp){
    add(new THREE.Mesh(tube,bone),pp[0],1.02,pp[1]);
  });
  /* diagonal braces down to the tail, the classic Baja silhouette */
  [[-0.74],[0.74]].forEach(function(pp){
    var br=new THREE.Mesh(new THREE.CylinderGeometry(0.05,0.05,1.55,6),bone);
    br.position.set(pp[0],0.96,-1.52); br.rotation.x=0.72;
    br.castShadow=true; truck.add(br);
  });
  box(1.62,0.08,1.62,bone, 0,1.62, -0.12);          /* roof panel */
  box(1.44,0.42,0.06,glass,0,0.96,  0.66, false);   /* windscreen */
  box(0.66,0.34,0.60,dark,-0.34,0.52,-0.20);        /* seat */

  /* ---- lights ---- */
  box(1.22,0.12,0.14,dark, 0,1.76,-0.04);           /* light bar spine */
  for(var li=0;li<4;li++){
    var lamp=new THREE.Mesh(new THREE.CylinderGeometry(0.085,0.085,0.07,10),lampM);
    lamp.rotation.x=Math.PI/2;
    add(lamp,-0.42+li*0.28,1.76,0.04,false);
  }
  [[-0.44],[0.44]].forEach(function(pp){            /* headlights in the nose */
    var hl=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.13,0.08,10),lampM);
    hl.rotation.x=Math.PI/2; add(hl,pp[0],0.10,2.16,false);
  });
  [[-0.52],[0.52]].forEach(function(pp){
    box(0.22,0.12,0.06,tailM, pp[0],0.22,-2.12,false);
  });

  /* ---- rear deck: spare, jerry can, exhaust ---- */
  var spare=new THREE.Mesh(new THREE.CylinderGeometry(0.40,0.40,0.28,14),tyre);
  spare.rotation.x=Math.PI/2; add(spare,0,0.52,-1.62);
  box(0.34,0.42,0.24,dark, 0.58,0.54,-1.30);
  var pipe=new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.1,8),chrome);
  pipe.rotation.z=Math.PI/2; add(pipe,0.86,-0.06,-0.85);

  /* ---- struts ---- */
  /* A helix scaled along its axis compresses its own pitch, which is what a
     real spring does, so one Y scale per frame is an honest looking spring.
     Kept deliberately low segment so it stays chunky. */
  function helix(radius,turns,len,tubeR){
    var pts=[], N=turns*8;
    for(var i=0;i<=N;i++){
      var t=i/N, ang=t*turns*Math.PI*2;
      pts.push(new THREE.Vector3(Math.cos(ang)*radius,-t*len,Math.sin(ang)*radius));
    }
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),N,tubeR,5,false);
  }
  var springGeo=helix(0.125,7,1.0,0.030);
  var wheelGeo=new THREE.CylinderGeometry(WHEEL_R,WHEEL_R,0.40,14);
  wheelGeo.rotateZ(Math.PI/2);
  var rimGeo=new THREE.CylinderGeometry(WHEEL_R*0.48,WHEEL_R*0.48,0.42,8);
  rimGeo.rotateZ(Math.PI/2);
  var hubGeo=new THREE.CylinderGeometry(WHEEL_R*0.17,WHEEL_R*0.17,0.46,6);
  hubGeo.rotateZ(Math.PI/2);

  var MOUNT=[
    [-TRACK/2, -0.06,  WHEELBASE/2],
    [ TRACK/2, -0.06,  WHEELBASE/2],
    [-TRACK/2, -0.06, -WHEELBASE/2],
    [ TRACK/2, -0.06, -WHEELBASE/2]
  ];
  for(var i=0;i<4;i++){
    var m=MOUNT[i];
    var grp=new THREE.Group(); grp.position.set(m[0],m[1],m[2]); truck.add(grp);

    var shock=new THREE.Mesh(new THREE.CylinderGeometry(0.048,0.048,1.0,7),chrome);
    shock.position.y=-0.5; grp.add(shock);
    var spr=new THREE.Mesh(springGeo,spring); grp.add(spr);

    var arm=new THREE.Mesh(new THREE.BoxGeometry(0.66,0.10,0.18),dark);
    arm.castShadow=true; grp.add(arm);

    var hubg=new THREE.Group(); grp.add(hubg);
    var wheel=new THREE.Mesh(wheelGeo,tyre); wheel.castShadow=true; hubg.add(wheel);
    var rim=new THREE.Mesh(rimGeo,rimM); hubg.add(rim);
    hubg.add(new THREE.Mesh(hubGeo,chrome));

    STRUT.push({grp:grp,shock:shock,spring:spr,arm:arm,hub:hubg,wheel:wheel,rim:rim});
    corners.push({
      mount:new THREE.Vector3(m[0],m[1],m[2]),
      front:(i<2), left:(i%2===0),
      len:SUS_REST, prevLen:SUS_REST, load:0, contact:false, spin:0, slip:0,
      alphaF:0, locked:false,
      cp:new THREE.Vector3(), nrm:new THREE.Vector3(0,1,0)
    });
  }
})();

'''

s = s[:a] + new_truck + s[b:]
n += 1

# drive the lamps from the time of day
old = """  /* headlights sit on the nose and look where the truck is pointed */"""
assert old in s
s = s.replace(old, """  /* lamps and tail lights come up as the light goes */
  for(var gi2=0;gi2<GLOW.length;gi2++){
    GLOW[gi2].m.emissive.copy(GLOW[gi2].c).multiplyScalar(TOD.glow*0.9);
  }

  /* headlights sit on the nose and look where the truck is pointed */""", 1)
n += 1

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
print('BODY_COL still referenced:', 'BODY_COL' in s)
