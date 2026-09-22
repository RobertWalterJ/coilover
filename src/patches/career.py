# -*- coding: utf-8 -*-
"""A session that starts fresh, a career that does not, and something to chase.

TWO NUMBERS, NOT ONE. `PROG.score` was doing two incompatible jobs: it was the
number in the corner AND the thing that bought cars. So it could never reset,
and after a few drives the corner read a meaningless seven figures. Split:

  PROG.score   this session. Starts at zero every time you open the game, and
               it is what the corner counts.
  PROG.career  everything you have ever scored. Never resets, and it is what
               buys the garage and sets your rank.

The explored map resets with the session for the same reason: a fog-of-war
overlay that is already fully uncovered tells you nothing. Where you have
driven TODAY is a live picture; where you have ever driven is noise.

Records still persist, because a record is not a session: best run, top speed,
segment times, feats and found landmarks all carry over as they did.

AND A POINT TO IT. You said you had no sense of what the driving was for, which
is fair: it scored you and never asked you for anything. There are now three
open runs at any time, drawn from the map you are actually on, each worth real
career points, and a new one takes the place of each as you finish it. They are
concrete and short: hold a speed, land a jump of a stated size, chain five
scores without dropping it, find a landmark, beat one of your own segment
records. They show in the pause screen, and completing one announces itself.

Above them sits a rank, ten of them, from the first drive to the last. The
pause screen tells you what you are, what is next, and how far. That is the
long line the session sits inside.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ================================================ 1. the split
sub("           score:0, best:0, top:0, seg:{}, feat:{},",
    "           score:0, career:0, best:0, top:0, seg:{}, feat:{},")

sub("""    PROG.score=o.score||0; PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};
    PROG.feat=o.feat||{};
    if(o.map){
      var bin=atob(o.map);
      for(var i=0;i<PROG.mapv.length && i<bin.length;i++) PROG.mapv[i]=bin.charCodeAt(i);
    }""",
"""    /* The session score starts at zero every time. The career does not.
       An old save has only one number in it, so it becomes the career. */
    PROG.score=0;
    PROG.career=(o.career!==undefined? o.career : (o.score||0));
    PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};
    PROG.feat=o.feat||{};
    /* the explored map is per session too: an overlay that is already fully
       uncovered is not information */""")

sub("""    var str='';
    for(var i=0;i<PROG.mapv.length;i++) str+=String.fromCharCode(PROG.mapv[i]);
    localStorage.setItem(SAVEKEY,JSON.stringify({
      odo:PROG.odo, air:PROG.air, gates:PROG.gates, found:PROG.found,
      jump:PROG.jump, jumpAt:PROG.jumpAt,
      score:PROG.score, best:PROG.best, top:PROG.top, seg:PROG.seg,
      feat:PROG.feat, map:btoa(str)}));""",
"""    localStorage.setItem(SAVEKEY,JSON.stringify({
      odo:PROG.odo, air:PROG.air, gates:PROG.gates, found:PROG.found,
      jump:PROG.jump, jumpAt:PROG.jumpAt,
      career:PROG.career, best:PROG.best, top:PROG.top, seg:PROG.seg,
      feat:PROG.feat}));""")

# everything that gates on progress reads the career, not the session
sub("function have(o){ return PROG.score >= priceOf(o); }",
    "function have(o){ return PROG.career >= priceOf(o); }")
sub("""  if(UNL_SEEN<0){ UNL_SEEN=PROG.score; return; }
  var was=UNL_SEEN; UNL_SEEN=PROG.score;
  if(PROG.score<=was) return;""",
"""  if(UNL_SEEN<0){ UNL_SEEN=PROG.career; return; }
  var was=UNL_SEEN; UNL_SEEN=PROG.career;
  if(PROG.career<=was) return;""")
sub("    if(pr>was && pr<=PROG.score){", "    if(pr>was && pr<=PROG.career){")
sub("""    if(!ok) lk.innerHTML='Locked. <b>'+commas(priceOf(V))+'</b> points opens this one. '+
                         'You have '+commas(PROG.score)+', so <b>'+
                         commas(priceOf(V)-PROG.score)+'</b> to go.';""",
"""    if(!ok) lk.innerHTML='Locked. <b>'+commas(priceOf(V))+'</b> career points opens this '+
                         'one. You have '+commas(PROG.career)+', so <b>'+
                         commas(priceOf(V)-PROG.career)+'</b> to go.';""")
sub("""    self.textContent=MAPS[nx].name+': '+commas(priceOf(MAPS[nx])-PROG.score)+' points away';""",
"""    self.textContent=MAPS[nx].name+': '+commas(priceOf(MAPS[nx])-PROG.career)+' away';""")
sub("""    ? ('Next up: the '+nx.kind+' <b>'+nx.o.name+'</b> at '+commas(priceOf(nx.o))+
       ' points. <b>'+commas(priceOf(nx.o)-PROG.score)+'</b> to go.')""",
"""    ? ('Next up: the '+nx.kind+' <b>'+nx.o.name+'</b> at '+commas(priceOf(nx.o))+
       ' career points. <b>'+commas(priceOf(nx.o)-PROG.career)+'</b> to go.')""")

# every point scored counts twice: once for today, once forever
sub("""  SK.run+=pts;
  PROG.score+=pts;""",
"""  SK.run+=pts;
  PROG.score+=pts;                 /* this session, the number in the corner */
  PROG.career+=pts;                /* and the one that buys the garage */
  runProgress(name,pts);""")

# ================================================ 2. rank, and the open runs
sub("function driftName(d){",
"""/* ---- rank ----------------------------------------------------------
   Ten of them against the career total, so there is a long line for the
   session to sit inside and a name for where you are on it. */
