# -*- coding: utf-8 -*-
"""Place the buildings along the block edges, and let the truck hit them."""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------- fill BLD and build the mesh
sub("""(function(){
  function m(col,tex){
    return styleMat(new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true}),{tex:tex||'rock'});
  }
  var capM=m(0x4f4a52,'metal'), poleM=m(0x565059,'metal');""",
"""(function(){
  function m(col,tex){
    return styleMat(new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true}),{tex:tex||'rock'});
  }
  var capM=m(0x4f4a52,'metal'), poleM=m(0x565059,'metal');

  /* ---- place the buildings ----
     Walk every block, then every one of its four street frontages, and lay
     parcels along it built to the building line. Neighbours share their edge,
     so the wall is continuous; corner parcels get an extra storey. */
  var WALLC=[0xb4a894,0xa08e84,0xc0ab92,0x8e8e9a,0xb08a72,0x9aa0a4,0xc4b8a2,0x86807e];
  var CAPC =[0x5b5660,0x6a6058,0x4e4a52,0x746a5e];
  var DEPTH=16;
  for(var bi=-3;bi<=3;bi++) for(var bj=-4;bj<=4;bj++){
    var bx=bi*PX, bz=bj*PZ;                       /* block centre */
    if(Math.hypot(bx,bz)>RIM-24) continue;
    if(panMask(bx,bz)>0.30) continue;
    var innerX=PX-2*BUILD, innerZ=PZ-2*BUILD;     /* the block, inside the ROW */
    var core=1-sstep(40,210,Math.hypot(bx-30,bz+34));
    /* four frontages: +z, -z, +x, -x */
    for(var e=0;e<4;e++){
      var along=(e<2)?innerX:innerZ;
      var wBar=(core>0.45)?18:9.5;
      var W=parcelWidths(along,wBar,bi*17.3+bj*5.1+e*2.7);
      var run=-along*0.5;
      for(var q=0;q<W.length;q++){
        var w=W[q], cAlong=run+w*0.5; run+=w;
        var isCorner=(q===0||q===W.length-1);
        var hs=hash2(bi*7.1+q*2.3+e*11.7, bj*3.9-q*1.7);
        var hh=6+hs*9 + core*core*(12+hs*46) + (isCorner?3.2:0);
        var px2,pz2,ww,dd;
        if(e===0){ px2=bx+cAlong; pz2=bz+innerZ*0.5-DEPTH*0.5; ww=w; dd=DEPTH; }
        else if(e===1){ px2=bx+cAlong; pz2=bz-innerZ*0.5+DEPTH*0.5; ww=w; dd=DEPTH; }
        else if(e===2){ px2=bx+innerX*0.5-DEPTH*0.5; pz2=bz+cAlong; ww=DEPTH; dd=w; }
        else{ px2=bx-innerX*0.5+DEPTH*0.5; pz2=bz+cAlong; ww=DEPTH; dd=w; }
        if(Math.hypot(px2,pz2)>RIM-18) continue;
        if(panMask(px2,pz2)>0.25) continue;
        /* a gap now and then: a laneway mouth, a lot, a parkette */
        if(!isCorner && hash2(px2*0.31,pz2*0.27)>0.90) continue;
        BLD.push({x:px2, z:pz2, w:ww*0.97, d:dd*0.97, h:hh,
                  y:height(px2,pz2)+KERB,
                  par:isCorner?1.5:0.9,
                  col:WALLC[Math.floor(hs*WALLC.length)%WALLC.length],
                  cap:CAPC[Math.floor(hs*13)%CAPC.length]});
      }
    }
  }
  bldGridBuild();
  G_CITY.add(buildCityBuildings());""")

# ------------------------------------------------------------ the collision
sub("""  sync(dt);
  updateLightPool();""",
"""  sync(dt);
  updateLightPool();""")

# resolve against walls right after the integrator moves the body
sub("""  S.v.addScaledVector(Fsum,dt/MASS);""",
"""  S.v.addScaledVector(Fsum,dt/MASS);
  if(MAP===1) hitWalls(dt);""")

sub("""/* ================= physics ================= */""",
"""/* ---- walls ----
   The struts and the ground query are untouched. This acts on the body only,
   horizontally, through two circles on the centreline. */
var _wf=new THREE.Vector3(), _wp=new THREE.Vector3();
function hitWalls(dt){
  var R=0.98, halfL=1.15;
  _wf.set(0,0,1).applyQuaternion(S.q); _wf.y=0;
  if(_wf.lengthSq()<1e-6) return; _wf.normalize();
  for(var e=0;e<2;e++){
    var sgn=(e===0)?1:-1;
    var px=S.p.x+_wf.x*halfL*sgn, pz=S.p.z+_wf.z*halfL*sgn;
    var hit=wallNear(px,pz,S.p.y-0.4);
    if(!hit || hit.d>=R) continue;
    var nx=hit.nx, nz=hit.nz;                 /* flat by construction */
    var vn=S.v.x*nx + S.v.z*nz;
    if(vn>=0) continue;                       /* already separating, leave it */
    var sp=Math.min(Math.abs(vn)/18,1);
    var rest=0.34*(1-sp)+0.10*sp;             /* a wall at speed takes speed */
    var fric=0.06*(1-sp)+0.50*sp;             /* and scrapes harder the faster */
    var tvx=S.v.x-nx*vn, tvz=S.v.z-nz*vn;
    S.v.x=tvx*(1-fric) - nx*rest*vn;
    S.v.z=tvz*(1-fric) - nz*rest*vn;
    if(S.v.y>0) S.v.y=0;                      /* a wall never lifts the truck */
    var pen=Math.min(R-hit.d,1.6);
    S.p.x+=nx*pen*0.55; S.p.z+=nz*pen*0.55;
    /* a corner hit should turn you, not launch you */
    var rx=px-S.p.x, rz=pz-S.p.z;
    S.w.y += (rx*nz-rz*nx)*(-(1+rest)*vn)*0.055;
    S.w.y = Math.max(-4,Math.min(4,S.w.y));
    S.shake=Math.min(1.4,(S.shake||0)+Math.abs(vn)*0.045);
    if(Math.abs(vn)>4) buzz(Math.min(40,Math.abs(vn)*2));
  }
}

/* ================= physics ================= */""")

# expose for testing
sub("    panMask:panMask, streetD:streetD, parcelH:parcelH, roadH:roadH,",
    "    panMask:panMask, streetD:streetD, roadH:roadH,\n"
    "    BLD:BLD, wallNear:wallNear,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
