# -*- coding: utf-8 -*-
"""Wire the world up: discovery, the odometer, the map, the moving stones.

Everything here obeys one rule. Show what has been found, never what is
missing. There is no count of remaining landmarks, no percentage, no badge on
the menu telling you there is unfinished business. The map fills in, the flags
go up, the stones walk out, and that is the whole ledger.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:90].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---------------------------------------------------------------- landing
sub("""    if(S.airT>0.45){
      var dist=Math.hypot(S.p.x-S.airFrom.x,S.p.z-S.airFrom.z);
      if(S.airT>S.bestAir){ S.bestAir=S.airT; }
      if(dist>S.bestDist) S.bestDist=dist;""",
"""    if(S.airT>0.45){
      var dist=Math.hypot(S.p.x-S.airFrom.x,S.p.z-S.airFrom.z);
      if(S.airT>S.bestAir){ S.bestAir=S.airT; }
      if(S.airT>PROG.air){ PROG.air=S.airT; }
      if(dist>S.bestDist) S.bestDist=dist;

      /* Landed flat, off a ramp, further than before? The stones move out to
         the new spot behind you. This is the only record the game keeps that
         you can actually see from the driver's seat. */
      if(_bup.y>0.90){
        for(var ki=0;ki<3;ki++){
          var kdx=KICKERS[ki].x-S.airFrom.x, kdz=KICKERS[ki].z-S.airFrom.z;
          if(Math.hypot(kdx,kdz)<36 && dist>PROG.jump[ki]+0.4){
            PROG.jump[ki]=dist; setStone(ki,S.p.x,S.p.z);
            chime(); buzz(30); saveProg();
          }
        }
      }""")

# ---------------------------------------------------------------- discovery
sub("""/* ================= camera ================= */""",
"""/* ================= discovery ================= */
function checkLandmarks(){
  for(var i=0;i<LANDMARKS.length;i++){
    var L=LANDMARKS[i];
    if(L.found) continue;
    if(PROG.found[L.name]){                       /* restored from a past drive */
      L.found=true; L.orb.visible=false; L.flag.visible=true; continue;
    }
    if(Math.hypot(S.p.x-L.x,S.p.z-L.z)<20){
      L.found=true; PROG.found[L.name]=1;
      L.orb.visible=false; L.flag.visible=true;
      chime(); buzz(28); saveProg();
    }
  }
}

/* ================= camera ================= */""")

# ---------------------------------------------------------------- per frame
sub("""  /* lamps and tail lights come up as the light goes */""",
"""  if(WINDMILL) WINDMILL.rotation.z+=dt*0.5;
  var pulse=0.24+0.20*Math.sin(performance.now()*0.0022);
  for(var lg=0;lg<LANDMARKS.length;lg++){
    var Lm=LANDMARKS[lg];
    if(!Lm.found) Lm.orb.material.opacity=pulse*(1+TOD.night*1.1);
  }
  for(var lgi=0;lgi<LGLOW.length;lgi++){
    LGLOW[lgi].m.emissive.copy(LGLOW[lgi].c).multiplyScalar(TOD.glow*LGLOW[lgi].s);
  }

  /* lamps and tail lights come up as the light goes */""")

sub("""    checkGates();
    stepDust(dt);
    hud(dt); audioTick();""",
"""    checkGates();
    checkLandmarks();
    /* the odometer only ever goes up, which is the whole idea */
    PROG.odo += S.v.length()*dt;
    mapT+=dt; if(mapT>0.10){ mapT=0; markMap(S.p.x,S.p.z); }
    saveT+=dt; if(saveT>8){ saveT=0; saveProg(); }
    stepDust(dt);
    hud(dt); audioTick();""")

sub("var last=performance.now(), acc=0, FIXED=1/200;",
    "var last=performance.now(), acc=0, mapT=0, FIXED=1/200;")

# ---------------------------------------------------------------- pause screen
sub("""    <div class="tally3">
      <div><div class="lbl">Gates</div><div class="num" id="m-gates">0</div></div>
      <div><div class="lbl">Best air</div><div class="num" id="m-air">0.0s</div></div>
      <div><div class="lbl">Longest</div><div class="num" id="m-dist">0m</div></div>
    </div>""",
"""    <div class="tally3">
      <div><div class="lbl">Driven</div><div class="num" id="m-odo">0.0 km</div></div>
      <div><div class="lbl">Found</div><div class="num" id="m-found">0</div></div>
      <div><div class="lbl">Best air</div><div class="num" id="m-air">0.0s</div></div>
    </div>
    <div id="mapwrap"><canvas id="mapcv" width="192" height="192"></canvas></div>""")

sub("""  .tally3 .num{font-size:19px;margin-top:5px;color:var(--amber)}""",
"""  .tally3 .num{font-size:19px;margin-top:5px;color:var(--amber)}
  #mapwrap{margin:10px 0 2px;border:1px solid var(--edge);border-radius:2px;
           background:#150f1c;display:flex;justify-content:center;overflow:hidden}
  #mapcv{display:block;width:100%;max-width:230px;height:auto;image-rendering:pixelated}""")

sub("""document.getElementById('b-menu').addEventListener('click',function(){
  S.running=false;
  document.getElementById('m-gates').textContent=S.gates;
  document.getElementById('m-air').textContent=S.bestAir.toFixed(1)+'s';
  document.getElementById('m-dist').textContent=Math.round(S.bestDist)+'m';
  show('menu',true);
});""",
"""/* The map is drawn from where the wheels have been, plus a flag for every
   place you have reached. Nothing marks what you have not found. */
function drawMap(){
  var cv=document.getElementById('mapcv'), g=cv.getContext('2d');
  g.clearRect(0,0,192,192);
  g.fillStyle='#150f1c'; g.fillRect(0,0,192,192);
  var px=192/MAPN;
  for(var j=0;j<MAPN;j++) for(var i=0;i<MAPN;i++){
    var v=PROG.mapv[j*MAPN+i];
    if(!v) continue;
    var a=Math.min(1,v/200);
    g.fillStyle='rgba('+Math.round(190+50*a)+','+Math.round(130+70*a)+','+Math.round(70+40*a)+','+(0.25+0.65*a)+')';
    g.fillRect(i*px,j*px,px+0.6,px+0.6);
  }
  function toMap(x,z){ return [(x+HALF)/WORLD*192,(z+HALF)/WORLD*192]; }
  for(var li=0;li<LANDMARKS.length;li++){
    var L=LANDMARKS[li]; if(!L.found) continue;
    var q=toMap(L.x,L.z);
    g.fillStyle='#e0553f'; g.fillRect(q[0]-2.5,q[1]-2.5,5,5);
    g.fillStyle='#f4ebdd'; g.fillRect(q[0]-0.5,q[1]-6,1,4);
  }
  for(var si=0;si<3;si++){
    if(PROG.jump[si]<=0 || !STONES[si].visible) continue;
    var t=toMap(STONES[si].position.x,STONES[si].position.z);
    g.fillStyle='#ffb454'; g.fillRect(t[0]-1.5,t[1]-1.5,3,3);
  }
  var me=toMap(S.p.x,S.p.z);
  g.fillStyle='#2bc4b0'; g.beginPath(); g.arc(me[0],me[1],3.2,0,6.2832); g.fill();
  g.strokeStyle='rgba(0,0,0,.6)'; g.lineWidth=1; g.stroke();
}

document.getElementById('b-menu').addEventListener('click',function(){
  S.running=false;
  document.getElementById('m-odo').textContent=(PROG.odo/1000).toFixed(1)+' km';
  document.getElementById('m-found').textContent=Object.keys(PROG.found).length;
  document.getElementById('m-air').textContent=Math.max(S.bestAir,PROG.air).toFixed(1)+'s';
  drawMap();
  saveProg();
  show('menu',true);
});""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
