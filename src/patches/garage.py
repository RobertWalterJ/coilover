# -*- coding: utf-8 -*-
"""The garage.

A real 360, not a preview render: the car sits on the salt in the actual world
under the actual light, and the camera orbits it. So what you are looking at is
exactly what you will be driving, at whatever time of day you have chosen.

The three bars are computed from the same numbers the solver reads, so they
cannot drift out of step with how the car behaves. No figures, no stars, no
percentages, and nothing counting.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------------------------------- markup
sub("""<div class="sheet" id="nogl" hidden>""",
"""<div class="sheet" id="garage" hidden>
  <div class="card">
    <div class="gname" id="g-name">Bracken</div>
    <div class="gkind" id="g-kind">Utility 4x4</div>
    <div class="rule"></div>
    <div class="bars">
      <div><span>Power</span><i><b id="g-pow"></b></i></div>
      <div><span>Grip</span><i><b id="g-grip"></b></i></div>
      <div><span>Travel</span><i><b id="g-trav"></b></i></div>
    </div>
    <div class="gnav">
      <button class="go ghost gprev" id="g-prev" aria-label="Previous vehicle">&lt;</button>
      <div class="gdots" id="g-dots"></div>
      <button class="go ghost gnext" id="g-next" aria-label="Next vehicle">&gt;</button>
    </div>
    <button class="go" id="g-take">Drive this one</button>
  </div>
</div>

<div class="sheet" id="nogl" hidden>""")

sub("""    <button class="go ghost" id="b-pedal">Pedals: two</button>""",
    """    <button class="go ghost" id="b-pedal">Pedals: two</button>
    <button class="go ghost" id="b-garage">Garage</button>""")

# ---------------------------------------------------------------------- css
sub("""  #segs{margin:9px 0 0;display:flex;flex-direction:column;gap:5px}""",
"""  /* the garage card sits low so the car itself owns the middle of the screen */
  #garage{align-items:flex-end;background:linear-gradient(to top,rgba(12,7,14,.86),transparent 62%)}
  #garage .card{max-width:360px;margin-bottom:6px}
  .gname{font-weight:700;font-size:34px;line-height:.95;text-transform:uppercase;
         letter-spacing:.01em;color:var(--cream)}
  .gkind{font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.16em;
         color:var(--mute);margin-top:5px}
  .bars{display:flex;flex-direction:column;gap:7px;margin:2px 0 12px}
  .bars div{display:flex;align-items:center;gap:10px}
  .bars span{flex:0 0 58px;font-weight:600;font-size:10px;text-transform:uppercase;
             letter-spacing:.14em;color:var(--mute)}
  .bars i{flex:1;height:6px;border-radius:3px;background:#2c2233;display:block;overflow:hidden}
  .bars b{display:block;height:100%;background:var(--amber);border-radius:3px;
          transition:width .22s}
  .gnav{display:flex;align-items:center;gap:10px;margin-bottom:2px}
  .gprev,.gnext{flex:0 0 54px;margin-top:0;padding:13px 0;font-size:18px}
  .gdots{flex:1;display:flex;justify-content:center;gap:7px}
  .gdots u{width:7px;height:7px;border-radius:50%;background:#4a3c50;display:block}
  .gdots u.on{background:var(--amber)}
  #segs{margin:9px 0 0;display:flex;flex-direction:column;gap:5px}""")

# ------------------------------------------------------------------- orbit
sub("""function updateCam(dt){
  var speed=S.v.length();""",
"""var GARAGE={on:false, ang:0.6};
function updateCam(dt){
  if(GARAGE.on){
    /* a slow orbit of the real car in the real world, so what you choose is
       what you get, under whatever light you have set */
    GARAGE.ang+=dt*0.34;
    var R=8.4, hh=2.1;
    camera.position.set(S.p.x+Math.sin(GARAGE.ang)*R, S.p.y+hh, S.p.z+Math.cos(GARAGE.ang)*R);
    camLook.lerp(_v3.copy(S.p).setY(S.p.y-0.10),Math.min(1,dt*8));
    camera.up.set(0,1,0);
    camera.fov=36; camera.updateProjectionMatrix();
    camera.lookAt(camLook);
    return;
  }
  var speed=S.v.length();""")

# ----------------------------------------------------------------- the card
sub("""document.getElementById('b-tilt').addEventListener('click',function(){""",
"""/* Bars come straight off the spec, so they can never disagree with the car. */
function garageCard(){
  var V=VEHICLES[VEH];
  document.getElementById('g-name').textContent=V.name;
  document.getElementById('g-kind').textContent=V.kind;
  function pct(v,lo,hi){ return Math.round(Math.max(0.08,Math.min(1,(v-lo)/(hi-lo)))*100)+'%'; }
  document.getElementById('g-pow').style.width =pct(V.drive,20000,30500);
  document.getElementById('g-grip').style.width=pct((V.muF+V.muR)/2,0.93,1.07);
  document.getElementById('g-trav').style.width=pct(V.susMax-V.susMin,0.48,0.90);
  var d='';
  for(var i=0;i<VEHICLES.length;i++) d+='<u class="'+(i===VEH?'on':'')+'"></u>';
  document.getElementById('g-dots').innerHTML=d;
}
function pickVehicle(i){
  i=(i+VEHICLES.length)%VEHICLES.length;
  window.__setVehicle(i);
  try{ localStorage.setItem('coilover.veh',String(i)); }catch(_){}
  garageCard();
}
function openGarage(){
  show('menu',false);
  /* park it on the flat salt so the car sits level for the turntable */
  placeTruck(-96,96,0.0);
  S.v.set(0,0,0); S.w.set(0,0,0);
  IN.gas=IN.brake=IN.steer=0;
  GARAGE.on=true; GARAGE.ang=0.6;
  garageCard();
  show('garage',true);
}
function closeGarage(){
  GARAGE.on=false;
  camera.fov=54; camera.updateProjectionMatrix();
  show('garage',false);
  placeTruck(0,0,0.4);
  S.running=true; last=performance.now(); acc=0;
}
document.getElementById('b-garage').addEventListener('click',openGarage);
document.getElementById('g-prev').addEventListener('click',function(){ pickVehicle(VEH-1); });
document.getElementById('g-next').addEventListener('click',function(){ pickVehicle(VEH+1); });
document.getElementById('g-take').addEventListener('click',closeGarage);

document.getElementById('b-tilt').addEventListener('click',function(){""")

# ------------------------------------------------- boot with the saved choice
sub("""(function(){
  var m=0; try{ m=parseInt(localStorage.getItem('coilover.pedal')||'0',10)||0; }catch(_){}
  setPedalMode(Math.max(0,Math.min(2,m)));
})();""",
"""(function(){
  var m=0; try{ m=parseInt(localStorage.getItem('coilover.pedal')||'0',10)||0; }catch(_){}
  setPedalMode(Math.max(0,Math.min(2,m)));
  var v=0; try{ v=parseInt(localStorage.getItem('coilover.veh')||'0',10)||0; }catch(_){}
  window.__setVehicle(Math.max(0,Math.min(VEHICLES.length-1,v)));
  garageCard();
})();""")

# -------------------------------------------------------------- debug export
sub("""    getPost:function(){return POST;},STYLE_U:STYLE_U,PAL:PAL,""",
    """    getPost:function(){return POST;},STYLE_U:STYLE_U,PAL:PAL,
    VEHICLES:VEHICLES, setVehicle:function(i){return window.__setVehicle(i);},
    getVeh:function(){return VEH;}, GARAGE:GARAGE,""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
