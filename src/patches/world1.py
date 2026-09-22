# -*- coding: utf-8 -*-
"""Landmarks and the progression spine.

The design rule underneath all of it: everything counts up, never down. A
stopwatch runs against you, an odometer runs for you. So there is an odometer
that never resets, a map that paints itself in as you drive, eight places worth
finding, and stones at each ramp that physically relocate to your longest clean
landing while you are still driving away from it. No results screen, no
grading, no percentage complete, and nothing that shows you what you are
missing.

The landmarks are also the nostalgia payload: a gas station, a motel sign, a
drive in screen, a water tower, a half buried aircraft, a camper, a windmill,
a ring of stones. Dead quiet in daylight, lit at dusk and night.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- fenders
sub("""    var fen=box(0.34,0.20,1.34,paint, f[0],0.16,f[1]);
    fen.rotation.z=(f[0]<0?1:-1)*0.22;""",
    """    var fen=box(0.46,0.18,1.46,paint, f[0]*1.04,-0.06,f[1]);
    fen.rotation.z=(f[0]<0?1:-1)*0.26;""")

# ---------------------------------------------------------------- world props
sub("""/* ================= the truck ================= */""",
"""/* ================= landmarks ================= */
/* Eight places worth driving to. Each one is tall or lit enough to read from
   a couple of hundred metres, because the whole discovery loop depends on you
   being able to see the next one from the last one. */
