# -*- coding: utf-8 -*-
"""Built to the measurement, not to my guess.

Twelve ember.lite frames were pulled and measured. What they actually are:

  median luminance 0.175, p95 0.704, every one of ten value bins occupied
  mean saturation 0.578
  hue 210 to 240 is 50 percent of all coloured pixels, warm 30 to 40 is the
  accent, and the dark half of the frame is deep blue at saturation 0.68

Coilover at Golden, measured the same way:

  median 0.321, p95 0.423, three bins hold 93 percent of the frame
  mean saturation 0.431
  hue 330 to 20 is 97 percent, and there is no blue anywhere

So two things are wrong, and neither is the grain.

NO HIGHLIGHTS. Nothing in a Coilover frame goes above 0.42. An ember only
reads as an ember if there is real darkness around it and something genuinely
bright inside it. The top band now runs past 1.0 so lit faces can actually
blow, the sun carries a real core, and the shoulder catches it instead of the
whole frame sitting in the middle.

NO BLUE. The reference is a blue field with warm accents, which is a near
complementary split, and that opposition is most of what the eye reads as the
style. Coilover was one warm arc, so nothing could oppose anything. Shadow,
sky fill, fog and haze all move to deep blue, which is also just true of a real
sunset: the shadows are lit by the sky, and the sky is blue.

The sunset stays. It gets a blue shadow and a hot sun, which is more colour
rather than less.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:100].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------- the shadow goes deep blue
sub("  uShadowTint:{value:sc(0xe0a8ae)},", "  uShadowTint:{value:sc(0x4d5cb8)},")

# and it keeps its chroma instead of being washed toward grey first
sub("'pcS = mix( pcS, mix( pcS, vec3(dot(pcS,LUMA_S)), 0.20 ) * uShadowTint, sTS*0.80 );',",
    "'pcS = mix( pcS, mix( pcS, vec3(dot(pcS,LUMA_S)), 0.34 ) * uShadowTint * 1.85, sTS*0.92 );',")

# ---------------------------------------------------- per time colour and key
# sky fill, fog and haze all move blue; band step opens so the top band can
# exceed 1.0 and give the frame something to actually glow
sub("""    dir:[-70,16,-130], sun:0xffc0b0, sunI:1.20, hemiS:0xa8a8d0, hemiG:0x8f7266, hemiI:0.46,
    sky:[0xe9c3b4,0xd9a89f,0xa98aa8,0x6d6f9c,0x3b4a80], fog:0xc8a0b4, fogN:60, fogF:470,""",
"""    dir:[-70,16,-130], sun:0xffc0b0, sunI:1.34, hemiS:0x7d8ae0, hemiG:0x7a5a70, hemiI:0.50,
    sky:[0xffd3b4,0xe09aa4,0x9a7ec0,0x5a62b4,0x2b3a90], fog:0x9a86c4, fogN:60, fogF:470,""")
sub("lift:0.406, gain:3.45, bLo:0.30, bSt:0.150,",
    "lift:0.396, gain:2.30, bLo:0.26, bSt:0.205,")
sub("haze:0xcaa8b8, hazeA:0.52 },", "haze:0x8f8ad2, hazeA:0.50 },")

sub("""    dir:[-96,30,44], sun:0xfff0d2, sunI:1.45, hemiS:0xbcc4e0, hemiG:0xbb8a5c, hemiI:0.44,
    sky:[0xf2e0c2,0xe3d0ae,0xb9c2cf,0x82a2cc,0x4d7ec4], fog:0xcfcadc, fogN:110, fogF:600,""",
"""    dir:[-96,30,44], sun:0xfff0d2, sunI:1.52, hemiS:0x9ab0ee, hemiG:0xb0845e, hemiI:0.46,
    sky:[0xfae6c4,0xdcd6c0,0x93b6dc,0x4f8ad6,0x1f5cc4], fog:0xb6c4e4, fogN:110, fogF:600,""")
sub("lift:0.867, gain:7.08, bLo:0.52, bSt:0.170,",
    "lift:0.858, gain:5.10, bLo:0.46, bSt:0.215,")
sub("haze:0xd3d0dc, hazeA:0.44 },", "haze:0xa8bee2, hazeA:0.44 },")

sub("""    dir:[-120,22,60], sun:0xffb870, sunI:1.42, hemiS:0x8e7aa8, hemiG:0xb0603a, hemiI:0.42,
    sky:[0xffc87a,0xf59a62,0xd9705f,0xa85e7e,0x6b4c86], fog:0xb98498, fogN:70, fogF:560,""",
"""    dir:[-120,22,60], sun:0xffb870, sunI:1.50, hemiS:0x6a76d4, hemiG:0xa8563e, hemiI:0.46,
    sky:[0xffd089,0xfb9257,0xd05f74,0x8253a8,0x3f3f9e], fog:0x8d7ac0, fogN:70, fogF:560,""")
sub("lift:0.639, gain:3.04, bLo:0.42, bSt:0.215,",
    "lift:0.629, gain:2.05, bLo:0.38, bSt:0.240,")
sub("haze:0xc38a92, hazeA:0.58 },", "haze:0x8878c6, hazeA:0.54 },")

sub("""    dir:[-150,7,20], sun:0xff9a6a, sunI:1.05, hemiS:0x6b6ba8, hemiG:0x7a4a48, hemiI:0.70,
    sky:[0x7b3965,0x693b6d,0x513d74,0x152873,0x0a2574], fog:0x8f5a6a, fogN:50, fogF:430,""",
"""    dir:[-150,7,20], sun:0xff9a6a, sunI:1.16, hemiS:0x4a58bc, hemiG:0x6a4258, hemiI:0.72,
    sky:[0xff8a52,0xc4557e,0x6a4098,0x22287e,0x0d1a68], fog:0x5a4a9c, fogN:50, fogF:430,""")
sub("lift:0.271, gain:2.06, bLo:0.22, bSt:0.130,",
    "lift:0.261, gain:1.90, bLo:0.17, bSt:0.185,")
sub("haze:0x8c5f7c, hazeA:0.62 },", "haze:0x4e4494, hazeA:0.58 },")

sub("""    dir:[-150,26,20], sun:0x7f92c8, sunI:0.42, hemiS:0x2a3560, hemiG:0x201824, hemiI:0.42,
    sky:[0x1c144e,0x06094c,0x00002d,0x000018,0x000010], fog:0x241c46, fogN:35, fogF:330,""",
"""    dir:[-150,26,20], sun:0x8fa2e0, sunI:0.46, hemiS:0x28379c, hemiG:0x1c1a34, hemiI:0.44,
    sky:[0x24308c,0x14206e,0x0a1250,0x050a34,0x030520], fog:0x161e5c, fogN:35, fogF:330,""")
sub("lift:0.082, gain:2.13, bLo:0.12, bSt:0.095,",
    "lift:0.072, gain:1.85, bLo:0.09, bSt:0.150,")
sub("haze:0x2b2450, hazeA:0.50 }", "haze:0x141c5e, hazeA:0.52 }")

# ------------------------------------------------------------- a real sun core
sub("""      '  sky += uSunHalo * pow(sd,  9.0) * 0.34;',
      '  sky += uSunHalo * pow(sd,  2.0) * 0.09;',""",
"""      /* a core hot enough to be a highlight, and a wide halo under it. The
         frame had nothing above 0.42 luma, so nothing could read as lit. */
      '  sky += uSunHalo * pow(sd, 220.0) * 2.20;',
      '  sky += uSunHalo * pow(sd, 26.0) * 0.62;',
      '  sky += uSunHalo * pow(sd,  9.0) * 0.30;',
      '  sky += uSunHalo * pow(sd,  2.0) * 0.11;',""")

# ------------------------------------------------------------------ the grade
# more chroma, a lighter vignette, and a shoulder that starts later so the new
# highlights survive to the screen instead of being pulled back to the middle
sub("uSat:{value:1.08}, uVig:{value:0.22}, uGrain:{value:0.075},",
    "uSat:{value:1.22}, uVig:{value:0.15}, uGrain:{value:0.075},")
sub("'  c = c*0.965 + 0.035*vec3(0.11,0.08,0.12);',",
    "'  c = c*0.985 + 0.015*vec3(0.07,0.06,0.14);',")
sub("'  c = c/(1.0 + max(vec3(0.0), c-0.88)*0.55);',",
    "'  c = c/(1.0 + max(vec3(0.0), c-1.02)*0.42);',")

# per time saturation raised toward the reference's 0.578
for a, b in [("sat:1.10, expo:1.00, bloom:0.45, bthr:0.74,", "sat:1.24, expo:1.00, bloom:0.52, bthr:0.70,"),
             ("sat:1.04, expo:1.00, bloom:0.22, bthr:0.88,", "sat:1.14, expo:1.00, bloom:0.26, bthr:0.86,"),
             ("sat:1.12, expo:1.00, bloom:0.48, bthr:0.72,", "sat:1.26, expo:1.00, bloom:0.55, bthr:0.68,"),
             ("sat:1.18, expo:1.00, bloom:0.85, bthr:0.60,", "sat:1.32, expo:1.00, bloom:0.92, bthr:0.56,"),
             ("sat:1.12, expo:1.00, bloom:1.05, bthr:0.44,", "sat:1.28, expo:1.00, bloom:1.10, bthr:0.40,")]:
    sub(a, b)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
