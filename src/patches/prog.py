# -*- coding: utf-8 -*-
"""Points that mean something, and three labels that were lying.

PROGRESSION. `PROG.score` accumulated forever, was drawn in three places, and
was read by nothing. Every car and both maps were available from the first
second, so the tally was a number that went up next to a game that never
changed. That is the thing you said twice you were not seeing.

Points now buy the garage. Each car past the Bracken has a price, the city has
a price, the garage shows a locked car's price against your total rather than
hiding it (you should be able to see what you are driving towards), and the
pause screen carries one line saying what is next and how far away it is. When
a threshold falls mid drive it announces itself and saves.

LANDMARKS PAID NOTHING. Finding one chimed, buzzed, planted a flag and awarded
zero points. There are twelve of them and they were worth nothing at all.

THE CHAIN WAS DRAWN TWICE, once large in the centre and again in the corner
tally. The centre keeps it, because that is where the act happens.

"LET IT DRIFT" IS NOT ABOUT DRIFTING. It drifts the time of day, and it sat in
Controls between the pedal mode and the tilt steering, which is the worst
possible place for it. Renamed and moved to View and sound.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ============================================================ 1. the prices
sub("id:'bracken',", "id:'bracken', unlock:0,")
sub("id:'marisol',", "id:'marisol', unlock:6000,")
sub("id:'kestrel',", "id:'kestrel', unlock:18000,")
sub("id:'serrano',", "id:'serrano', unlock:40000,")
sub("id:'veloce',", "id:'veloce', unlock:78000,")

sub("{id:'city',  name:'Vantage Hill', kind:'City and pan',",
    "{id:'city',  name:'Vantage Hill', kind:'City and pan', unlock:12000,")

# ======================================================== 2. what is unlocked
sub("function driftName(d){",
    "/* Unlocking is derived from the lifetime tally rather than stored, so it can\n"
    "   never disagree with the number on screen. */\n"
    "function priceOf(o){ return o.unlock||0; }\n"
    "function have(o){ return PROG.score >= priceOf(o); }\n"
    "function commas(v){ return String(Math.round(v)).replace(/\\B(?=(\\d{3})+(?!\\d))/g,','); }\n"
    "/* The cheapest thing still out of reach, which is the only one worth naming. */\n"
    "function nextUnlock(){\n"
    "  var best=null;\n"
    "  function look(o,kind){\n"
    "    if(have(o)) return;\n"
    "    if(!best || priceOf(o)<priceOf(best.o)) best={o:o,kind:kind};\n"
    "  }\n"
    "  for(var i=0;i<VEHICLES.length;i++) look(VEHICLES[i],'vehicle');\n"
    "  for(var m=0;m<MAPS.length;m++)     look(MAPS[m],'map');\n"
    "  return best;\n"
    "}\n"
    "/* Called after every award, so anything the last points just bought says so. */\n"
    "var UNL_SEEN=-1;\n"
    "function checkUnlocks(){\n"
    "  if(UNL_SEEN<0){ UNL_SEEN=PROG.score; return; }\n"
    "  var was=UNL_SEEN; UNL_SEEN=PROG.score;\n"
    "  if(PROG.score<=was) return;\n"
    "  function fell(o,label){\n"
    "    var pr=priceOf(o);\n"
    "    if(pr>was && pr<=PROG.score){\n"
    "      if(popN){ popN.textContent=label+' unlocked';\n"
    "                popP.textContent=o.name; popEl.className='on'; popT=2.4; }\n"
    "      chime(); buzz(46); saveProg();\n"
    "    }\n"
    "  }\n"
    "  for(var i=0;i<VEHICLES.length;i++) fell(VEHICLES[i],'Vehicle');\n"
    "  for(var m=0;m<MAPS.length;m++)     fell(MAPS[m],'Map');\n"
    "}\n"
    "\n"
    "function driftName(d){")

# the chain belongs in one place, not two
sub("  if(tallyC) tallyC.textContent=SK.chain>1?('x'+SK.chain):'';\n"
    "  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);",
    "  blip(430*Math.pow(1.055,SK.chain),0.10,'triangle',0.09);\n"
    "  checkUnlocks();")
sub("  FT.ramps={}; FT.rampN=0; FT.rimA=0; FT.rimLast=null;\n"
    "  if(tallyC) tallyC.textContent='';",
    "  FT.ramps={}; FT.rampN=0; FT.rimA=0; FT.rimLast=null;")

# ==================================================== 3. landmarks pay now
sub("      L.found=true; PROG.found[L.name]=1;\n"
    "      L.orb.visible=false; L.flag.visible=true;\n"
    "      chime(); buzz(28); saveProg();",
    "      L.found=true; PROG.found[L.name]=1;\n"
    "      L.orb.visible=false; L.flag.visible=true;\n"
    "      /* twelve of these paid nothing at all until now */\n"
    "      award('Found '+L.name, 340);\n"
    "      chime(); buzz(28); saveProg();")

# ================================================ 4. the garage shows a price
sub('    <button class="go" id="g-take">Drive this one</button>',
    '    <div class="glock" id="g-lock" hidden></div>\n'
    '    <button class="go" id="g-take">Drive this one</button>')

sub("  .keyhint{font-size:12px;color:var(--mute);margin:9px 0 0;line-height:1.4}",
    "  .keyhint{font-size:12px;color:var(--mute);margin:9px 0 0;line-height:1.4}\n"
    "  .glock{font-size:12px;color:var(--mute);line-height:1.45;margin:2px 0 9px;\n"
    "         padding:8px 10px;border-radius:8px;background:rgba(0,0,0,.16)}\n"
    "  .glock b{color:var(--ink);font-weight:700}\n"
    "  .go[disabled]{opacity:.42;pointer-events:none}\n"
    "  .nxt{font-size:12px;color:var(--mute);margin:10px 0 0;line-height:1.45}\n"
    "  .nxt b{color:var(--ink);font-weight:700}")

sub("  var d='';\n"
    "  for(var i=0;i<VEHICLES.length;i++) d+='<u class=\"'+(i===VEH?'on':'')+'\"></u>';\n"
    "  document.getElementById('g-dots').innerHTML=d;",
    "  var d='';\n"
    "  for(var i=0;i<VEHICLES.length;i++)\n"
    "    d+='<u class=\"'+(i===VEH?'on':(have(VEHICLES[i])?'':'off'))+'\"></u>';\n"
    "  document.getElementById('g-dots').innerHTML=d;\n"
    "  /* Show the price rather than hiding the car. You should be able to see what\n"
    "     you are driving towards. */\n"
    "  var lk=document.getElementById('g-lock'), tk=document.getElementById('g-take');\n"
    "  var ok=have(V);\n"
    "  if(lk){\n"
    "    lk.hidden=ok;\n"
    "    if(!ok) lk.innerHTML='Locked. <b>'+commas(priceOf(V))+'</b> points opens this one. '+\n"
    "                         'You have '+commas(PROG.score)+', so <b>'+\n"
    "                         commas(priceOf(V)-PROG.score)+'</b> to go.';\n"
    "  }\n"
    "  if(tk){ tk.disabled=!ok; tk.textContent=ok?'Drive this one':'Locked'; }")

# =============================================== 5. the label that was lying
sub('    <button class="go ghost" id="b-drift">Let it drift: off</button>\n', '')
sub('    <button class="go ghost" id="b-sound">Sound: on</button>',
    '    <button class="go ghost" id="b-drift">Light drifts: off</button>\n'
    '    <button class="go ghost" id="b-sound">Sound: on</button>')
sub("this.textContent='Let it drift: '+(TOD.drift?'on':'off');",
    "this.textContent='Light drifts: '+(TOD.drift?'on':'off');")

# =============================================== 6. a line saying what is next
sub('    <div id="segs"></div>',
    '    <div class="nxt" id="m-next"></div>\n'
    '    <div id="segs"></div>')
sub("  document.getElementById('m-odo').textContent=(PROG.odo/1000).toFixed(1)+' km';",
    "  var nx=nextUnlock(), nxE=document.getElementById('m-next');\n"
    "  if(nxE) nxE.innerHTML = nx\n"
    "    ? ('Next up: the '+nx.kind+' <b>'+nx.o.name+'</b> at '+commas(priceOf(nx.o))+\n"
    "       ' points. <b>'+commas(priceOf(nx.o)-PROG.score)+'</b> to go.')\n"
    "    : 'Everything is open. The rest is just driving it better.';\n"
    "  document.getElementById('m-odo').textContent=(PROG.odo/1000).toFixed(1)+' km';")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
