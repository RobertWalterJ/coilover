# -*- coding: utf-8 -*-
"""One handed mode.

The one pedal law with steering on the same thumb. Press anywhere in the lower
half, and from that point: up is throttle, down through the dead band is brake,
left and right is steer. One finger does everything, so the other hand can hold
the phone or a cup of tea.

Tilt steering was not the same thing and I should not have treated it as if it
were. Tilt still leaves you needing a thumb on the pedals and a hand steady
enough to aim the whole phone; this needs one thumb and nothing else.

Two decisions worth stating. The steering uses exactly the same curve as the
normal steering thumb, the same dead zone and the same 95 px lock, so the car
does not feel different in this mode, only the input does. And the touch origin
walks with you on a long turn, the same way the steering arc does, so you never
run out of thumb halfway through a corner.

The gauge grows a second axis: the fill and marker still read throttle and
brake vertically, and a bar now slides left and right for steer.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------------------------ the mode
sub("var PEDAL_NAMES=['two','one','arcade'];",
    "var PEDAL_NAMES=['two','one','arcade','one hand'];")

# a touch anywhere in the lower half is the whole control
sub("""    if(PEDAL_MODE!==1){
      var br=brakeEl.getBoundingClientRect();          /* brake sits inside the gas zone */
      if(x>br.left-12 && x<br.right+12 && y>br.top-12 && y<br.bottom+12) return 'brake';
    }
    return (x < innerWidth*0.50) ? 'steer' : 'gas';""",
"""    /* one handed: the whole lower half is the one control */
    if(PEDAL_MODE===3) return 'gas';
    if(PEDAL_MODE!==1){
      var br=brakeEl.getBoundingClientRect();          /* brake sits inside the gas zone */
      if(x>br.left-12 && x<br.right+12 && y>br.top-12 && y<br.bottom+12) return 'brake';
    }
    return (x < innerWidth*0.50) ? 'steer' : 'gas';""")

# --------------------------------------------------------------- the law
sub("""  var t0y=0;
  function down(e){""",
"""  /* One handed: the one pedal law on Y, the normal steering law on X, from a
     single origin. Same curve and same lock as the steering thumb, so the car
     behaves identically and only the input differs. */
  window.applyOneHand=function(dx,dy,t){
    applyOnePedal(dy);
    var m=Math.max(0,Math.abs(dx)-DEAD)/(LOCK-DEAD);
    IN.steer=(dx<0?-1:1)*Math.pow(Math.min(m,1),1.25);
    /* let the origin walk on a long turn, or you run out of thumb */
    if(t && Math.abs(dx)>LOCK) t.ox += (dx<0?-1:1)*0.8;
    var g=gasEl.querySelector('.gs');
    if(g) g.style.left=(50+IN.steer*46).toFixed(1)+'%';
  };

  var t0y=0;
  function down(e){""")

sub("""      if(PEDAL_MODE===2){ IN.gas=1; IN.brake=0; pedalGauge(gasEl,1,0,1,0,0,0); }
      else if(PEDAL_MODE===1){ applyOnePedal(0); }""",
"""      if(PEDAL_MODE===2){ IN.gas=1; IN.brake=0; pedalGauge(gasEl,1,0,1,0,0,0); }
      else if(PEDAL_MODE===3){
        applyOneHand(0,0,null);
        /* show the arc where the thumb landed, so the steering has a home */
        arcEl.style.left=arcDot.style.left=e.clientX+'px';
        arcEl.style.top =arcDot.style.top =e.clientY+'px';
        arcEl.classList.add('on'); arcDot.classList.add('on');
      }
      else if(PEDAL_MODE===1){ applyOnePedal(0); }""")

sub("""      if(PEDAL_MODE===2) return;                       /* arcade does not modulate */
      if(PEDAL_MODE===1){ applyOnePedal(e.clientY-t.oy); return; }""",
"""      if(PEDAL_MODE===2) return;                       /* arcade does not modulate */
      if(PEDAL_MODE===3){
        applyOneHand(e.clientX-t.ox, e.clientY-t.oy, t);
        arcEl.style.left=t.ox+'px';
        arcDot.style.left=(t.ox+IN.steer*58)+'px';
        return;
      }
      if(PEDAL_MODE===1){ applyOnePedal(e.clientY-t.oy); return; }""")

sub("""      IN.gas=0; if(PEDAL_MODE===1){ IN.brake=0; IN.revHold=0; }
      gasEl.classList.remove('on'); pedalClear(gasEl);""",
"""      IN.gas=0;
      if(PEDAL_MODE===1||PEDAL_MODE===3){ IN.brake=0; IN.revHold=0; }
      if(PEDAL_MODE===3){
        IN.steer=0;
        arcEl.classList.remove('on'); arcDot.classList.remove('on');
        var gsE=gasEl.querySelector('.gs'); if(gsE) gsE.style.left='50%';
      }
      gasEl.classList.remove('on'); pedalClear(gasEl);""")

# ---------------------------------------------------------------- the gauge
sub("""<span class="gd"></span><span class="gf"></span><span class="gz"></span><span class="gm"></span></button>""",
    """<span class="gd"></span><span class="gf"></span><span class="gz"></span><span class="gm"></span><span class="gs"></span></button>""")

sub("""  .gm{height:2px;top:0;opacity:0;background:rgba(255,246,232,.95);
      box-shadow:0 0 6px rgba(255,246,232,.55)}""",
"""  .gm{height:2px;top:0;opacity:0;background:rgba(255,246,232,.95);
      box-shadow:0 0 6px rgba(255,246,232,.55)}
  /* the second axis: a bar that slides for steer, one handed mode only */
  .gs{position:absolute;left:50%;top:14%;bottom:14%;width:3px;margin-left:-1.5px;
      border-radius:2px;background:rgba(255,246,232,.92);opacity:0;
      box-shadow:0 0 6px rgba(255,246,232,.5);transition:opacity .12s}
  #gas.hand.on .gs{opacity:1}""")

# the ring is sized and placed for a thumb in this mode too
sub("""  #gas.one{width:124px;height:124px;
           right:calc(22px + env(safe-area-inset-right));
           bottom:calc(104px + env(safe-area-inset-bottom))}""",
"""  #gas.one,#gas.hand{width:124px;height:124px;
           right:calc(22px + env(safe-area-inset-right));
           bottom:calc(104px + env(safe-area-inset-bottom))}""")
sub("    #gas.one{width:108px;height:108px;bottom:calc(88px + env(safe-area-inset-bottom))}",
    "    #gas.one,#gas.hand{width:108px;height:108px;bottom:calc(88px + env(safe-area-inset-bottom))}")
sub("""    #gas.one{width:92px;height:92px;
             right:calc(18px + env(safe-area-inset-right));
             bottom:calc(58px + env(safe-area-inset-bottom))}""",
"""    #gas.one,#gas.hand{width:92px;height:92px;
             right:calc(18px + env(safe-area-inset-right));
             bottom:calc(58px + env(safe-area-inset-bottom))}""")
sub("  #gas.one.on .gz{opacity:1}", "  #gas.one.on .gz,#gas.hand.on .gz{opacity:1}")
sub("  #gas.one.on .gd{opacity:1}", "  #gas.one.on .gd,#gas.hand.on .gd{opacity:1}")

# --------------------------------------------------------------- the switch
sub("""  gasEl.classList.toggle('one',m===1);
  gasEl.classList.toggle('two',m!==1);
  brakeEl.style.display=(m===1)?'none':'';""",
"""  gasEl.classList.toggle('one',m===1);
  gasEl.classList.toggle('hand',m===3);
  gasEl.classList.toggle('two',m!==1&&m!==3);
  brakeEl.style.display=(m===1||m===3)?'none':'';
  var gsE=gasEl.querySelector('.gs'); if(gsE) gsE.style.left='50%';""")
sub("  setPedalMode((PEDAL_MODE+1)%3);", "  setPedalMode((PEDAL_MODE+1)%PEDAL_NAMES.length);")
sub("  setPedalMode(Math.max(0,Math.min(2,m)));",
    "  setPedalMode(Math.max(0,Math.min(PEDAL_NAMES.length-1,m)));")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