var LANDMARKS=[], LGLOW=[];
(function(){
  function m(col,extra){
    var o={color:sc(col),specular:0x000000,shininess:0,flatShading:true};
    if(extra) for(var k in extra) o[k]=extra[k];
    return new THREE.MeshPhongMaterial(o);
  }
  var post=m(0x6b5a52), panel=m(0xd8cec0), rust=m(0x8a4a34), metal=m(0x8d939a),
      dark=m(0x2f2a30), wood=m(0x7a5c40), white=m(0xe8e2d4);
  function lit(col,em,strength){
    var mm=m(col); mm.emissive=new THREE.Color(0x000000);
    LGLOW.push({m:mm,c:new THREE.Color(em),s:strength===undefined?1:strength});
    return mm;
  }

  function B(g,mat,x,y,z,parent){
    var mesh=new THREE.Mesh(g,mat); mesh.position.set(x,y,z);
    mesh.castShadow=true; mesh.receiveShadow=true; parent.add(mesh); return mesh;
  }
  function bx(w,h,d){ return new THREE.BoxGeometry(w,h,d); }
  function cy(r,h,seg){ return new THREE.CylinderGeometry(r,r,h,seg||8); }

  function place(name,x,z,build){
    var g=new THREE.Group();
    var y=height(x,z);
    g.position.set(x,y,z);
    g.rotation.y=hash2(x*0.11,z*0.13)*Math.PI*2;
    build(g);
    /* a pale marker that pulses above anything not yet reached */
    var orb=new THREE.Mesh(new THREE.SphereGeometry(0.9,10,7),
      new THREE.MeshBasicMaterial({color:0xfff0cf,transparent:true,opacity:0.5,
        depthWrite:false,fog:true}));
    orb.position.y=13; g.add(orb);
    /* and a flag that goes up once you have been */
    var flag=new THREE.Group(); flag.visible=false;
    B(cy(0.06,3.2,6),metal,0,1.6,0,flag);
    B(bx(1.1,0.62,0.05),lit(0xe0553f,0xe0553f,0.5),0.58,2.9,0,flag);
    flag.position.set(3.2,0,2.4); g.add(flag);
    scene.add(g);
    LANDMARKS.push({name:name,x:x,y:y,z:z,g:g,orb:orb,flag:flag,found:false});
  }

  /* a roadside gas station, canopy and two pumps */
  place('Gas station',-138,-58,function(g){
    B(bx(9,0.34,6.4),panel,0,4.3,0,g);
    [[-4,-2.7],[4,-2.7],[-4,2.7],[4,2.7]].forEach(function(pp){
      B(cy(0.17,4.3,7),metal,pp[0],2.15,pp[1],g);
    });
    B(bx(0.9,1.7,0.7),rust,-1.4,0.85,0,g);
    B(bx(0.9,1.7,0.7),rust, 1.4,0.85,0,g);
    B(bx(4.6,1.5,0.16),lit(0xf2e2c0,0xffd9a0),0,6.2,0,g);
    B(bx(5.0,0.2,0.3),metal,0,5.35,0,g);
    B(bx(6.5,2.6,4.2),panel,-8.5,1.3,0,g);
  });

  /* the motel sign, tall enough to see from anywhere */
  place('Motel sign',96,142,function(g){
    B(cy(0.22,13,7),rust,0,6.5,0,g);
    B(bx(4.6,6.2,0.3),lit(0xe8543a,0xff6a3a),0,10.6,0,g);
    B(bx(5.2,0.35,0.55),metal,0,13.9,0,g);
    B(bx(3.4,0.9,0.4),lit(0xf6e4bc,0xfff0c8),0,7.0,0,g);
  });

  /* a drive in screen facing the basin */
  place('Drive in',-92,158,function(g){
    B(bx(17,10.5,0.5),white,0,6.4,0,g);
    B(bx(17.8,0.6,1.0),dark,0,11.9,0,g);
    [-7.6,-2.5,2.5,7.6].forEach(function(x){ B(cy(0.2,7,6),rust,x,3.5,-1.1,g); });
    B(bx(3.6,1.0,0.3),lit(0xf2d9a8,0xffdca8),0,1.3,0.4,g);
  });

  /* water tower */
  place('Water tower',158,-92,function(g){
    B(cy(3.1,4.4,10),metal,0,11.4,0,g);
    B(new THREE.ConeGeometry(3.2,1.6,10),metal,0,14.4,0,g);
    [[-2,-2],[2,-2],[-2,2],[2,2]].forEach(function(pp){
      var leg=B(cy(0.16,9.6,6),rust,pp[0]*1.25,4.8,pp[1]*1.25,g);
      leg.rotation.x=-pp[1]*0.028; leg.rotation.z=pp[0]*0.028;
    });
    B(bx(4.4,1.0,0.12),lit(0xd8cec0,0xffc890,0.7),0,11.8,3.2,g);
  });

  /* a half buried aircraft, nose down in the sand */
  place('Old wreck',-58,-168,function(g){
    var fus=B(cy(1.5,11,9),panel,0,2.2,0,g);
    fus.rotation.x=Math.PI/2; fus.rotation.z=0.16; fus.rotation.y=0.3;
    var wing=B(bx(15,0.3,2.6),panel,0,2.4,1.2,g); wing.rotation.z=0.1;
    var tail=B(bx(0.3,3.4,2.2),rust,0,4.6,-4.4,g); tail.rotation.x=0.2;
  });

  /* an abandoned camper with one chair facing the view */
  place('The camp',176,86,function(g){
    B(bx(2.6,2.2,5.4),panel,0,1.6,0,g);
    B(bx(2.7,0.25,5.5),rust,0,2.8,0,g);
    B(bx(0.5,0.5,0.5),dark,0,0.3,3.1,g);
    B(bx(0.9,0.06,0.9),wood,3.4,0.5,1.2,g);
    B(bx(0.9,0.9,0.06),wood,3.4,0.95,0.78,g);
    B(bx(1.1,0.9,0.14),lit(0xf0dcb0,0xffd48a),1.36,1.7,1.0,g);
    B(cy(0.7,0.3,9),dark,3.0,0.15,-1.6,g);
  });

  /* a windmill, and the blades actually turn */
  place('Windmill',-172,52,function(g){
    [[-1.3,-1.3],[1.3,-1.3],[-1.3,1.3],[1.3,1.3]].forEach(function(pp){
      var leg=B(cy(0.12,10.5,5),metal,pp[0],5.2,pp[1],g);
      leg.rotation.x=-pp[1]*0.055; leg.rotation.z=pp[0]*0.055;
    });
    B(bx(2.4,0.3,2.4),metal,0,10.5,0,g);
    var rot=new THREE.Group(); rot.position.set(0,11.4,0.5); g.add(rot);
    for(var i=0;i<12;i++){
      var bl=B(bx(0.5,2.5,0.05),metal,0,1.5,0,rot);
      bl.position.set(Math.sin(i/12*6.283)*1.5,Math.cos(i/12*6.283)*1.5,0);
      bl.rotation.z=-i/12*6.283;
    }
    LANDMARKS.push({spin:rot});          /* handled below, has no trigger */
  });

  /* a ring of stones out on the flat */
  place('Stone ring',-40,120,function(g){
    for(var i=0;i<11;i++){
      var a=i/11*Math.PI*2, r=6;
      var st=B(new THREE.DodecahedronGeometry(0.8+hash2(i,3)*0.7,0),
               m(0x8a5a44),Math.sin(a)*r,0.3,Math.cos(a)*r,g);
      st.rotation.set(hash2(i,1)*3,hash2(i,2)*6,hash2(i,4)*3);
    }
    B(cy(0.5,2.6,7),m(0x8a5a44),0,1.3,0,g);
  });
})();
/* the windmill rotor got pushed on as a bare entry; pull it back out */
var WINDMILL=null;
for(var _li=LANDMARKS.length-1;_li>=0;_li--){
  if(LANDMARKS[_li].spin){ WINDMILL=LANDMARKS[_li].spin; LANDMARKS.splice(_li,1); }
}

