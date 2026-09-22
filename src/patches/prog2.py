# -*- coding: utf-8 -*-
"""Three ways the new lock could strand you, closed.

1. THE GARAGE TRAP. The garage has exactly one button. Disabling it on a locked
   car meant browsing to the Veloce left you in a sheet with nothing to press.
   The button is never disabled; on a locked car it reads "Back" and returns
   you to the menu on the last car you can actually drive.

2. BROWSING APPLIED THE CAR. `pickVehicle` sets the vehicle the moment you
   press the arrow, so a locked car was already under you and was written to
   local storage. It is still shown, because you should be able to look at what
   you are working towards, but only an unlocked one is ever remembered.

3. THE MAP BUTTON cycled straight into a locked map. It now says the price
   instead of switching, and puts the label back after a moment.

4. AN OLD SAVE could name a car that now has a price on it. Clamped at load.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- 1. the button is never a dead end
sub("  if(tk){ tk.disabled=!ok; tk.textContent=ok?'Drive this one':'Locked'; }",
    "  /* Never disable it: this sheet has one button, and a disabled one is a\n"
    "     room with no door. Locked just means it takes you back instead. */\n"
    "  if(tk){ tk.disabled=false; tk.textContent=ok?'Drive this one':'Back'; }")

sub("document.getElementById('g-take').addEventListener('click',closeGarage);",
    "document.getElementById('g-take').addEventListener('click',function(){\n"
    "  if(have(VEHICLES[VEH])){ closeGarage(); return; }\n"
    "  /* browsing a locked one is only looking; put the driveable car back */\n"
    "  pickVehicle(lastOwned());\n"
    "  closeGarage();\n"
    "});")

# ---- 2. only an unlocked car is remembered
sub("  try{ localStorage.setItem('coilover.veh',String(i)); }catch(_){}\n"
    "  garageCard();",
    "  if(have(VEHICLES[i])){\n"
    "    try{ localStorage.setItem('coilover.veh',String(i)); }catch(_){}\n"
    "  }\n"
    "  garageCard();")

sub("function nextUnlock(){",
    "/* The best car you have actually earned, for when a locked one has to be\n"
    "   handed back. */\n"
    "function lastOwned(){\n"
    "  var b=0;\n"
    "  for(var i=0;i<VEHICLES.length;i++) if(have(VEHICLES[i])) b=i;\n"
    "  return b;\n"
    "}\n"
    "function nextUnlock(){")

# ---- 3. the map button states the price rather than switching
sub("document.getElementById('b-map').addEventListener('click',function(){\n"
    "  setMap((MAP+1)%MAPS.length);\n"
    "});",
    "document.getElementById('b-map').addEventListener('click',function(){\n"
    "  var nx=(MAP+1)%MAPS.length, self=this;\n"
    "  if(!have(MAPS[nx])){\n"
    "    self.textContent=MAPS[nx].name+': '+commas(priceOf(MAPS[nx])-PROG.score)+' points away';\n"
    "    clearTimeout(self.__t);\n"
    "    self.__t=setTimeout(function(){ self.textContent='Map: '+MAPS[MAP].name; },2200);\n"
    "    return;\n"
    "  }\n"
    "  setMap(nx);\n"
    "});")

# ---- 4. an old save cannot name a car that now costs something
sub("  window.__setVehicle(Math.max(0,Math.min(VEHICLES.length-1,v)));",
    "  v=Math.max(0,Math.min(VEHICLES.length-1,v));\n"
    "  if(!have(VEHICLES[v])) v=lastOwned();      /* a save from before prices */\n"
    "  window.__setVehicle(v);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
