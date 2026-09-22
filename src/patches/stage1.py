# -*- coding: utf-8 -*-
"""Stage 1 of the gameplay audit: make the truck feel like a truck.

The headline bug: above 25 km/h the brake was ALSO a full handbrake. Rear grip
dropped from 0.92 to 0.34 while the service brake stayed at full, so every
attempt to slow down dumped the back end. That is a car you cannot stop, and it
is most of "the vehicle movements don't feel great".

Now the drift is a deliberate act: brake while turning past a threshold and the
back comes round, in proportion to how much lock you are carrying. Brake in a
straight line and it simply brakes.

Also here:
  Analogue throttle. Press for full, slide down to feather. Weight transfer is
  the whole pleasure of this vehicle and a binary button hid all of it.
  Air authority cut hard. Every landing was self levelling to flat, so the
  clean landing requirement was not a requirement and the ramp record collapsed
  to "how fast were you going". Landings can be got wrong again.
  The gate trigger was wider than the gate, so you could clear it by driving
  past the outside of a post. It now checks in the gate's own local space.
  The ramp stones reloaded on a bearing with no relationship to where you
  actually landed, so the one persistent physical record moved every time the
  game reopened. The landing position is saved now.
  Gate colour never reset after a full loop, so every gate was permanently lit.
  The last clock in the game, best airtime in seconds, becomes best jump in
  metres.
  Saves on pagehide, so a backgrounded phone stops losing the odometer.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- the brake
sub("""  /* One pedal, three jobs, chosen by what the truck is doing. Fast means you
     wanted the back end out. Stopped and still holding means you wanted to
     back up. Everything between is just the brake. */
  var sp=S.v.length();
  if(b>0){
    if(sp>6.9) h=1;
    else if(sp<0.9){
      IN.revHold+=dt;
      if(IN.revHold>0.35){ rev=1; b=0; }
    }
  }else IN.revHold=0;""",
"""  /* One pedal, three jobs, but the drift is now something you ASK for rather
     than something that happens every time you touch the brake. Brake while
     carrying lock and the back comes round in proportion. Brake straight and
     it just brakes. Stopped and still holding, it reverses. */
  var sp=S.v.length();
  if(b>0){
    var lock=Math.abs(S.steer);
    if(sp>6.9 && lock>0.34) h=Math.min(1,(lock-0.34)/0.34);
    else if(sp<0.9){
      IN.revHold+=dt;
      if(IN.revHold>0.35){ rev=1; b=0; }
    }
  }else IN.revHold=0;""")

# the handbrake is continuous now, so the tyre has to read it that way
sub("""    var hand=(!c2.front && S.hand>0.5);
    var muL=hand? MU_HAND : (c2.front?MU_LAT_F:MU_LAT_R);
    var Bc=hand?HAND_B:TYRE_B, Cc=hand?HAND_C:TYRE_C;""",
"""    var hb=c2.front?0:S.hand;
    var muBase=c2.front?MU_LAT_F:MU_LAT_R;
    var muL=muBase+(MU_HAND-muBase)*hb;
    var Bc=hb>0.35?HAND_B:TYRE_B, Cc=hb>0.35?HAND_C:TYRE_C;""")

# and shift the brake forward while the rear is loose, like a real handbrake
sub("""    var bf=MAX_BRAKE*(c2.front?BRAKE_BIAS_F:1-BRAKE_BIAS_F)*0.5*S.brake
         + (!c2.front? S.hand*4200 : 0);""",
"""    var bias=c2.front? BRAKE_BIAS_F+0.22*S.hand : (1-BRAKE_BIAS_F)*(1-0.75*S.hand);
    var bf=MAX_BRAKE*bias*0.5*S.brake + (!c2.front? S.hand*5200 : 0);""")

sub("  S.hand=h;", "  S.hand += (h-S.hand)*Math.min(1,dt*16);")

# ---------------------------------------------------------------- analogue throttle
sub("""    if(kind==='gas'){ IN.gas=1; gasEl.classList.add('on'); }""",
    """    if(kind==='gas'){ IN.gas=1; t0y=e.clientY; gasEl.classList.add('on'); }""")
sub("""  function move(e){
    var t=active.get(e.pointerId);
    if(!t || t.kind!=='steer') return;""",
"""  function move(e){
    var t=active.get(e.pointerId);
    if(t && t.kind==='gas'){
      /* Press for full, slide down to feather. Weight transfer is the whole
         pleasure of this truck and a binary button hid all of it. */
      IN.gas=Math.max(0.12,Math.min(1,1-(e.clientY-t.oy)/95));
      return;
    }
    if(!t || t.kind!=='steer') return;""")
sub("    active.set(e.pointerId,{kind:kind,ox:e.clientX});",
    "    active.set(e.pointerId,{kind:kind,ox:e.clientX,oy:e.clientY});")
sub("  function down(e){\n    var kind=zoneAt(e.clientX,e.clientY,e.target);",
    "  var t0y=0;\n  function down(e){\n    var kind=zoneAt(e.clientX,e.clientY,e.target);")

# ---------------------------------------------------------------- air
sub("    var auth=0.34+0.66*Math.max(0,1-tImp/0.95);",
    """    /* Barely there through the flight, a firm hand only right at the ground.
       At the old floor every landing self levelled, so a clean landing was not
       something you could fail and the ramp record was just a speed record. */
    var auth=0.11+0.72*Math.max(0,1-tImp/0.85);""")
sub("      if(flat>0.80){", "      if(flat>0.88){")

# ---------------------------------------------------------------- gates
sub("""  var d=Math.hypot(S.p.x-gt.x,S.p.z-gt.z);
  if(d<8.5 && Math.abs(S.p.y-gt.y)<7){""",
"""  /* Check in the gate's own frame, so you have to go BETWEEN the posts. The
     old radius test was wider than the gate itself. */
  _v3.copy(S.p); gt.g.worldToLocal(_v3);
  if(Math.abs(_v3.x)<4.0 && Math.abs(_v3.z)<3.4 && Math.abs(_v3.y)<6){""")

sub("""    var all=GATES.every(function(x){return x.done;});
    if(all){ GATES.forEach(function(x){x.done=false;}); flash('Loop complete','all twelve, going round again'); }
    else flash('Gate '+S.gates,'next one is lit');
    chime(); buzz(25);""",
"""    var all=GATES.every(function(x){return x.done;});
    if(all) GATES.forEach(function(x){
      x.done=false;
      /* the bars have to go back to red or every gate reads as done forever */
      x.g.children.forEach(function(ch){
        if(ch.userData.baseHex!==undefined) ch.material.color.setHex(ch.userData.baseHex);
      });
    });
    PROG.gates=(PROG.gates||0)+1; saveProg();
    chime(); buzz(25);""")

sub("""    gt.g.children.forEach(function(ch){
      if(ch===gt.beam || !ch.material || !ch.material.color) return;
      ch.material=ch.material.clone();
      ch.material.color.setHex(0x2bc4b0);
    });""",
"""    gt.g.children.forEach(function(ch){
      if(ch===gt.beam || !ch.material || !ch.material.color) return;
      if(ch.userData.baseHex===undefined){
        ch.material=ch.material.clone();
        ch.userData.baseHex=ch.material.color.getHex();
      }
      ch.material.color.setHex(0x2bc4b0);
    });""")

# make the next gate readable against a bright sky
sub("    if(gt.beam.visible) gt.beam.material.opacity=(0.07+0.05*Math.sin(performance.now()*0.0026))*(1+TOD.night*1.6);",
    "    if(gt.beam.visible) gt.beam.material.opacity=(0.20+0.10*Math.sin(performance.now()*0.0026))*(1+TOD.night*1.2);")

# ---------------------------------------------------------------- stones
sub("""            PROG.jump[ki]=dist; setStone(ki,S.p.x,S.p.z);
            chime(); buzz(30); saveProg();""",
"""            PROG.jump[ki]=dist;
            PROG.jumpAt[ki]=[S.p.x,S.p.z];
            /* Put it to the side of the line rather than under the wheels, so
               it rises into peripheral vision as you drive away from it. */
            _v3.copy(S.v).setY(0).normalize();
            setStone(ki, S.p.x - _v3.z*9, S.p.z + _v3.x*9);
            chime(); buzz(30); saveProg();""")

sub("""for(var _si=0;_si<3;_si++){
  if(PROG.jump[_si]>0){
    var _kk=KICKERS[_si], _d=PROG.jump[_si];
    setStone(_si,_kk.x+Math.cos(_si*2.1)*_d,_kk.z+Math.sin(_si*2.1)*_d);
  }
}""",
"""for(var _si=0;_si<3;_si++){
  /* restore where it actually landed, not on an invented bearing */
  if(PROG.jump[_si]>0 && PROG.jumpAt[_si]) setStone(_si,PROG.jumpAt[_si][0],PROG.jumpAt[_si][1]);
}""")

sub("var PROG={ odo:0, air:0, found:{}, jump:[0,0,0], mapv:new Uint8Array(MAPN*MAPN) };",
    "var PROG={ odo:0, air:0, gates:0, found:{}, jump:[0,0,0], jumpAt:[null,null,null],\n           mapv:new Uint8Array(MAPN*MAPN) };")
sub("""    PROG.jump=o.jump||[0,0,0];""",
    """    PROG.jump=o.jump||[0,0,0];
    PROG.jumpAt=o.jumpAt||[null,null,null];
    PROG.gates=o.gates||0;""")
sub("""      odo:PROG.odo, air:PROG.air, found:PROG.found, jump:PROG.jump, map:btoa(str)}));""",
    """      odo:PROG.odo, air:PROG.air, gates:PROG.gates, found:PROG.found,
      jump:PROG.jump, jumpAt:PROG.jumpAt, map:btoa(str)}));""")

# ---------------------------------------------------------------- the last clock
sub("""      <div><div class="lbl">Best air</div><div class="num" id="m-air">0.0s</div></div>""",
    """      <div><div class="lbl">Best jump</div><div class="num" id="m-air">0 m</div></div>""")
sub("""  document.getElementById('m-air').textContent=Math.max(S.bestAir,PROG.air).toFixed(1)+'s';""",
    """  /* metres, not seconds. A duration presented as a record is a stopwatch. */
  document.getElementById('m-air').textContent=Math.round(Math.max.apply(null,PROG.jump))+' m';""")

# ---------------------------------------------------------------- saving
sub("""loadProg();""",
"""loadProg();
/* a backgrounded phone was losing up to eight seconds of odometer */
addEventListener('pagehide',function(){ saveProg(); });
document.addEventListener('visibilitychange',function(){ if(document.hidden) saveProg(); });""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
