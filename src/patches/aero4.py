# -*- coding: utf-8 -*-
"""Size the downforce against the speed each car can actually reach.

Raising the speed ceilings put the Veloce back where it started: 13,495 N of
downforce at 209 km/h against 12,850 N of car, so it bottoms out again at the
one speed it was built for. Downforce is a square law, and I had sized it for a
top speed that has since gone up by half. Rescaled so each car makes a sensible
fraction of its own weight at ITS OWN ceiling rather than at a shared one.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

sub("rb:0.50, aero:0.35,", "rb:0.50, aero:0.30,")
sub("rb:0.53, aero:0.80,", "rb:0.53, aero:0.55,")
sub("rb:0.62, aero:1.40, aeroF:0.34,", "rb:0.62, aero:0.95, aeroF:0.34,")
sub("rb:0.57, aero:2.00, aeroF:0.40,", "rb:0.57, aero:1.30, aeroF:0.40,")
sub("    aero:4.20, aeroF:0.44,", "    aero:1.70, aeroF:0.44,")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
