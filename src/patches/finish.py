# -*- coding: utf-8 -*-
"""The four outstanding items: feats, a wordless opening, landscape, filtering.

FEATS. Four named things worth going out of your way for, designed a while ago
and never written. Each is awarded at the moment you finish it, none of them is
timed, and each one is remembered the first time you do it so there is
something to have done rather than only something to score.

  Whoop skim    carry the washboard at speed with the wheels mostly off it
  Salt circle   a full turn, held sideways, without straightening, on the lake
  Ramp chain    all three kickers with real air, inside one chain
  Rim run       a full lap of the rim, inside one chain

WORDLESS OPENING. The game opened on a card that told you which side does what.
It now opens in the world, on a slow orbit of your truck, with the two pedals
breathing where your thumbs go. Touch anything and you are driving. The only
word on screen is the name, and it fades.

LANDSCAPE. There was one height based media query and nothing about landscape,
so on a phone held sideways the pedals sat where the palm of your hand is. They
now move inboard and up, the steering arc shortens, and the score clears the
notch.

FILTERING. Not the cheesy end of that era: no lens flare, no dirty lens. The
part you actually asked for is the texel. Magnification goes to nearest, so up
close a texture shows its pixels the way a 2005 console did, while minification
stays linear so the distance does not crawl.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ===================================================== 1. chunky magnification
sub("""    t.wrapS=t.wrapT=THREE.RepeatWrapping;
    t.magFilter=t.minFilter=THREE.LinearFilter;
    t.generateMipmaps=false;""",
"""    t.wrapS=t.wrapT=THREE.RepeatWrapping;
    /* nearest when magnified so a texel is a visible square up close, linear
       when minified so the far field does not crawl. That split is the 2005
       look without any of the lens nonsense that came with it. */
    t.magFilter=THREE.NearestFilter;
    t.minFilter=THREE.LinearFilter;
    t.generateMipmaps=false;""")
sub("""  t.anisotropy=1; t.magFilter=THREE.LinearFilter; t.minFilter=THREE.LinearFilter;
  t.generateMipmaps=false;""",
"""  t.anisotropy=1; t.magFilter=THREE.NearestFilter; t.minFilter=THREE.LinearFilter;
  t.generateMipmaps=false;""")

# ===================================================================== 2. feats
sub("""var SK={ chain:1, run:0, since:0, seg:null, segPts:0, fastFlag:false,""",
"""/* ---- feats ----
   Four things worth driving out of your way for. Each is an event, none is a
   clock, and the first time you land one it is remembered. */
var FEATS=[
  {id:'whoop', name:'Whoop skim',  pts:420},
  {id:'circle',name:'Salt circle', pts:520},
  {id:'ramps', name:'Ramp chain',  pts:680},
  {id:'rim',   name:'Rim run',     pts:600}
];
var FT={
  whoopD:0, whoopAir:0, whoopIn:false,
  circYaw:0, circOn:false,
  ramps:{}, rampN:0,
  rimA:0, rimLast:null, rimIn:false
};
function featDone(id){
  for(var i=0;i<FEATS.length;i++) if(FEATS[i].id===id){
    var first=!PROG.feat[id];
    PROG.feat[id]=(PROG.feat[id]||0)+1;
    award(FEATS[i].name + (first?'':' again'), FEATS[i].pts);
    if(first){ chime(); saveProg(); }
    return;
  }
}

var SK={ chain:1, run:0, since:0, seg:null, segPts:0, fastFlag:false,""")

sub("""  /* named segments */""",
"""  /* ---- whoop skim: the washboard, fast, mostly airborne ---- */
  var inWhoop = Math.abs(S.p.z+48)<26 && S.p.x>-72 && S.p.x<128;
  if(inWhoop && sp>16){
    if(!FT.whoopIn){ FT.whoopIn=true; FT.whoopD=0; FT.whoopAir=0; }
    FT.whoopD+=d;
    if(S.grounded<2) FT.whoopAir+=d;
    if(FT.whoopD>70 && FT.whoopAir/FT.whoopD>0.34){ featDone('whoop'); FT.whoopIn=false; }
  }else if(FT.whoopIn && (!inWhoop || sp<8)){ FT.whoopIn=false; }

  /* ---- salt circle: a full turn held sideways on the lakebed ---- */
  var onSalt = corners[0].surf && corners[0].surf.n==='riverbed';
  if(onSalt && SK.drift.on && sp>10){
    FT.circOn=true; FT.circYaw+=Math.abs(S.w.y)*dt;
    if(FT.circYaw>6.283){ featDone('circle'); FT.circYaw=0; FT.circOn=false; }
  }else if(FT.circOn){ FT.circOn=false; FT.circYaw=0; }

  /* ---- ramp chain: all three kickers with air, inside one chain ---- */
  if(S.grounded<2 && S.airT>0.45){
    for(var ki=0;ki<KICKERS.length;ki++){
      if(Math.hypot(S.p.x-KICKERS[ki].x,S.p.z-KICKERS[ki].z)<34 && !FT.ramps[ki]){
        FT.ramps[ki]=1; FT.rampN++;
        if(FT.rampN>=3){ featDone('ramps'); FT.ramps={}; FT.rampN=0; }
      }
    }
  }

  /* ---- rim run: a full lap of the rim, inside one chain ---- */
  var r=Math.hypot(S.p.x,S.p.z);
  if(r>148 && r<194 && sp>9){
    var a=Math.atan2(S.p.z,S.p.x);
    if(FT.rimLast!==null){
      var da=a-FT.rimLast;
      while(da>Math.PI) da-=6.283; while(da<-Math.PI) da+=6.283;
      FT.rimA+=da;
      if(Math.abs(FT.rimA)>6.10){ featDone('rim'); FT.rimA=0; }
    }
    FT.rimLast=a; FT.rimIn=true;
  }else if(FT.rimIn){ FT.rimIn=false; FT.rimLast=null; FT.rimA=0; }

  /* named segments */""")

# breaking the chain resets the two feats that depend on one
sub("""  SK.chain=1; SK.run=0; SK.since=0; SK.fastFlag=false;
  if(tallyC) tallyC.textContent='';""",
"""  SK.chain=1; SK.run=0; SK.since=0; SK.fastFlag=false;
  FT.ramps={}; FT.rampN=0; FT.rimA=0; FT.rimLast=null;
  if(tallyC) tallyC.textContent='';""")

# feats persist
sub("           score:0, best:0, top:0, seg:{}, mapv:new Uint8Array(MAPN*MAPN) };",
    "           score:0, best:0, top:0, seg:{}, feat:{}, mapv:new Uint8Array(MAPN*MAPN) };")
sub("    PROG.score=o.score||0; PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};",
    "    PROG.score=o.score||0; PROG.best=o.best||0; PROG.top=o.top||0; PROG.seg=o.seg||{};\n    PROG.feat=o.feat||{};")
sub("      score:PROG.score, best:PROG.best, top:PROG.top, seg:PROG.seg, map:btoa(str)}));",
    "      score:PROG.score, best:PROG.best, top:PROG.top, seg:PROG.seg,\n      feat:PROG.feat, map:btoa(str)}));")

# and they show on the pause card, under the segments
sub("""  document.getElementById('segs').innerHTML=sv;""",
"""  document.getElementById('segs').innerHTML=sv;
  var fv='';
  for(var fi=0;fi<FEATS.length;fi++){
    var c=PROG.feat[FEATS[fi].id]||0;
    fv+='<div class="'+(c?'on':'')+'"><span>'+FEATS[fi].name+'</span><b>'+
        (c?(c>1?('x'+c):'done'):'')+'</b></div>';
  }
  document.getElementById('feats').innerHTML=fv;""")
sub("""    <div id="segs"></div>""",
    """    <div id="segs"></div>
    <div class="grp">Feats</div>
    <div id="feats"></div>""")
sub("""  #segs b{font-family:"Azeret Mono",monospace;font-weight:700;color:var(--amber);font-size:14px}""",
"""  #segs b{font-family:"Azeret Mono",monospace;font-weight:700;color:var(--amber);font-size:14px}
  #feats{display:flex;flex-direction:column;gap:5px}
  #feats div{display:flex;justify-content:space-between;align-items:baseline;
             font-size:14px;color:#6d6270}
  #feats div.on{color:#ded2d8}
  #feats b{font-family:"Azeret Mono",monospace;font-weight:700;font-size:12px;
           color:var(--teal);text-transform:uppercase;letter-spacing:.08em}""")

# ======================================================= 3. wordless opening
sub("""<div class="sheet" id="intro">
  <div class="card">
    <h1>Coil<em>over</em></h1>
    <div class="rule"></div>
    <p>Right side drives. Left side steers.</p>
    <button class="go" id="b-start">Drive</button>
  </div>
</div>""",
"""<div id="intro">
  <div id="ititle">Coil<em>over</em></div>
  <button id="b-start" aria-label="Drive"></button>
</div>""")

sub("""  /* the running score. Small, in the corner, and it is the only number on""",
"""  /* The opening. No card, no instructions: the world is already there, the
     truck turns in front of you, and the two pedal rings breathe where your
     thumbs go. Touch anything and you are driving. */
  #intro{position:fixed;inset:0;z-index:5}
  #intro[hidden]{display:none}
  #b-start{position:absolute;inset:0;width:100%;height:100%;
           background:none;border:0;padding:0;cursor:pointer}
  #ititle{position:absolute;left:50%;top:16%;transform:translateX(-50%);
          font-weight:700;font-size:52px;letter-spacing:.02em;text-transform:uppercase;
          color:var(--cream);text-shadow:0 3px 22px rgba(20,10,6,.9);
          pointer-events:none;animation:fadeIn .9s ease both}
  #ititle em{font-style:normal;color:var(--amber)}
  @keyframes fadeIn{from{opacity:0;transform:translateX(-50%) translateY(9px)}
                    to{opacity:1;transform:translateX(-50%) translateY(0)}}
  /* the rings breathe until you touch one, which is the whole tutorial */
  #hud.wait .ring{animation:breathe 2.1s ease-in-out infinite}
  #hud.wait #brake{animation-delay:.5s}
  @keyframes breathe{0%,100%{border-color:rgba(244,235,221,.22);transform:scale(1)}
                     50%{border-color:rgba(244,235,221,.80);transform:scale(1.055)}}

  /* the running score. Small, in the corner, and it is the only number on""")

sub("""document.getElementById('b-start').addEventListener('click',function(){
  audioOn(); engineStart(); show('intro',false); S.running=true; last=performance.now(); acc=0;
});""",
"""document.getElementById('b-start').addEventListener('click',function(){
  audioOn(); engineStart();
  show('intro',false);
  hudEl.classList.remove('wait');
  GARAGE.on=false; camera.fov=54; camera.updateProjectionMatrix();
  placeTruck(0,0,0.4);
  S.running=true; last=performance.now(); acc=0;
});""")

# open on the turntable rather than on a card
sub("""resize();
applyTime(1);
S.camMode=0;""",
"""resize();
applyTime(1);
/* the opening view: the world, and your truck turning in it */
hudEl.classList.add('wait');
GARAGE.on=true; GARAGE.ang=0.6;
placeTruck(-96,96,0.0);
S.camMode=0;""")

# ============================================================== 4. landscape
sub("""  @media (max-height:560px){
    #gas{width:86px;height:86px}#brake{width:62px;height:62px}
    #gas.one{width:108px;height:108px;bottom:calc(88px + env(safe-area-inset-bottom))}""",
"""  /* A phone held sideways is short and wide, and the old rules put the pedals
     under the heel of your hand. Bring them inboard and up. */
  @media (orientation:landscape) and (max-height:520px){
    #gas{width:78px;height:78px;
         right:calc(20px + env(safe-area-inset-right));
         bottom:calc(20px + env(safe-area-inset-bottom))}
    #brake{width:56px;height:56px;
           right:calc(112px + env(safe-area-inset-right));
           bottom:calc(14px + env(safe-area-inset-bottom))}
    #gas.one{width:92px;height:92px;
             right:calc(18px + env(safe-area-inset-right));
             bottom:calc(58px + env(safe-area-inset-bottom))}
    #arc{width:104px;height:104px;margin:-52px 0 0 -52px}
    #tally{top:calc(7px + env(safe-area-inset-top));
           left:calc(9px + env(safe-area-inset-left))}
    #tally b{font-size:16px}
    #ititle{top:9%;font-size:38px}
    #pop{top:24%}
    #chn{top:calc(24% + 38px)}
    .card{max-width:430px;padding:14px 16px 12px;
          max-height:calc(100vh - 24px);overflow-y:auto}
    .card h1{font-size:30px}
    #mapwrap{display:none}
  }
  @media (max-height:560px){
    #gas{width:86px;height:86px}#brake{width:62px;height:62px}
    #gas.one{width:108px;height:108px;bottom:calc(88px + env(safe-area-inset-bottom))}""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
