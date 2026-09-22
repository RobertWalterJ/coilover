# -*- coding: utf-8 -*-
"""The city's own props, and the switch between maps.

Buildings stand on the block plateaus that are already in the heightfield, so
they never disagree with what the truck can drive on. Each block gets a
footprint stepped in from its kerb and a height drawn from a hash of its grid
cell, which means the skyline is stable: the same block is the same building
every time you come back to it, without storing anything.

Street lights sit on the kerbs at every intersection. They are registered the
same way the desert landmarks are, so the light pool that already follows you
picks them up with no extra wiring, and at dusk the grid becomes a field of
warm pools in a blue frame. That is the ember.lite subject arriving from a
place that genuinely has lights in it.

The desert props all move into one group and the city props into another, and
swapping a map shows one and hides the other while the terrain geometry is
rebuilt in place. Segment and feat records are namespaced by map so the desert
Rim run and a city record can never be confused with each other.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------- one group per map's props
sub("""/* ================= scatter: rocks and scrub ================= */""",
"""/* Every prop belongs to a map. Swapping shows one group and hides the other,
   which is instant, instead of disposing and rebuilding a world. */
var G_DESERT=new THREE.Group(); scene.add(G_DESERT);
var G_CITY=new THREE.Group(); G_CITY.visible=false; scene.add(G_CITY);

