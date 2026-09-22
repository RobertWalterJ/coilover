# -*- coding: utf-8 -*-
"""ember.lite, second pass. Diagnosis first, then the repair.

Measured across four headings at each time of day, against twelve real
ember.lite frames measured the same way:

                 ember.lite   Golden    Dusk    Night
  median              0.175    0.391   0.270    0.194
  p95                 0.704    0.484   0.593    0.518
  saturation          0.578    0.352   0.377    0.444
  blue 200 to 250       50%       2%      4%      31%
  frame below 0.20      59%      14%     20%      40%

The headline is not that Coilover is too bright. It is that it is COMPRESSED.
ember.lite runs from 0.175 to 0.704. Golden runs from 0.391 to 0.484, a span of
nine hundredths, with 43 percent of the frame sitting in a single value bin and
nothing at all above bin six. There are no darks and there are no highlights,
so there is nothing for an ember to be bright against.

Three repairs, and they compound:

ONE, THE RANGE. The four shading bands were mapped into a narrow slice of the
albedo. Each time of day now runs its bands from a genuinely dark floor to a
lit band that goes past 1.0, so sunlit faces can actually blow out while shadow
sits properly down. Golden goes from 0.40 to 1.08 out of the old range and now
runs 0.24 to 1.26.

TWO, THE CURVE. There was no contrast control anywhere in the grade, only a
lift and a shoulder, so whatever the renderer produced arrived at the screen
with its mid tones intact. A pivot contrast is now applied around a low pivot,
which pushes the middle down without touching what little is already bright.

THREE, THE BLUE. I am not adding blue anywhere new, because when I did that
before the blue met the amber everywhere and averaged to violet mud. The blue
already lives in the darkest band only. Making the frame properly dark puts far
more of it INTO that band, so the blue arrives as a consequence of fixing the
key rather than as a paint job. Saturation comes up at the same time, toward
the reference's 0.578, which the frame can now carry because it has range.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------- 1. the band range
# bLo drops (real shadow) and bSt rises (lit faces pass 1.0 and clip)
sub("bLo:0.27, bSt:0.190, sat:1.10, expo:1.00, bloom:0.45, bthr:0.74,",
    "bLo:0.17, bSt:0.285, sat:1.42, expo:1.00, bloom:0.52, bthr:0.68, con:0.30, piv:0.30,")
sub("bLo:0.47, bSt:0.205, sat:1.04, expo:1.00, bloom:0.22, bthr:0.88,",
    "bLo:0.33, bSt:0.300, sat:1.28, expo:1.00, bloom:0.30, bthr:0.82, con:0.22, piv:0.42,")
sub("bLo:0.40, bSt:0.225, sat:1.12, expo:1.00, bloom:0.48, bthr:0.72,",
    "bLo:0.24, bSt:0.340, sat:1.46, expo:1.00, bloom:0.56, bthr:0.66, con:0.34, piv:0.33,")
sub("bLo:0.18, bSt:0.175, sat:1.18, expo:1.00, bloom:0.85, bthr:0.60,",
    "bLo:0.10, bSt:0.250, sat:1.52, expo:1.00, bloom:0.92, bthr:0.54, con:0.40, piv:0.24,")
sub("bLo:0.10, bSt:0.140, sat:1.12, expo:1.00, bloom:1.05, bthr:0.44,",
    "bLo:0.05, bSt:0.190, sat:1.50, expo:1.00, bloom:1.15, bthr:0.38, con:0.44, piv:0.17,")

# ------------------------------------------------------------- 2. the curve
sub("        uSat:{value:1.20}, uVig:{value:0.16}, uGrain:{value:0.016},",
    "        uSat:{value:1.46}, uVig:{value:0.16}, uGrain:{value:0.016},\n"
    "        uCon:{value:0.34}, uPiv:{value:0.33},")
sub("        'uniform float uExpo,uBloom; uniform sampler2D tPaper,tBloom;',",
    "        'uniform float uExpo,uBloom,uCon,uPiv; uniform sampler2D tPaper,tBloom;',")

# applied before the split tone, so the grade acts on a frame with real range
sub("""        '  c *= uExpo;',""",
"""        '  c *= uExpo;',
        /* Pivot contrast. There was no contrast control at all before, so the
           mid tones arrived on screen exactly as the renderer left them and
           the whole frame lived in one narrow band. Pivoting low pushes the
           middle down and leaves the little that is already bright alone. */
        '  c = max(vec3(0.0), (c - uPiv) * (1.0 + uCon*2.4) + uPiv*(1.0 - uCon*0.55));',""")

# ------------------------------------------------------- drive both per time
sub("""  if(POST){
    POST.mat.uniforms.uSat.value=LF(A.sat,B.sat);""",
"""  if(POST){
    POST.mat.uniforms.uSat.value=LF(A.sat,B.sat);
    POST.mat.uniforms.uCon.value=LF(A.con,B.con);
    POST.mat.uniforms.uPiv.value=LF(A.piv,B.piv);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
