# -*- coding: utf-8 -*-
"""Round the Shield off, because that is what a glacier did to it.

Surveyed 3000 points on each map and compared:

                 <8deg   8-18   18-30   30-42   >42   max
  Ochre Basin     47%     34%     12%      4%    3%    61
  Pike Narrows    39%     18%     15%     14%   14%    79

Twenty eight percent of Pike Narrows was steeper than thirty degrees against
the desert's seven, and a seventh of the map was over forty two, which is a
wall you cannot climb. Two causes, and the first is also just wrong about the
place:

THE DOMES WERE SQUARED. `shDome^2 * 24` puts the steepest part of the curve at
the TOP of the dome, so each one had a sharp shoulder and a cliff on its flank.
Real Shield outcrops are the opposite: the ice rode over them for ten thousand
years and left whalebacks that are smooth all the way over. A smoothstep
profile has zero slope at both the base and the crest, which is the actual
shape, and it drops the peak gradient by a third at the same height.

THE LAKE SHORES FELL TOO FAST. The bed was carved over a band 0.24 wide in lake
radii, about nineteen metres of ground, dropping ten. Widened to 0.40 and made
shallower, so a shoreline is a beach you can drive along rather than a step.

AND THE CAMPS WERE ON CLIFFS. Placement walked out from the lake centre and
stopped at the first dry ground, which on a steep shore is a 35 degree slope.
It now keeps walking until it finds ground under 14 degrees, and skips the camp
rather than perching one on a rock face.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- whalebacks, not cliffs
sub("  h += shDome(x,z)*shDome(x,z)*24;                   /* granite whalebacks */",
    "  /* smoothstep, not square: zero gradient at the base AND at the crest, so\n"
    "     the dome is smooth all the way over the top the way the ice left it */\n"
    "  var dm=shDome(x,z);\n"
    "  h += dm*dm*(3-2*dm)*15;                            /* granite whalebacks */")

# ---- shores you can drive along
sub("""  var ld=shLakeD(x,z);
  if(ld<1.22){
    var t=1-sstep(0.98,1.22,ld);
    h = h*(1-t) + (SH_WATER-3.0-7.0*t)*t;
  }""",
"""  var ld=shLakeD(x,z);
  if(ld<1.34){
    var t=1-sstep(0.94,1.34,ld);
    h = h*(1-t) + (SH_WATER-1.6-4.4*t)*t;
  }""")

# ---- the bush closing the map is a shoulder, not a wall
sub("  if(r>210) h += Math.min(58, Math.pow((r-210)*0.049,2.1)*15);",
    "  if(r>224) h += Math.min(52, Math.pow((r-224)*0.043,1.9)*15);")

# ---- and the camps stand on something flat
sub("""    if(!found) continue;
    var inX=(LK[0]-fx), inZ=(LK[1]-fz), il=Math.hypot(inX,inZ)||1;
    inX/=il; inZ/=il;
    camp(fx+inX*-7, fz+inZ*-7, Math.atan2(-inX,-inZ));
    dock(fx+inX*1.5, fz+inZ*1.5, inX, inZ);""",
"""    if(!found) continue;
    var inX=(LK[0]-fx), inZ=(LK[1]-fz), il=Math.hypot(inX,inZ)||1;
    inX/=il; inZ/=il;
    /* Walk back from the water until the ground is flat enough to build on.
       Stopping at the first dry ground put camps on 35 degree rock faces. */
    var back=6, flat=false;
    for(var bk2=6;bk2<44;bk2+=2.5){
      var tx2=fx-inX*bk2, tz2=fz-inZ*bk2;
      var h0=height(tx2,tz2);
      var gxx=(height(tx2+2,tz2)-height(tx2-2,tz2))/4;
      var gzz=(height(tx2,tz2+2)-height(tx2,tz2-2))/4;
      if(Math.atan(Math.hypot(gxx,gzz))<0.245){ back=bk2; flat=true; break; }
    }
    if(!flat) continue;                       /* no camp rather than a perched one */
    camp(fx-inX*back, fz-inZ*back, Math.atan2(-inX,-inZ));
    dock(fx+inX*1.5, fz+inZ*1.5, inX, inZ);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
