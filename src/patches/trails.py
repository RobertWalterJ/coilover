# -*- coding: utf-8 -*-
"""Pike Narrows, made passable: causeways, trails, and a thinner bush.

Three things made it a place you could look at but not get across.

THE ROAD DROVE INTO THE LAKES. The lake carve ran after the road grading, so
wherever the haul road met water it simply stopped and the ground fell away to
the bed. It now crosses on a causeway held two metres above the water line, and
where the water is deep there is a timber bridge standing on piles, with rails,
so the crossing is a thing you can see coming.

THERE WAS NO WAY THROUGH THE BUSH. The only cleared lines were the haul road
and the esker, and everything else was trees with collision on them. There are
now three winding trails cut through the bush, lightly graded so they are
smoother than what they cross, with the trees held back eight metres either
side. They connect the quiet parts of the map to the road.

AND THE BUSH WAS TOO THICK. 560 spruce and 300 birch in a 400 m circle, with
collision on every trunk over nine metres. Down to 360 and 190, and a spruce
now needs to be a real tree before it becomes a wall: the collision threshold
goes from 9 m to 10.5 m, so the smaller ones are scenery you brush past.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- the trails
sub("""/* The logging road wanders north to south with one spur running east. */""",
"""/* Three trails cut through the bush, so the middle of the map is reachable
   without the haul road. Lightly graded, and the trees are held off them. */
