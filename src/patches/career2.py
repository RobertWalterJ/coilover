# -*- coding: utf-8 -*-
"""Wire the runs to the acts that satisfy them, and show the rank.

The run definitions exist; this hands them the four events they watch (a jump
landed, a drift ended, a landmark found, a segment record beaten), steps them
each frame, and puts the rank, the three open runs and the session total on the
pause screen so there is something to read before you drive off again.

The pause screen's headline numbers change with the split: Points is now this
session, and Career sits beside it, because those are two different questions
and the old screen could only answer one of them.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- the four events the runs watch
sub("""      award(airName(S.airT,dist), 26*S.airT + 2.6*dist);""",
"""      award(airName(S.airT,dist), 26*S.airT + 2.6*dist);
      if(dist>runEv.jump) runEv.jump=dist;""")

sub("""    if(SK.drift.dist>16) award(driftName(SK.drift.dist), SK.drift.dist*1.15*(1+SK.drift.peak));""",
"""    if(SK.drift.dist>16){
      award(driftName(SK.drift.dist), SK.drift.dist*1.15*(1+SK.drift.peak));
      if(SK.drift.dist>runEv.drift) runEv.drift=SK.drift.dist;
    }""")

sub("""      award('Found '+L.name, 340);""",
"""      award('Found '+L.name, 340);
      runEv.found=true;""")

sub("""        PROG.seg[key]=SK.segPts;""",
"""        PROG.seg[key]=SK.segPts;
        if(prev>0) runEv.segRec=true;      /* beating nothing is not a record */""")

# ---- step them, and start a fresh set with each session and each map
sub("""    skills(dt);
    if(popT>0){ popT-=dt; if(popT<=0 && popEl) popEl.className=''; }""",
"""    skills(dt);
    stepRuns(dt);
    if(popT>0){ popT-=dt; if(popT<=0 && popEl) popEl.className=''; }""")

sub("""        readInput(dt); step(dt); checkGates(); checkLandmarks(); skills(dt);""",
    """        readInput(dt); step(dt); checkGates(); checkLandmarks(); skills(dt); stepRuns(dt);""")

sub("""  breakChain();
  try{ localStorage.setItem('coilover.map',String(i)); }catch(_){}""",
"""  breakChain();
  resetRuns();                 /* the open runs belong to the map you are on */
  try{ localStorage.setItem('coilover.map',String(i)); }catch(_){}""")

# ---- the pause screen
sub("""      <div><div class="lbl">Points</div><div class="num" id="m-score">0</div></div>
      <div><div class="lbl">Best run</div><div class="num" id="m-best">0</div></div>
      <div><div class="lbl">Top</div><div class="num" id="m-top">0</div></div>""",
"""      <div><div class="lbl">This session</div><div class="num" id="m-score">0</div></div>
      <div><div class="lbl">Career</div><div class="num" id="m-career">0</div></div>
      <div><div class="lbl">Best run</div><div class="num" id="m-best">0</div></div>""")

sub("""    <div class="nxt" id="m-next"></div>""",
"""    <div class="rankrow"><b id="m-rank">Green</b><span id="m-rankto"></span></div>
    <div class="rankbar"><i id="m-rankfill"></i></div>
    <div class="grp">Open runs</div>
    <div id="runs"></div>
    <div class="nxt" id="m-next"></div>""")

sub("""  .nxt{font-size:12px;color:var(--mute);margin:10px 0 0;line-height:1.45}""",
"""  .rankrow{display:flex;align-items:baseline;gap:10px;margin:14px 0 6px}
  .rankrow b{font-weight:700;font-size:19px;text-transform:uppercase;
             letter-spacing:.03em;color:var(--cream)}
  .rankrow span{font-size:11px;color:var(--mute);text-transform:uppercase;
                letter-spacing:.14em}
  .rankbar{height:5px;border-radius:2px;background:var(--edge);overflow:hidden}
  .rankbar i{display:block;height:100%;background:var(--amber)}
  #runs div{display:flex;justify-content:space-between;gap:12px;align-items:baseline;
            padding:7px 0;border-bottom:1px solid var(--edge);font-size:13px;
            color:#ded2d8}
  #runs div:last-child{border-bottom:0}
  #runs b{font-family:"Azeret Mono",monospace;font-weight:700;font-size:12px;
          color:var(--amber);white-space:nowrap}
  #runs u{text-decoration:none;font-size:11px;color:var(--mute);white-space:nowrap}
  .nxt{font-size:12px;color:var(--mute);margin:10px 0 0;line-height:1.45}""")

sub("""  document.getElementById('m-score').textContent=PROG.score;
  document.getElementById('m-best').textContent=PROG.best;
  document.getElementById('m-top').textContent=Math.round(PROG.top*3.6);""",
"""  document.getElementById('m-score').textContent=commas(PROG.score);
  var mc=document.getElementById('m-career');
  if(mc) mc.textContent=commas(PROG.career);
  document.getElementById('m-best').textContent=commas(PROG.best);
  /* rank: what you are, what is next, and how far */
  var ri=rankOf(PROG.career), rn=document.getElementById('m-rank');
  if(rn){
    rn.textContent=RANKS[ri][1];
    var nxr=RANKS[ri+1], to=document.getElementById('m-rankto');
    var lo=RANKS[ri][0], hi=nxr?nxr[0]:lo+1;
    to.textContent=nxr? (commas(hi-PROG.career)+' to '+nxr[1]) : 'nothing left to prove';
    document.getElementById('m-rankfill').style.width=
      (nxr? Math.max(2,Math.min(100,(PROG.career-lo)/(hi-lo)*100)) : 100)+'%';
  }
  /* and the three things currently being asked of you */
  var rv='';
  for(var qi=0;qi<RUNS.length;qi++){
    var R=RUNS[qi]; if(!R) continue;
    var prog='';
    if(R.id==='hold' && R.got>0) prog='<u>'+R.got.toFixed(1)+'/'+R.need+'s</u>';
    if(R.id==='chain') prog='<u>x'+SK.chain+' now</u>';
    rv+='<div><span>'+R.t+'</span>'+prog+'<b>+'+commas(R.pts)+'</b></div>';
  }
  document.getElementById('runs').innerHTML=rv;""")

# ---- and a set waiting the moment the game opens
sub("""  var ck=0; try{ ck=parseInt(localStorage.getItem('coilover.clock')||'0',10)||0; }catch(_){}""",
"""  resetRuns();
  var ck=0; try{ ck=parseInt(localStorage.getItem('coilover.clock')||'0',10)||0; }catch(_){}""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