/* ================= the truck ================= */""")

# ---------------------------------------------------------------- progression
sub("""/* ================= landmarks ================= */""",
"""/* ================= what carries over ================= */
var MAPN=96;
var PROG={ odo:0, air:0, found:{}, jump:[0,0,0], mapv:new Uint8Array(MAPN*MAPN) };
var SAVEKEY='coilover.v1';

function loadProg(){
  try{
    var raw=localStorage.getItem(SAVEKEY); if(!raw) return;
    var o=JSON.parse(raw);
    PROG.odo=o.odo||0; PROG.air=o.air||0; PROG.found=o.found||{};
    PROG.jump=o.jump||[0,0,0];
    if(o.map){
      var bin=atob(o.map);
      for(var i=0;i<PROG.mapv.length && i<bin.length;i++) PROG.mapv[i]=bin.charCodeAt(i);
    }
  }catch(e){}
}
var saveT=0;
function saveProg(){
  try{
    var str='';
    for(var i=0;i<PROG.mapv.length;i++) str+=String.fromCharCode(PROG.mapv[i]);
    localStorage.setItem(SAVEKEY,JSON.stringify({
      odo:PROG.odo, air:PROG.air, found:PROG.found, jump:PROG.jump, map:btoa(str)}));
  }catch(e){}
}
loadProg();

/* The map paints itself in from where the wheels have actually been. It shows
   what you have found and never what you have not. */
function markMap(x,z){
  var i=Math.floor((x+HALF)/WORLD*MAPN), j=Math.floor((z+HALF)/WORLD*MAPN);
  if(i<0||j<0||i>=MAPN||j>=MAPN) return;
  var k=j*MAPN+i;
  if(PROG.mapv[k]<255) PROG.mapv[k]=Math.min(255,PROG.mapv[k]+60);
}

/* ================= landmarks ================= */""")

# ---------------------------------------------------------------- marker stones
sub("""/* ================= dust ================= */""",
"""/* ================= ramp marker stones ================= */
/* Beat your longest clean landing at a ramp and the stones walk out to the new
   spot while you are still driving away from it. No number, no popup. */
var KICKERS=[{x:50,z:30},{x:-38,z:-120},{x:124,z:74}];
var STONES=[];
(function(){
  var sm=new THREE.MeshPhongMaterial({color:sc(0x8a5a44),specular:0x000000,
    shininess:0,flatShading:true});
  for(var i=0;i<3;i++){
    var g=new THREE.Group();
    for(var j=0;j<5;j++){
      var r=0.62-j*0.085;
      var st=new THREE.Mesh(new THREE.DodecahedronGeometry(r,0),sm);
      st.position.set((hash2(i,j)-0.5)*0.24, 0.30+j*0.42, (hash2(j,i)-0.5)*0.24);
      st.rotation.set(hash2(i,j+9)*3,hash2(j,i+4)*6,hash2(i+2,j)*3);
      st.castShadow=true; g.add(st);
    }
    g.visible=false; scene.add(g);
    STONES.push(g);
  }
})();
function setStone(i,x,z){
  STONES[i].position.set(x,height(x,z),z);
  STONES[i].visible=true;
}
for(var _si=0;_si<3;_si++){
  if(PROG.jump[_si]>0){
    var _kk=KICKERS[_si], _d=PROG.jump[_si];
    setStone(_si,_kk.x+Math.cos(_si*2.1)*_d,_kk.z+Math.sin(_si*2.1)*_d);
  }
}

/* ================= dust ================= */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