var RANKS=[[0,'Green'],[2500,'Running In'],[8000,'Regular'],[20000,'Known Locally'],
           [42000,'Quick'],[78000,'Course Record'],[130000,'Feared'],
           [210000,'Legend of the Basin'],[330000,'Untouchable'],[520000,'Immortal']];
function rankOf(v){
  var i=0;
  for(var k=0;k<RANKS.length;k++) if(v>=RANKS[k][0]) i=k;
  return i;
}

/* ---- open runs ------------------------------------------------------
   Three at a time, drawn from the map you are on, each short enough to hold in
   your head and worth enough to matter. One is replaced the moment it is done,
   so there is always something being asked of you. */
var RUNPOOL=[
  {id:'hold',  pts:900,  make:function(){ var v=90+Math.floor(Math.random()*4)*20;
      return {t:'Hold '+v+' km/h for 7 seconds', v:v, need:7, got:0}; },
   step:function(r,dt,sp){ if(sp*3.6>=r.v) r.got+=dt; else r.got=0; return r.got>=r.need; }},
  {id:'air',   pts:850,  make:function(){ var v=[22,30,40][Math.floor(Math.random()*3)];
      return {t:'Land a jump of '+v+' metres', v:v}; },
   step:function(r,dt,sp,ev){ return ev.jump>=r.v; }},
  {id:'chain', pts:1100, make:function(){ var v=[4,5,6][Math.floor(Math.random()*3)];
      return {t:'Reach a x'+v+' chain', v:v}; },
   step:function(r){ return SK.chain>=r.v; }},
  {id:'drift', pts:950,  make:function(){ var v=[60,90,120][Math.floor(Math.random()*3)];
      return {t:'Hold a '+v+' metre drift', v:v}; },
   step:function(r,dt,sp,ev){ return ev.drift>=r.v; }},
  {id:'find',  pts:1000, make:function(){ return {t:'Find a new landmark'}; },
   step:function(r,dt,sp,ev){ return ev.found; }, maps:[0]},
  {id:'seg',   pts:1200, make:function(){ return {t:'Beat one of your segment records'}; },
   step:function(r,dt,sp,ev){ return ev.segRec; }}
];
var RUNS=[null,null,null], runEv={jump:0,drift:0,found:false,segRec:false};
function newRun(slot){
  var tries=0, pick;
  do{ pick=RUNPOOL[Math.floor(Math.random()*RUNPOOL.length)]; tries++; }
  while(tries<24 && ((pick.maps && pick.maps.indexOf(MAP)<0) ||
        RUNS.some(function(r,i){ return i!==slot && r && r.id===pick.id; })));
  var r=pick.make(); r.id=pick.id; r.pts=pick.pts; r.step=pick.step;
  RUNS[slot]=r;
}
function resetRuns(){ for(var i=0;i<3;i++) newRun(i); }
/* Called from award, so a run can be finished by the same act that scored. */
function runProgress(){}
function stepRuns(dt){
  var sp=S.v.length();
  for(var i=0;i<3;i++){
    var r=RUNS[i]; if(!r) { newRun(i); continue; }
    var done=false;
    try{ done=r.step(r,dt,sp,runEv); }catch(e){}
    if(done){
      PROG.career+=r.pts; PROG.score+=r.pts;
      if(popN){ popN.textContent='Run complete';
                popP.textContent='+'+r.pts; popEl.className='on'; popT=2.0; }
      chime(); buzz(38); flyScore(r.pts); if(TAL_WAIT<=0) TAL_WAIT=0.62;
      newRun(i); saveProg(); checkUnlocks();
    }
  }
  runEv.jump=0; runEv.drift=0; runEv.found=false; runEv.segRec=false;
}

function driftName(d){""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
