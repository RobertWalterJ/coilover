# -*- coding: utf-8 -*-
"""Control rewrite.

Three problems with the first pass. The steering pad was a small rectangle, so
a thumb in motion left it constantly. Full lock at 72 px was far too twitchy for
a truck meant to slide. And a separate handbrake button asked the left thumb to
abandon steering at exactly the moment steering matters most.

Now: the lower half of the screen is two invisible zones, left steers and right
drives. Pointer capture keeps a wandering thumb attached to whatever it grabbed.
Full lock at 120 px through a soft centred curve. The brake reads the situation
and becomes a slide above 25 km/h and reverse when stopped, so there are only
ever two things to touch.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:80].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- markup
sub("""    <div id="leftctl">
      <button class="pedal" id="hand">Hand</button>
      <div id="steer">""",
    """    <div id="leftctl">
      <div id="steer">""")

# ---------------------------------------------------------------- css
sub("""  #hand{width:64px;height:44px;border-radius:3px;font-size:11px;letter-spacing:.08em}
  #hand.on{border-color:var(--amber);background:#5a3d15;transform:scale(.97)}
""", "")

sub("""#brake.on{border-color:var(--hot);background:radial-gradient(circle at 50% 38%,#6e2419,#33110c);
            transform:scale(.97)}""",
    """#brake.on{border-color:var(--hot);background:radial-gradient(circle at 50% 38%,#6e2419,#33110c);
            transform:scale(.97)}
  #brake.slide{border-color:var(--amber)}""")

# ---------------------------------------------------------------- input
old_input = s[s.index("function hold(el,onFn,offFn){"):s.index("/* optional tilt steering */")]
new_input = '''var IN={gas:0,brake:0,hand:0,steer:0,revHold:0};
var gasEl=document.getElementById('gas'), brakeEl=document.getElementById('brake');
var steerEl=document.getElementById('steer'), snub=document.getElementById('snub');

function buzz(pattern){
  /* Android honours this, iOS Safari does not. Never the only signal. */
  if(!S.haptics || !('vibrate' in navigator)) return;
  try{ navigator.vibrate(pattern); }catch(_){}
}

(function(){
  var LOCK=120, DEAD=5;
  var active=new Map();

  function zoneAt(x,y,target){
    if(!S.running) return null;
    if(target && target.closest && target.closest('.sheet,.btn')) return null;
    if(y < innerHeight*0.50) return null;              /* the top half is scenery */
    var br=brakeEl.getBoundingClientRect();            /* brake sits inside the gas zone */
    if(x>br.left-12 && x<br.right+12 && y>br.top-12 && y<br.bottom+12) return 'brake';
    return (x < innerWidth*0.50) ? 'steer' : 'gas';
  }

  function down(e){
    var kind=zoneAt(e.clientX,e.clientY,e.target);
    if(!kind) return;
    e.preventDefault();
    audioOn();
    try{ (e.target.setPointerCapture?e.target:document.body).setPointerCapture(e.pointerId); }catch(_){}
    active.set(e.pointerId,{kind:kind,ox:e.clientX});
    if(kind==='gas'){ IN.gas=1; gasEl.classList.add('on'); }
    if(kind==='brake'){ IN.brake=1; IN.revHold=0; brakeEl.classList.add('on'); }
  }

  function move(e){
    var t=active.get(e.pointerId);
    if(!t || t.kind!=='steer') return;
    var d=e.clientX-t.ox;
    var m=Math.max(0,Math.abs(d)-DEAD)/(LOCK-DEAD);
    /* soft in the middle for holding a line, fast at the edge for catching a slide */
    IN.steer=(d<0?-1:1)*Math.pow(Math.min(m,1),1.6);
    if(Math.abs(d)>LOCK) t.ox += (d<0?-1:1)*0.8;       /* let the origin walk with a long turn */
    snub.style.transform='translateX('+(IN.steer*((steerEl.clientWidth/2)-38))+'px)';
  }

  function up(e){
    var t=active.get(e.pointerId);
    if(!t) return;
    active.delete(e.pointerId);
    if(t.kind==='steer'){ IN.steer=0; snub.style.transform=''; }
    if(t.kind==='gas'){ IN.gas=0; gasEl.classList.remove('on'); }
    if(t.kind==='brake'){ IN.brake=0; IN.revHold=0; brakeEl.classList.remove('on'); }
  }

  addEventListener('pointerdown',down,{passive:false});
  addEventListener('pointermove',move);
  addEventListener('pointerup',up);
  addEventListener('pointercancel',up);
  document.addEventListener('visibilitychange',function(){
    if(!document.hidden) return;
    active.clear(); IN.gas=IN.brake=IN.steer=IN.hand=0; IN.revHold=0;
    gasEl.classList.remove('on'); brakeEl.classList.remove('on','slide');
    snub.style.transform='';
  });
})();

'''
s = s.replace(old_input, new_input, 1); n += 1

