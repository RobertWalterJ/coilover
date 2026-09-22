# -*- coding: utf-8 -*-
"""Strip the HUD down to three things.

Two independent reviews landed on the same answer, and it matches what you saw
on screen. This game has no fail state, no resource, no opponent and no clock,
so nothing on screen can prevent a loss. Every element was either an input
surface or commentary, and the world tells the commentary better.

Persistent: a gas ring, a brake ring, a menu dot. Steering is an invisible
surface that draws an arc under your thumb only while you are touching it.
Speed, the strut bars, the gate counter, best air, the chevron, the distance
and the toasts are all gone. The world carries them instead: field of view and
engine pitch for speed, the truck's own springs for load, and a slowly turning
dust column standing over every gate you have not collected yet.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

def block(start, end):
    a = s.index(start); b = s.index(end)
    return s[a:b]

# ============================== CSS ==============================
old_css = block("  .lbl{font-weight:600;text-transform:uppercase", "  /* ---- sheets ---- */")
new_css = '''  .lbl{font-weight:600;text-transform:uppercase;letter-spacing:.15em;font-size:10px;
       color:var(--mute);line-height:1}
  .num{font-family:"Azeret Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums;
       font-weight:700;color:var(--cream);line-height:1}

  #hud{position:fixed;inset:0;pointer-events:none}

  /* the only permanent mark on the screen that is not a pedal */
  #b-menu{position:absolute;top:calc(9px + env(safe-area-inset-top));
          right:calc(9px + env(safe-area-inset-right));
          width:40px;height:40px;border:0;background:none;padding:0;
          pointer-events:auto;cursor:pointer}
  #b-menu::after{content:"";position:absolute;left:50%;top:50%;width:8px;height:8px;
                 margin:-4px 0 0 -4px;border-radius:50%;background:rgba(244,235,221,.40)}
  #b-menu:focus-visible{outline:2px solid var(--amber);outline-offset:2px;border-radius:50%}

  /* Pedals are absolute targets, so they need a fixed home the thumb can find
     without looking. Fixed does not mean loud: outline only, no words. */
  .ring{position:absolute;border-radius:50%;background:transparent;padding:0;
        border:2px solid rgba(244,235,221,.26);pointer-events:auto;cursor:pointer;
        transition:border-color .09s,background .09s,transform .09s}
  .ring:focus-visible{outline:2px solid var(--amber);outline-offset:3px}
  #gas{width:100px;height:100px;
       right:calc(26px + env(safe-area-inset-right));
       bottom:calc(34px + env(safe-area-inset-bottom))}
  #brake{width:66px;height:66px;
         right:calc(142px + env(safe-area-inset-right));
         bottom:calc(24px + env(safe-area-inset-bottom))}
  .ring.on{border-color:rgba(244,235,221,.78);background:rgba(244,235,221,.12);transform:scale(.965)}
  #brake.slide{border-color:rgba(255,180,84,.85)}
  #hud.idle .ring{border-color:rgba(244,235,221,.14)}

  /* steering draws nothing until a thumb lands, then an arc under it */
  #arc,#arcdot{position:fixed;border-radius:50%;pointer-events:none;opacity:0;
               transition:opacity .18s}
  #arc{width:132px;height:132px;margin:-66px 0 0 -66px;border:2px solid rgba(244,235,221,.42)}
  #arcdot{width:15px;height:15px;margin:-7.5px 0 0 -7.5px;background:rgba(244,235,221,.85)}
  #arc.on,#arcdot.on{opacity:1}

  /* a scrim so anything drawn over a bright sky still reads */
  #scrim{position:absolute;inset:0;pointer-events:none;
         background:linear-gradient(to bottom,rgba(30,16,8,.30),transparent 130px),
                    linear-gradient(to top,rgba(30,16,8,.34),transparent 150px)}

'''
s = s.replace(old_css, new_css, 1); n += 1

# ============================== markup ==============================
old_hud = block('<div id="hud">', '<div class="sheet" id="intro">')
new_hud = '''<div id="hud">
  <div id="scrim"></div>
  <button id="b-menu" aria-label="Menu"></button>
  <button class="ring" id="brake" aria-label="Brake"></button>
  <button class="ring" id="gas" aria-label="Gas"></button>
</div>
<div id="arc"></div><div id="arcdot"></div>

'''
s = s.replace(old_hud, new_hud, 1); n += 1

# intro and pause, rewritten with almost no words
sub('''    <h1>Coil<em>over</em></h1>
    <div class="rule"></div>
    <p>A desert basin, a big truck, and 70 cm of suspension you can watch working. Hit the whoops flat out and the springs do the rest.</p>
    <div class="hint"><b>Left pad</b><span>Slide your thumb to steer. It springs back straight.</span></div>
    <div class="hint"><b>Right</b><span>Gas and brake. In the air, gas lifts the nose, brake drops it.</span></div>
    <div class="hint"><b>Hand</b><span>Handbrake. Lets the back end go.</span></div>
    <p style="color:#a99ba5;font-size:14px;margin-top:13px">Twelve gates out there if you want a route. No clock, nothing is chasing you.</p>
    <button class="go" id="b-start">Fire it up</button>''',
'''    <h1>Coil<em>over</em></h1>
    <div class="rule"></div>
    <p>Right side drives. Left side steers.</p>
    <button class="go" id="b-start">Drive</button>''')

sub('''    <h1>Parked</h1>
    <div class="rule"></div>
    <div class="tally3">
      <div><div class="lbl">Gates</div><div class="num" id="m-gates">0</div></div>
      <div><div class="lbl">Best air</div><div class="num" id="m-air">0.0s</div></div>
      <div><div class="lbl">Longest</div><div class="num" id="m-dist">0m</div></div>
    </div>
    <button class="go" id="b-resume">Back in it</button>
    <button class="go ghost" id="b-flip">Set the truck upright</button>
    <button class="go ghost" id="b-sound">Sound: on</button>
    <button class="go ghost" id="b-tilt">Tilt steering: off</button>''',
'''    <h1>Parked</h1>
    <div class="rule"></div>
    <div class="tally3">
      <div><div class="lbl">Gates</div><div class="num" id="m-gates">0</div></div>
      <div><div class="lbl">Best air</div><div class="num" id="m-air">0.0s</div></div>
      <div><div class="lbl">Longest</div><div class="num" id="m-dist">0m</div></div>
    </div>
    <button class="go" id="b-resume">Drive</button>
    <button class="go ghost" id="b-flip">Upright the truck</button>
    <button class="go ghost" id="b-cam">Camera</button>
    <button class="go ghost" id="b-sound">Sound: on</button>
    <button class="go ghost" id="b-tilt">Tilt steering: off</button>''')

# ============================== hud() ==============================
old_fn = block("var elK=document.getElementById('kmh')", "var toast=document.getElementById('toast')")
new_fn = '''var hudEl=document.getElementById('hud');
var arcEl=document.getElementById('arc'), arcDot=document.getElementById('arcdot');
var idleT=0;

function hud(dt){
  /* Everything that used to be drawn here now happens in the world. The only
     job left is letting the pedals fade back while nobody is touching them,
     and bringing them back the moment a thumb lands or the truck stops. */
  if(IN.gas||IN.brake||IN.steer!==0){ idleT=0; }
  else idleT+=dt;
  var slow=S.v.lengthSq()<4;
  hudEl.classList.toggle('idle', idleT>4 && !slow);
}

'''
s = s.replace(old_fn, new_fn, 1); n += 1

# flash() had a toast to drive; the world does this now
sub('''var toast=document.getElementById('toast'), toastT=0;
function flash(b,s){
  document.getElementById('toastb').textContent=b;
  document.getElementById('toasts').textContent=s;
  toast.className='on'; toastT=1.6;
}''',
'''var toastT=0;
/* kept as a seam: the events are real, the announcement is not */
function flash(){}''')

sub("  if(toastT>0){ toastT-=dt; if(toastT<=0) toast.className=''; }\n", "")
sub("    checkGates();\n    stepDust(dt);\n    hud(); audioTick();",
    "    checkGates();\n    stepDust(dt);\n    hud(dt); audioTick();")
sub("sync(0); updateCam(0.016); hud();", "sync(0); updateCam(0.016); hud(0);")

# ============================== steer arc ==============================
sub("""  function down(e){
    var kind=zoneAt(e.clientX,e.clientY,e.target);
    if(!kind) return;
    e.preventDefault();
    audioOn();""",
"""  function down(e){
    var kind=zoneAt(e.clientX,e.clientY,e.target);
    if(!kind) return;
    e.preventDefault();
    audioOn();
    if(kind==='steer'){
      arcEl.style.left=arcDot.style.left=e.clientX+'px';
      arcEl.style.top =arcDot.style.top =e.clientY+'px';
      arcEl.classList.add('on'); arcDot.classList.add('on');
    }""")

sub("""    if(Math.abs(d)>LOCK) t.ox += (d<0?-1:1)*0.8;       /* let the origin walk with a long turn */
    snub.style.transform='translateX('+(IN.steer*((steerEl.clientWidth/2)-38))+'px)';""",
"""    if(Math.abs(d)>LOCK) t.ox += (d<0?-1:1)*0.8;       /* let the origin walk with a long turn */
    arcEl.style.left=t.ox+'px';
    arcDot.style.left=(t.ox+IN.steer*62)+'px';""")

sub("    if(t.kind==='steer'){ IN.steer=0; snub.style.transform=''; }",
    "    if(t.kind==='steer'){ IN.steer=0; arcEl.classList.remove('on'); arcDot.classList.remove('on'); }")

sub("""    active.clear(); IN.gas=IN.brake=IN.steer=IN.hand=0; IN.revHold=0;
    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    snub.style.transform='';""",
"""    active.clear(); IN.gas=IN.brake=IN.steer=IN.hand=0; IN.revHold=0;
    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    arcEl.classList.remove('on'); arcDot.classList.remove('on');""")

sub("""var gasEl=document.getElementById('gas'), brakeEl=document.getElementById('brake');
var steerEl=document.getElementById('steer'), snub=document.getElementById('snub');""",
    """var gasEl=document.getElementById('gas'), brakeEl=document.getElementById('brake');""")

# camera moves to a double tap up top, and to the pause menu
sub("""    if(y < innerHeight*0.50) return null;              /* the top half is scenery */""",
    """    if(y < innerHeight*0.50){ tapUpper(x,y); return null; }   /* the top half is scenery */""")

sub("""(function(){
  var LOCK=120, DEAD=5;
  var active=new Map();""",
"""var _tapT=0;
function tapUpper(){
  /* double tap the sky to change camera, so the button can go */
  var now=performance.now();
  if(now-_tapT<330){ cycleCam(); _tapT=0; } else _tapT=now;
}

(function(){
  var LOCK=120, DEAD=5;
  var active=new Map();""")

sub("""function cycleCam(){ S.camMode=(S.camMode+1)%3; document.getElementById('b-cam').textContent=CAMS[S.camMode]; }
document.getElementById('b-cam').addEventListener('click',cycleCam);""",
    """function cycleCam(){ S.camMode=(S.camMode+1)%3; }
document.getElementById('b-cam').addEventListener('click',cycleCam);""")
sub("S.camMode=0; document.getElementById('b-cam').textContent=CAMS[0];\n", "S.camMode=0;\n")
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