/* ================= scatter: rocks and scrub ================= */""")

# route the desert props into their group
sub("  scene.add(rocks); scene.add(bushes);", "  G_DESERT.add(rocks); G_DESERT.add(bushes);")
sub("""    scene.add(g);
    GATES.push({x:x,y:y,z:z,g:g,beam:beam,done:false});""",
    """    G_DESERT.add(g);
    GATES.push({x:x,y:y,z:z,g:g,beam:beam,done:false});""")
sub("""    scene.add(g);
    LANDMARKS.push({name:name,x:x,y:y,z:z,g:g,orb:orb,flag:flag,found:false});""",
    """    G_DESERT.add(g);
    LANDMARKS.push({name:name,x:x,y:y,z:z,g:g,orb:orb,flag:flag,found:false});""")
sub("""    var rail=new THREE.Mesh(new THREE.BoxGeometry(12.2,0.26,0.5),legM);
    rail.position.y=6.2; g.add(rail);
    scene.add(g);""",
"""    var rail=new THREE.Mesh(new THREE.BoxGeometry(12.2,0.26,0.5),legM);
    rail.position.y=6.2; g.add(rail);
    G_DESERT.add(g);""")
sub("""  scene.add(pk);""", """  G_DESERT.add(pk);""")

# ------------------------------------------------------------- the city props
sub("""/* ================= the truck ================= */""",
"""/* ================= the city, built ================= */
(function(){
  function m(col,tex){
    return styleMat(new THREE.MeshPhongMaterial({color:sc(col),specular:0x000000,
      shininess:0,flatShading:true}),{tex:tex||'rock'});
  }
  var wallA=m(0x8a7f74), wallB=m(0x6f6b74), wallC=m(0x9c8878), wallD=m(0x5c6470);
  var WALLS=[wallA,wallB,wallC,wallD];
  var roofM=m(0x4a4650,'metal');
  var poleM=m(0x565059,'metal');
  var kerbM=m(0x8e8a86,'rock');
  /* the lamp head is registered as lit, so the light pool finds it */
  function lampMat(){
    var mm=new THREE.MeshPhongMaterial({color:sc(0xfff0cc),specular:0x000000,
      shininess:0,flatShading:true});
    mm.emissive=new THREE.Color(0x000000);
    LGLOW.push({m:mm,c:new THREE.Color(0xffd89a),s:0.85});
    return mm;
  }
  var glassM=new THREE.MeshPhongMaterial({color:sc(0x2c3646),specular:0x000000,
    shininess:0,flatShading:true,transparent:true,opacity:0.66});

  var half=(CITY_PITCH-CITY_ST)*0.5;
  var lampsMade=0;

  for(var gz=-4;gz<=4;gz++) for(var gx=-4;gx<=4;gx++){
    var cx=gx*CITY_PITCH, cz=gz*CITY_PITCH;
    if(Math.hypot(cx,cz)>RIM-26) continue;
    if(panMask(cx,cz)>0.35) continue;              /* the pan stays empty */

    var top=height(cx,cz);
    var hsh=hash2(gx*13.7+3.1, gz*7.3-2.9);
    var hsh2v=hash2(gx*5.1-9.4, gz*11.9+4.2);

    /* the building: stepped in from the kerb so it sits on its own plateau */
    var fw=(half-3.2)*2*(0.66+hsh*0.24);
    var fd=(half-3.2)*2*(0.66+hsh2v*0.24);
    var bh=7+hsh*hsh2v*46;
    var g=new THREE.Group(); g.position.set(cx,top,cz); G_CITY.add(g);

    var b=new THREE.Mesh(new THREE.BoxGeometry(fw,bh,fd),WALLS[Math.floor(hsh*4)%4]);
    b.position.y=bh*0.5; b.castShadow=true; b.receiveShadow=true; g.add(b);
    var cap=new THREE.Mesh(new THREE.BoxGeometry(fw+0.9,0.7,fd+0.9),roofM);
    cap.position.y=bh+0.35; cap.castShadow=true; g.add(cap);

    /* window bands, which is what makes a box read as a building */
    var rows=Math.max(1,Math.floor(bh/4.4));
    for(var r=0;r<rows;r++){
      var wy=3.0+r*4.4;
      if(wy>bh-1.6) break;
      var wA=new THREE.Mesh(new THREE.BoxGeometry(fw*0.86,1.9,0.14),glassM);
      wA.position.set(0,wy,fd*0.5+0.05); g.add(wA);
      var wB=wA.clone(); wB.position.z=-fd*0.5-0.05; g.add(wB);
      var wC=new THREE.Mesh(new THREE.BoxGeometry(0.14,1.9,fd*0.86),glassM);
      wC.position.set(fw*0.5+0.05,wy,0); g.add(wC);
      var wD=wC.clone(); wD.position.x=-fw*0.5-0.05; g.add(wD);
    }

    /* a kerb line around the plateau, so the edge reads before you hit it */
    [[0,half-0.5,fw+half,0.9],[0,-(half-0.5),fw+half,0.9],
     [half-0.5,0,0.9,fd+half],[-(half-0.5),0,0.9,fd+half]].forEach(function(k){
      var kb=new THREE.Mesh(new THREE.BoxGeometry(k[2],0.34,k[3]),kerbM);
      kb.position.set(k[0],0.17,k[1]); g.add(kb);
    });

    /* one street light per block corner, on the kerb */
    if(lampsMade<64){
      var lx=(half-1.0)*(hsh>0.5?1:-1), lz=(half-1.0)*(hsh2v>0.5?1:-1);
      var lg=new THREE.Group(); lg.position.set(lx,0,lz); g.add(lg);
      var pole=new THREE.Mesh(new THREE.CylinderGeometry(0.13,0.16,7.4,6),poleM);
      pole.position.y=3.7; pole.castShadow=true; lg.add(pole);
      var armM=new THREE.Mesh(new THREE.BoxGeometry(2.0,0.16,0.16),poleM);
      armM.position.set(-lx>0?1.0:-1.0,7.3,0); lg.add(armM);
      var head=new THREE.Mesh(new THREE.BoxGeometry(1.0,0.34,0.5),lampMat());
      head.position.set(-lx>0?1.9:-1.9,7.1,0); lg.add(head);
      lampsMade++;
    }
  }
})();