# ---------------------------------------------------------------- readInput
sub("""function readInput(dt){
  var s=IN.steer, g=IN.gas, b=IN.brake, h=IN.hand;
  if(keys['a']||keys['arrowleft']) s=-1;
  if(keys['d']||keys['arrowright']) s=1;
  if(keys['w']||keys['arrowup']) g=1;
  if(keys['s']||keys['arrowdown']) b=1;
  if(keys[' ']) h=1;
  if(S.tilt && Math.abs(tiltVal)>0.04 && IN.steer===0) s=tiltVal;
  /* ease the rack so a flicked thumb does not snap the wheels */
  S.steer += (s-S.steer)*Math.min(1,dt*11);
  S.throttle += (g-S.throttle)*Math.min(1,dt*13);
  S.brake += (b-S.brake)*Math.min(1,dt*18);
  S.hand=h;
}""",
"""function readInput(dt){
  var s=IN.steer, g=IN.gas, b=IN.brake, h=0, rev=0;
  if(keys['a']||keys['arrowleft']) s=-1;
  if(keys['d']||keys['arrowright']) s=1;
  if(keys['w']||keys['arrowup']) g=1;
  if(keys['s']||keys['arrowdown']) b=1;
  if(keys[' ']) h=1;
  if(S.tilt && Math.abs(tiltVal)>0.04 && IN.steer===0) s=tiltVal;

  /* One pedal, three jobs, chosen by what the truck is doing. Fast means you
     wanted the back end out. Stopped and still holding means you wanted to
     back up. Everything between is just the brake. */
  var sp=S.v.length();
  if(b>0){
    if(sp>6.9) h=1;
    else if(sp<0.9){
      IN.revHold+=dt;
      if(IN.revHold>0.35){ rev=1; b=0; }
    }
  }else IN.revHold=0;
  brakeEl.classList.toggle('slide', h>0 && IN.brake>0);

  /* ease the rack so a flicked thumb does not snap the wheels */
  S.steer += (s-S.steer)*Math.min(1,dt*11);
  S.throttle += (g-S.throttle)*Math.min(1,dt*13);
  S.brake += (b-S.brake)*Math.min(1,dt*18);
  S.rev += (rev-S.rev)*Math.min(1,dt*8);
  S.hand=h;
}""")

# reverse needs a term in the drive force
sub("    if(!c2.front) Flong += S.throttle*MAX_DRIVE*0.5*Math.max(0,1-speed/40);",
    "    if(!c2.front) Flong += (S.throttle-S.rev*0.52)*MAX_DRIVE*0.5*Math.max(0,1-speed/40);")

sub("  steer:0, throttle:0, brake:0, hand:0,",
    "  steer:0, throttle:0, brake:0, hand:0, rev:0, haptics:true, dip:0,")

# ---------------------------------------------------------------- feel
# a short camera drop on landing is the cheapest satisfying thing there is
sub("""      S.shake=Math.min(1,S.airT*0.5);
      thump(Math.min(1,S.airT*0.6));""",
    """      S.shake=Math.min(1,S.airT*0.5);
      S.dip=Math.min(1,S.airT*0.7);
      thump(Math.min(1,S.airT*0.6));
      buzz(Math.round(12+Math.min(28,S.airT*22)));""")

sub("""  if(S.shake>0){
    S.shake=Math.max(0,S.shake-dt*2.4);
    camera.position.x+=(Math.random()-0.5)*S.shake*0.5;
    camera.position.y+=(Math.random()-0.5)*S.shake*0.5;
  }""",
    """  if(S.dip>0){                    /* the camera squats on impact, then recovers */
    S.dip=Math.max(0,S.dip-dt*3.6);
    camera.position.y-=S.dip*0.85;
  }
  if(S.shake>0){
    /* translation only. Rotating a phone held near the face is nauseating. */
    S.shake=Math.max(0,S.shake-dt*2.4);
    camera.position.x+=(Math.random()-0.5)*S.shake*0.4;
    camera.position.y+=(Math.random()-0.5)*S.shake*0.4;
  }""")

sub("    chime();", "    chime(); buzz(25);")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