function shTrailD(x,z){
  var a=Math.abs(z - (Math.sin(x*0.0168-0.4)*44 - Math.sin(x*0.0067+2.2)*58 - 46));
  var b=Math.abs(x - (Math.sin(z*0.0192+1.7)*36 + Math.cos(z*0.0081)*70 + 92));
  var c=Math.abs(z - (Math.cos(x*0.0131+2.6)*52 + 104));
  return Math.min(a,Math.min(b,c));
}
/* The logging road wanders north to south with one spur running east. */""")

# ---- grade the trails, and carry the road over the water
sub("""  /* the road takes the broad shape and ignores the chop, which is grading */
  var rd=1-sstep(5.6,13.0,shRoadD(x,z));
  h = h*(1-rd) + (broad-0.8)*rd;""",
"""  /* the road takes the broad shape and ignores the chop, which is grading */
  var rd=1-sstep(5.6,13.0,shRoadD(x,z));
  h = h*(1-rd) + (broad-0.8)*rd;
  /* the trails are cut, not graded: half the chop taken out, not all of it */
  var tr=1-sstep(4.0,10.0,shTrailD(x,z));
  h = h*(1-tr*0.62) + (broad+fbm(x*0.0140,z*0.0140,2)*3.2-1.6)*(tr*0.62);""")

sub("""  var ld=shLakeD(x,z);
  if(ld<1.34){
    var t=1-sstep(0.94,1.34,ld);
    h = h*(1-t) + (SH_WATER-1.6-4.4*t)*t;
  }""",
"""  var ld=shLakeD(x,z);
  if(ld<1.34){
    var t=1-sstep(0.94,1.34,ld);
    h = h*(1-t) + (SH_WATER-1.6-4.4*t)*t;
    /* But the road crosses. Wherever the haul road or a trail meets water it
       goes over on a causeway, held above the water line, rather than driving
       into the lake -- which is what it did before. */
    var cw=Math.max(1-sstep(5.0,11.0,shRoadD(x,z)), 1-sstep(3.6,8.0,shTrailD(x,z)));
    if(cw>0) h = h*(1-cw) + Math.max(h, SH_WATER+2.0)*cw;
  }""")

# ---- the trails are a surface you can feel
sub("""    if(shRoadD(x,z)<5.6)  return 10;                  /* the logging road */
    if(shEskerD(x,z)<11)  return 10;                  /* and the esker is gravel */""",
"""    if(shRoadD(x,z)<5.6)  return 10;                  /* the logging road */
    if(shEskerD(x,z)<11)  return 10;                  /* and the esker is gravel */
    if(shTrailD(x,z)<4.0) return 10;                  /* and the cut trails */""")

# ---- and they show
sub("""      var rdw=Math.max(1-sstep(4.4,6.6,shRoadD(mx,mz)), 1-sstep(8,12,shEskerD(mx,mz)));""",
"""      var rdw=Math.max(1-sstep(4.4,6.6,shRoadD(mx,mz)),
                Math.max(1-sstep(8,12,shEskerD(mx,mz)),
                         (1-sstep(2.8,4.6,shTrailD(mx,mz)))*0.82));""")

# ---------------------------------------------------------- a thinner bush
sub("  var NS=560, NB=300;", "  var NS=360, NB=190;")
sub("""  function clear(x,z,needRoad){
    if(Math.hypot(x,z)>206) return false;
    if(shLakeD(x,z)<1.05) return false;
    var onRoad=(shRoadD(x,z)<8.5 || shEskerD(x,z)<13);
    if(needRoad) return onRoad;
    return !onRoad;
  }""",
"""  function clear(x,z,needRoad){
    if(Math.hypot(x,z)>206) return false;
    if(shLakeD(x,z)<1.05) return false;
    /* trails are held clear too, or they are lines of trees rather than a way
       through, which is what made the bush impassable */
    var onRoad=(shRoadD(x,z)<8.5 || shEskerD(x,z)<13 || shTrailD(x,z)<8.0);
    if(needRoad) return onRoad;
    return !onRoad;
  }""")
sub("      if(hgt>9.0) BLD.push({x:x,z:z,w:0.9,d:0.9,y:y-1,h:hgt});",
    "      if(hgt>10.5) BLD.push({x:x,z:z,w:0.9,d:0.9,y:y-1,h:hgt});")

# ------------------------------------------------- a bridge where it is deep
sub("""  /* ---- a thing built out of boxes, with collision ---- */""",
"""  /* ---- timber bridges, where the haul road crosses open water ----
     Walk the road and put a deck on piles over any stretch that is properly
     wet, so the crossing announces itself instead of being a wet patch. */
  (function(){
    var run=null;
    for(var bz=-200; bz<=200; bz+=4){
      var bx=Math.sin(bz*0.0125)*86 + Math.sin(bz*0.0041+1.2)*54 - 34;
      var wet=(shLakeD(bx,bz)<1.02 && Math.hypot(bx,bz)<204);
      if(wet){ if(!run) run=[bz,bz]; else run[1]=bz; }
      else if(run){
        if(run[1]-run[0]>10) deck(run[0],run[1]);
        run=null;
      }
    }
    if(run && run[1]-run[0]>10) deck(run[0],run[1]);
    function deck(z0,z1){
      var g=new THREE.Group(); G_SHIELD.add(g);
      for(var q=z0;q<=z1;q+=3.2){
        var qx=Math.sin(q*0.0125)*86 + Math.sin(q*0.0041+1.2)*54 - 34;
        var d1=new THREE.Mesh(new THREE.BoxGeometry(11.0,0.34,3.4),dockM);
        d1.position.set(qx, SH_WATER+2.10, q); d1.receiveShadow=true; g.add(d1);
        [-1,1].forEach(function(sd){
          var pl=new THREE.Mesh(new THREE.BoxGeometry(0.30,3.4,0.30),poleM);
          pl.position.set(qx+sd*4.9, SH_WATER+0.55, q); pl.castShadow=true; g.add(pl);
          var rl=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.16,3.4),dockM);
          rl.position.set(qx+sd*5.3, SH_WATER+3.00, q); g.add(rl);
          var ps=new THREE.Mesh(new THREE.BoxGeometry(0.16,0.90,0.16),dockM);
          ps.position.set(qx+sd*5.3, SH_WATER+2.60, q); g.add(ps);
        });
      }
    }
  })();

  /* ---- a thing built out of boxes, with collision ---- */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
