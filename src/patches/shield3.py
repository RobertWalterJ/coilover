# -*- coding: utf-8 -*-
"""Start where the map says to start, not at the desert's origin.

The opening button called `placeTruck(0,0,0.4)` with the desert's coordinates
hard coded. On the city that happened to land on tarmac and the spawn guard
tidied up the rest; on Pike Narrows the origin is under eight metres of lake,
so pressing Drive put you on the bottom of it. It now reads the active map's
own start point, like every other path that places the truck.

And the guard that walks a bad spawn out to safety only knew about the city's
streets. It now also knows about water: if you are put in a lake, it walks you
out along the line from the lake's centre until the ground is dry.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("  placeTruck(0,0,0.4);\n  S.running=true; last=performance.now(); acc=0;\n});",
    "  var st0=MAPS[MAP].start;                 /* not the desert's origin */\n"
    "  placeTruck(st0[0],st0[1],st0[2]);\n"
    "  S.running=true; last=performance.now(); acc=0;\n});")

sub("""function safeSpot(x,z){
  if(MAP!==1) return [x,z];""",
"""function safeSpot(x,z){
  if(MAP===2){
    /* out of the water, along the line from the lake's centre */
    if(shLakeD(x,z)>=1.10) return [x,z];
    var bi=0, bd=9;
    for(var i=0;i<SH_LAKES.length;i++){
      var L=SH_LAKES[i], dd=Math.hypot((x-L[0])/L[2],(z-L[1])/L[3]);
      if(dd<bd){ bd=dd; bi=i; }
    }
    var LK=SH_LAKES[bi];
    var ux=x-LK[0], uz=z-LK[1], ul=Math.hypot(ux,uz);
    if(ul<0.001){ ux=1; uz=0; ul=1; }
    ux/=ul; uz/=ul;
    for(var st=0;st<220;st++){
      var nx=x+ux*st, nz=z+uz*st;
      if(shLakeD(nx,nz)>1.14) return [nx+ux*6, nz+uz*6];
    }
    return [x,z];
  }
  if(MAP!==1) return [x,z];""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