/* ================= the truck ================= */""")

# ------------------------------------------------------- the switch itself
sub("""function setPedalMode(m){""",
"""function setMap(i){
  MAP=i;
  G_DESERT.visible=(i===0);
  G_CITY.visible=(i===1);
  buildTerrain();
  /* the light pool indexes lit things by world position, and the city's lamps
     only exist once the city group is built, so rebuild the index on a swap */
  rebuildLightPts();
  var st=MAPS[i].start;
  placeTruck(st[0],st[1],st[2]);
  breakChain();
  try{ localStorage.setItem('coilover.map',String(i)); }catch(_){}
  var b=document.getElementById('b-map');
  if(b) b.textContent='Map: '+MAPS[i].name;
}

function setPedalMode(m){""")

# the light index has to be rebuildable, not built once
sub("""var LIGHTPTS=[];
(function(){""",
"""var LIGHTPTS=[];
function rebuildLightPts(){
  LIGHTPTS.length=0;""")
sub("""      LIGHTPTS.push({p:wp, c:g.c, s:g.s});
    });
  }
})();""",
"""      LIGHTPTS.push({p:wp, c:g.c, s:g.s});
    });
  }
  /* the city's lamps live in their own group, not in LANDMARKS */
  if(typeof G_CITY!=='undefined' && G_CITY.visible){
    G_CITY.updateMatrixWorld(true);
    G_CITY.traverse(function(o){
      if(!o.material) return;
      var g=look(o.material); if(!g) return;
      var wp=new THREE.Vector3(); o.getWorldPosition(wp);
      LIGHTPTS.push({p:wp, c:g.c, s:g.s});
    });
  }
}""")

# and it must run once at boot, after everything exists
sub("""/* ================= go ================= */
(function(){""",
"""/* ================= go ================= */
rebuildLightPts();
(function(){""")

# ---------------------------------------------------------------- the picker
sub("""    <div class="grp">Controls</div>""",
"""    <div class="grp">Map</div>
    <button class="go ghost" id="b-map">Map: Ochre Basin</button>
    <div class="grp">Controls</div>""")

sub("""document.getElementById('b-setback').addEventListener('click',function(){""",
"""document.getElementById('b-map').addEventListener('click',function(){
  setMap((MAP+1)%MAPS.length);
});
document.getElementById('b-setback').addEventListener('click',function(){""")

# ------------------------------------------- segments and feats per map
sub("""      var prev=PROG.seg[SK.seg.id]||0;
      if(SK.segPts>prev){
        PROG.seg[SK.seg.id]=SK.segPts;""",
"""      var key=MAPS[MAP].id+':'+SK.seg.id;
      var prev=PROG.seg[key]||0;
      if(SK.segPts>prev){
        PROG.seg[key]=SK.segPts;""")
sub("""    var b=PROG.seg[SEGMENTS[si].id]||0;""",
    """    var b=PROG.seg[MAPS[MAP].id+':'+SEGMENTS[si].id]||0;""")

# boot on the saved map
sub("""  var v=0; try{ v=parseInt(localStorage.getItem('coilover.veh')||'0',10)||0; }catch(_){}""",
"""  var mp=0; try{ mp=parseInt(localStorage.getItem('coilover.map')||'0',10)||0; }catch(_){}
  if(mp>0 && mp<MAPS.length) setMap(mp); else {
    var mb=document.getElementById('b-map');
    if(mb) mb.textContent='Map: '+MAPS[0].name;
  }
  var v=0; try{ v=parseInt(localStorage.getItem('coilover.veh')||'0',10)||0; }catch(_){}""")

# debug export
sub("    LIGHTPTS:LIGHTPTS, LPOOL:LPOOL, FT:FT, FEATS:FEATS,",
    "    LIGHTPTS:LIGHTPTS, LPOOL:LPOOL, FT:FT, FEATS:FEATS,\n"
    "    MAPS:MAPS, setMap:setMap, getMap:function(){return MAP;},\n"
    "    panMask:panMask, cityBlock:cityBlock,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
