# -*- coding: utf-8 -*-
"""The lakebed tint was keyed to "low and flat", but the whole basin floor sits
near minus eleven metres, so every flat patch came out pale. Key the colour to
the same mask that carves the lakebed, and share it between shape and colour so
the two can never disagree again."""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:80].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# one mask, used by both the heightfield and the painter
sub("""function baseH(x,z){""",
    """function lakeMask(x,z){ return disc(x,z,-96,96,50,36); }
function baseH(x,z){""")

sub("""  /* dry lakebed, dead flat, the fast bit */
  var lb=disc(x,z,-96,96,50,36);
  h = h*(1-lb) + (-4.2)*lb;""",
    """  /* dry lakebed, dead flat, the fast bit */
  var lb=lakeMask(x,z);
  h = h*(1-lb) + (-4.2)*lb;""")

sub("""    c.lerp(C_LAKE, sstep(0.02,0.004,slope)*sstep(-3.4,-4.2,y));""",
    """    c.lerp(C_LAKE, lakeMask(x,z));""")

# the surface grain was fine enough to alias against a two metre grid, which
# read as noise rather than facets and kept the suspension chattering
sub("""  h += (vnoise(x*0.105, z*0.105)-0.5)*0.5;           /* surface grain */""",
    """  h += (vnoise(x*0.058, z*0.058)-0.5)*0.30;          /* surface grain */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
