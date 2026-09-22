# -*- coding: utf-8 -*-
"""A proper boxy 4x4, and genuinely chunky tyres.

The lofted hull read as a generic buggy wedge. A Land Rover Defender is a
better answer for this style than anything sculpted, because the real vehicle
is already a set of flat panels meeting at hard right angles. Upright grille,
flat bonnet, vertical windscreen, squared cabin, white roof, roof rack, snorkel
up the pillar, spare on the back door.

Tyres go from 0.46 to 0.55 radius and get a real lug band, built as a second
nine sided ring of slightly larger radius so the silhouette is visibly knobbly
rather than a smooth cylinder. That is the cheapest way to make a wheel read as
an off road tyre at any distance.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

# chunkier rubber
s = s.replace("var WHEEL_R=0.46;", "var WHEEL_R=0.55;", 1); n += 1

start = "/* ================= the truck ================= */"
end = "/* Headlights."
a = s.index(start); b = s.index(end)

new_truck = '''/* ================= the truck ================= */
var truck=new THREE.Group(); scene.add(truck);
var corners=[], STRUT=[], GLOW=[], RIMMED=[];

(function(){
  function mat(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var kk in extra) o[kk]=extra[kk];
    return new THREE.MeshPhongMaterial(o);
  }
  /* A warm edge on the sun facing side lifts the truck off the sand without
     an outline, which would fight the facets. */
  function rimify(mm,power,amount){
    mm.onBeforeCompile=function(sh){
      sh.uniforms.uSunV={value:new THREE.Vector3()};
      sh.uniforms.uRimC={value:sc(0xffd9a0)};
      sh.uniforms.uRimP={value:power}; sh.uniforms.uRimA={value:amount};
      mm.userData.shader=sh;
      sh.fragmentShader=sh.fragmentShader
        .replace('#include <common>',
          '#include <common>\\nuniform vec3 uSunV,uRimC;\\nuniform float uRimP,uRimA;')
        .replace('vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;',
          [ 'vec3 Vv = normalize( vViewPosition );',
            'float rim = pow( 1.0 - clamp( dot( normal, Vv ), 0.0, 1.0 ), uRimP );',
            'rim *= smoothstep( -0.25, 0.55, dot( normal, uSunV ) );',
            'vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance + uRimC * rim * uRimA;'
          ].join('\\n'));
    };
    RIMMED.push(mm); return mm;
  }

  var paint  = rimify(mat(PAL.body),3.0,0.55);          /* body */
  var roofM  = rimify(mat(0xf0ece0),3.2,0.34);          /* the white roof */
  var trim   = mat(0x24313a);                           /* black trim and arches */
  var tyreM  = mat(0x231f28);
  var lugM   = mat(0x1a171f);
  var rimM   = mat(0xd6cbba);
  var chrome = mat(0x9aa0a8);
  var spring = mat(0xe8862c);                           /* the one hot accent */
  var glass  = mat(0x2c3f52,{transparent:true,opacity:0.62});
  var canvasM= mat(0xc9b489);                           /* roof rack load */
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
  function box(w,h,d,m,x,y,z,cast){
    return add(new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m),x,y,z,cast);
  }
  function cyl(r,h,seg,m,x,y,z,rx,rz){
    var c=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,seg),m);
    if(rx) c.rotation.x=rx; if(rz) c.rotation.z=rz;
    return add(c,x,y,z);
  }

  var W=1.78;                       /* body width */

  /* ---- chassis and lower body ---- */
  box(W,0.30,4.30, paint, 0,-0.16, 0.00);          /* sill band */
  box(1.30,0.14,0.60, trim, 0,-0.30, 2.02);        /* sump guard */
  box(0.16,0.16,2.30, trim,-0.94,-0.26,-0.10);     /* rock sliders */
  box(0.16,0.16,2.30, trim, 0.94,-0.26,-0.10);

  /* ---- bonnet, grille, front ---- */
  box(W,0.46,1.44, paint, 0, 0.22, 1.42);          /* flat bonnet */
  box(W,0.06,1.32, paint, 0, 0.46, 1.40, false);   /* bonnet lip */
  box(W,0.60,0.14, trim,  0, 0.22, 2.15);          /* upright grille panel */
  for(var gi=0;gi<5;gi++) box(0.05,0.44,0.05, chrome, -0.44+gi*0.22,0.22,2.22,false);
  box(1.94,0.22,0.34, trim, 0,-0.10, 2.20);        /* bull bar */
  box(0.10,0.60,0.10, trim,-0.90, 0.12, 2.20,false);
  box(0.10,0.60,0.10, trim, 0.90, 0.12, 2.20,false);
  /* round headlights, the Defender face */
  cyl(0.19,0.10,12, lampM, -0.60,0.26,2.24, Math.PI/2);
  cyl(0.19,0.10,12, lampM,  0.60,0.26,2.24, Math.PI/2);
  cyl(0.10,0.10,8, lampM, -0.86,0.06,2.24, Math.PI/2);
  cyl(0.10,0.10,8, lampM,  0.86,0.06,2.24, Math.PI/2);

  /* ---- cabin ---- */
  box(W,0.92,1.62, paint, 0, 0.91,-0.02);
  box(1.62,0.70,0.08, glass, 0, 1.00, 0.80, false);   /* vertical windscreen */
  box(0.08,0.52,1.20, glass,-0.90, 1.02,-0.06, false);
  box(0.08,0.52,1.20, glass, 0.90, 1.02,-0.06, false);
  box(1.84,0.12,1.74, roofM, 0, 1.43,-0.04);          /* white roof */
  box(0.10,0.34,0.10, trim, 0.92, 1.24, 0.72,false);  /* snorkel up the pillar */
  box(0.14,1.30,0.14, trim, 0.96, 0.80, 0.86);
  box(0.20,0.20,0.20, trim, 0.96, 1.48, 0.86,false);

  /* ---- rear body and door ---- */
  box(W,0.86,1.30, paint, 0, 0.88,-1.58);
  box(1.60,0.46,0.08, glass, 0, 1.06,-2.22, false);
  box(0.30,0.16,0.06, tailM,-0.66, 0.52,-2.24, false);
  box(0.30,0.16,0.06, tailM, 0.66, 0.52,-2.24, false);
  box(1.90,0.20,0.30, trim, 0,-0.08,-2.24);           /* rear bar */

  /* ---- roof rack, and the stuff on it ---- */
  box(1.86,0.07,1.80, trim, 0, 1.54,-0.90, false);
  [[-0.86,-0.02],[0.86,-0.02],[-0.86,-1.76],[0.86,-1.76]].forEach(function(pp){
    box(0.07,0.22,0.07, trim, pp[0],1.60,pp[1], false);
  });
  box(1.70,0.10,1.66, trim, 0, 1.70,-0.90);
  box(0.90,0.26,0.60, canvasM, -0.30,1.88,-1.20);
  box(0.34,0.44,0.26, trim, 0.56,1.97,-1.34);
  box(1.10,0.13,0.17, trim, 0, 1.82, 0.02, false);    /* roof light bar */
  for(var li=0;li<4;li++)
    cyl(0.085,0.07,10, lampM, -0.39+li*0.26,1.82,0.10, Math.PI/2);

  /* ---- spare on the back door ---- */
  var spare=new THREE.Mesh(new THREE.CylinderGeometry(0.50,0.50,0.32,14),tyreM);
  spare.rotation.x=Math.PI/2; add(spare,0.16,0.72,-2.36);
  var spareR=new THREE.Mesh(new THREE.CylinderGeometry(0.24,0.24,0.34,9),rimM);
  spareR.rotation.x=Math.PI/2; add(spareR,0.16,0.72,-2.36,false);

  /* ---- wheel arches, flared and black ---- */
  [[-1,1.55],[1,1.55],[-1,-1.55],[1,-1.55]].forEach(function(f){
    var ar=box(0.30,0.22,1.62, trim, f[0]*(W/2+0.06),-0.02,f[1]);
    ar.rotation.z=(f[0]<0?1:-1)*0.30;
  });

  /* ---- struts and wheels ---- */
  function helix(radius,turns,len,tubeR){
    var pts=[], N=turns*8;
    for(var i=0;i<=N;i++){
      var t=i/N, ang=t*turns*Math.PI*2;
      pts.push(new THREE.Vector3(Math.cos(ang)*radius,-t*len,Math.sin(ang)*radius));
    }
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),N,tubeR,5,false);
  }
  var springGeo=helix(0.130,7,1.0,0.032);

  /* A fourteen sided carcass plus a nine sided lug band of slightly larger
     radius. The lugs break the silhouette so it reads as an off road tyre
     rather than a smooth cylinder, for one extra mesh per corner. */
  var tyreGeo=new THREE.CylinderGeometry(WHEEL_R,WHEEL_R,0.46,14);
  tyreGeo.rotateZ(Math.PI/2);
  var lugGeo=new THREE.CylinderGeometry(WHEEL_R*1.075,WHEEL_R*1.075,0.34,9);
  lugGeo.rotateZ(Math.PI/2);
  var lug2Geo=new THREE.CylinderGeometry(WHEEL_R*1.055,WHEEL_R*1.055,0.20,9);
  lug2Geo.rotateZ(Math.PI/2); lug2Geo.rotateX(Math.PI/9);
  var rimGeo=new THREE.CylinderGeometry(WHEEL_R*0.52,WHEEL_R*0.52,0.48,8);
  rimGeo.rotateZ(Math.PI/2);
  var hubGeo=new THREE.CylinderGeometry(WHEEL_R*0.16,WHEEL_R*0.16,0.52,6);
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

    var shock=new THREE.Mesh(new THREE.CylinderGeometry(0.050,0.050,1.0,7),chrome);
    shock.position.y=-0.5; grp.add(shock);
    var spr=new THREE.Mesh(springGeo,spring); grp.add(spr);

    var arm=new THREE.Mesh(new THREE.BoxGeometry(0.70,0.11,0.20),trim);
    arm.castShadow=true; grp.add(arm);

    var hubg=new THREE.Group(); grp.add(hubg);
    var wheel=new THREE.Mesh(tyreGeo,tyreM); wheel.castShadow=true; hubg.add(wheel);
    hubg.add(new THREE.Mesh(lugGeo,lugM));
    hubg.add(new THREE.Mesh(lug2Geo,lugM));
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

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
print('hull() still referenced:', 'hull(' in s)
