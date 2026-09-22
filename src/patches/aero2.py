# -*- coding: utf-8 -*-
"""Make the grip numbers real, and stop the downforce crushing the car.

THE GRIP NUMBERS DID NOTHING. Every vehicle carries a muF and a muR, the
garage draws a Grip bar from them, and the Veloce was given the highest pair of
the five specifically so it would resist sliding. They were assigned into
MU_LAT_F and MU_LAT_R at line 2375 and then never read again by anything. The
tyre solver takes its friction from c2.muF/c2.muR, which are relaxed toward the
SURFACE's mu every frame. So all five cars had identical tyre grip, the Grip
bar was decorative, and no amount of tuning a vehicle's mu could ever have
changed how it cornered.

They are now a multiplier on the surface, normalised so the Bracken's 1.00/0.92
comes out at exactly 1.0 and the existing handling is untouched. The multiplier
lands on muL, which feeds both the lateral force and the friction ellipse, so
a grippier car brakes and accelerates better too.

THE DOWNFORCE WAS ABSURD. The Veloce made 18,993 N at 130 km/h against its own
weight of 12,850 N, so it was pressed into the ground with one and a half times
its mass. Four corners of 27,600 N/m spring have 0.43 m of travel; that load
asks for 0.69 m. It was fully bottomed at speed, which is why it cornered at
43 km/h while the Bracken managed 79. All five are rescaled to something a car
could survive: the Veloce now makes about 42 percent of its weight at its top
speed, which is a lot, and the rest proportionally less.

THE BALANCE. Its anti-roll bars were softer at the front than the rear, which
is the setup you choose when you want the back to step out. Reversed, because
you asked for the opposite.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ============================================ 1. the vehicle's grip is real
sub("var MU_LAT_F=1.00, MU_LAT_R=0.92, MU_LONG_MULT=1.08;",
    "var MU_LAT_F=1.00, MU_LAT_R=0.92, MU_LONG_MULT=1.08;\n"
    "/* The vehicle's own grip, as a multiplier on whatever it is driving over.\n"
    "   Normalised against the Bracken so it comes out at 1.0 and nothing that\n"
    "   was tuned before this line existed has moved. */\n"
    "var GRIP_F=1.0, GRIP_R=1.0;")

sub("    MU_LAT_F=V.muF; MU_LAT_R=V.muR;",
    "    MU_LAT_F=V.muF; MU_LAT_R=V.muR;\n"
    "    GRIP_F=V.muF/1.00; GRIP_R=V.muR/0.92;")

sub("    var muBase=c2.front?c2.muF:c2.muR;",
    "    /* surface grip times this car's tyres, instead of the surface alone */\n"
    "    var muBase=c2.front? c2.muF*GRIP_F : c2.muR*GRIP_R;")

# ============================================ 2. downforce a car can survive
sub("rb:0.50, aero:1.2,", "rb:0.50, aero:0.35,")
sub("rb:0.53, aero:2.6,", "rb:0.53, aero:0.80,")
sub("rb:0.62, aero:4.4, aeroF:0.34,", "rb:0.62, aero:1.40, aeroF:0.34,")
sub("rb:0.57, aero:6.5, aeroF:0.40,", "rb:0.57, aero:2.00, aeroF:0.40,")
sub("    aero:14.5, aeroF:0.44,", "    aero:4.20, aeroF:0.44,")

# ============================================ 3. and it should understeer
sub("    arbF:7600, arbR:9200, drive:31500, brake:31000, biasF:0.62,",
    "    arbF:9800, arbR:6600, drive:31500, brake:31000, biasF:0.62,")

# ============================================ 4. bars that fit their own scale
sub("document.getElementById('g-pow').style.width =pct(V.drive,20000,30500);",
    "document.getElementById('g-pow').style.width =pct(V.drive,20000,32000);")
sub("document.getElementById('g-grip').style.width=pct((V.muF+V.muR)/2,0.93,1.07);",
    "document.getElementById('g-grip').style.width=pct((V.muF+V.muR)/2,0.93,1.20);")
sub("if(ae) ae.style.width=pct(V.aero||0,0,15);",
    "if(ae) ae.style.width=pct(V.aero||0,0,4.4);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
