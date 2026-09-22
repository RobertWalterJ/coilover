# -*- coding: utf-8 -*-
"""Cab first, body second, which is the whole silhouette of these things.

The step was there but the cab was only 0.62 m of it, so the tall mass on
screen was the rear body and the cab read as a stub bonnet in front of a
lorry. On a Kamaz or an Iveco the cab is the front third of the vehicle and
the tallest thing on it; the body behind sits visibly lower.

Cab now runs from the front face back to z=0.75 and tops out at 1.24. Rear body
drops to 0.94, so the step is 30 cm rather than 16 and reads from any angle.

The spares stood on end at 1.42 and were the tallest thing on the truck, which
made it look like it was carrying a satellite dish. They lie flat on the deck.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

old_list = """      {z: 2.44, w:hw*0.88, y: 0.50, up:0.54, dn:0.58, n:5.4},
      {z: 2.30, w:hw*0.97, y: 0.52, up:0.62, dn:0.62, n:6.2},
      {z: 1.94, w:hw*1.10, y: 0.52, up:0.64, dn:0.62, n:6.4},   /* front flare */
      {z: 1.70, w:hw*1.17, y: 0.52, up:0.64, dn:0.60, n:6.6},
      {z: 1.44, w:hw*1.08, y: 0.53, up:0.65, dn:0.62, n:6.4},
      {z: 0.88, w:hw*1.00, y: 0.54, up:0.66, dn:0.64, n:6.6},
      {z: 0.62, w:hw*0.95, y: 0.44, up:0.44, dn:0.58, n:5.6},   /* the step */
      {z: 0.34, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-1.28, w:hw*1.08, y: 0.48, up:0.56, dn:0.58, n:6.4},   /* rear flare */
      {z:-1.54, w:hw*1.17, y: 0.48, up:0.56, dn:0.56, n:6.6},
      {z:-1.80, w:hw*1.08, y: 0.48, up:0.56, dn:0.58, n:6.4},
      {z:-2.02, w:hw*0.97, y: 0.48, up:0.56, dn:0.60, n:6.2},
      {z:-2.30, w:hw*0.92, y: 0.46, up:0.52, dn:0.56, n:5.8},
      {z:-2.42, w:hw*0.78, y: 0.44, up:0.44, dn:0.48, n:5.0}"""

new_list = """      {z: 2.44, w:hw*0.90, y: 0.54, up:0.66, dn:0.60, n:5.6},
      {z: 2.32, w:hw*0.99, y: 0.56, up:0.68, dn:0.64, n:6.4},   /* blunt face */
      {z: 1.94, w:hw*1.10, y: 0.56, up:0.68, dn:0.64, n:6.4},   /* front flare */
      {z: 1.70, w:hw*1.17, y: 0.56, up:0.68, dn:0.62, n:6.6},
      {z: 1.44, w:hw*1.06, y: 0.56, up:0.68, dn:0.64, n:6.4},
      {z: 0.92, w:hw*1.00, y: 0.56, up:0.68, dn:0.64, n:6.6},   /* cab, all of it */
      {z: 0.75, w:hw*0.99, y: 0.55, up:0.66, dn:0.64, n:6.6},
      {z: 0.58, w:hw*0.93, y: 0.40, up:0.38, dn:0.56, n:5.4},   /* the step down */
      {z: 0.34, w:hw*0.96, y: 0.44, up:0.50, dn:0.58, n:6.2},
      {z:-0.60, w:hw*0.96, y: 0.44, up:0.50, dn:0.58, n:6.2},
      {z:-1.28, w:hw*1.08, y: 0.44, up:0.50, dn:0.56, n:6.4},   /* rear flare */
      {z:-1.54, w:hw*1.17, y: 0.44, up:0.50, dn:0.54, n:6.6},
      {z:-1.80, w:hw*1.08, y: 0.44, up:0.50, dn:0.56, n:6.4},
      {z:-2.02, w:hw*0.96, y: 0.44, up:0.50, dn:0.58, n:6.2},
      {z:-2.30, w:hw*0.91, y: 0.43, up:0.47, dn:0.54, n:5.8},
      {z:-2.42, w:hw*0.76, y: 0.42, up:0.40, dn:0.46, n:5.0}"""

sub(old_list, new_list)

# the roof panel, the glass and the rack all sit on a cab that has grown
sub("    var scr=box(W*0.80,0.60,0.07, glass, 0, 0.96, 2.22, false);\n"
    "    scr.rotation.x=-0.24;\n"
    "    box(0.06,0.40,0.92, glass, -hw*0.97, 0.92, 1.56, false);\n"
    "    box(0.06,0.40,0.92, glass,  hw*0.97, 0.92, 1.56, false);\n"
    "    /* the cab roof, so the top of the cab is a panel and not the paint */\n"
    "    box(W*0.92,0.09,1.44, second, 0, 1.21, 1.58, false);",
    "    var scr=box(W*0.80,0.64,0.07, glass, 0, 1.00, 2.26, false);\n"
    "    scr.rotation.x=-0.22;\n"
    "    box(0.06,0.44,1.00, glass, -hw*1.00, 0.98, 1.56, false);\n"
    "    box(0.06,0.44,1.00, glass,  hw*1.00, 0.98, 1.56, false);\n"
    "    /* the cab roof, so the top of the cab is a panel and not the paint */\n"
    "    box(W*0.94,0.09,1.66, second, 0, 1.26, 1.50, false);")

sub("    var rz0=2.20, rz1=0.98, ry=1.36;", "    var rz0=2.22, rz1=0.86, ry=1.42;")

# spares lie flat on the deck instead of standing above the whole truck
sub("""    /* the deck top is at 1.04, so a 0.40 spare stands at 1.44, not 0.94 */
    [[-0.50],[0.50]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.40,0.40,0.26,12),tyreM);
      sw.rotation.z=Math.PI/2; add(sw,sp[0],1.42,-1.16);
    });
    box(W*0.88,0.07,0.07, trim, 0, 1.06,-0.58, false);
    box(W*0.88,0.07,0.07, trim, 0, 1.06,-1.86, false);
    box(0.07,0.07,1.34, trim, -hw*0.86, 1.06,-1.22, false);
    box(0.07,0.07,1.34, trim,  hw*0.86, 1.06,-1.22, false);""",
"""    /* Flat on the deck. Stood on end they were the tallest thing on the truck
       and it looked like it was carrying a dish. */
    [[-0.48,-0.90],[0.48,-0.90],[-0.48,-1.72],[0.48,-1.72]].forEach(function(sp){
      var sw=new THREE.Mesh(new THREE.CylinderGeometry(0.38,0.38,0.22,12),tyreM);
      add(sw,sp[0],1.02,sp[1]);
    });
    box(W*0.88,0.06,0.06, trim, 0, 1.00,-0.50, false);
    box(W*0.88,0.06,0.06, trim, 0, 1.00,-2.06, false);
    box(0.06,0.06,1.62, trim, -hw*0.90, 1.00,-1.28, false);
    box(0.06,0.06,1.62, trim,  hw*0.90, 1.00,-1.28, false);""")

sub("    box(W*0.82,0.11,0.07, tailM, 0, 0.62,-2.48, false);",
    "    box(W*0.82,0.11,0.07, tailM, 0, 0.56,-2.48, false);")
sub("    box(0.14,0.92,0.14, trim, hw*0.94, 1.06, 2.02, false);\n"
    "    box(0.16,0.16,0.22, trim, hw*0.94, 1.56, 1.94, false);",
    "    box(0.14,0.96,0.14, trim, hw*0.98, 1.12, 2.04, false);\n"
    "    box(0.16,0.16,0.22, trim, hw*0.98, 1.64, 1.96, false);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
