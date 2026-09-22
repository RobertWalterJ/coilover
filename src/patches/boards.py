# -*- coding: utf-8 -*-
"""Billboards, a plane livery, and a picture on the drive in screen.

One line on how this is done, because it matters. The weathering comes from a
real photograph, `Old_Paper_texture.jpg`, CC0, baked in as data. Everything
painted ON these surfaces is invented and drawn here in code: the words are
generic roadside copy, the aircraft carries a made up registration and a made
up cheatline, and there is not a single real brand, logo, badge or livery
anywhere. Reproducing someone's trade dress into a published game is the one
thing I will not do, and using a real photo of an advert would do exactly that.

So: a painted face is drawn as flat shapes, then the photograph is multiplied
over it, which is what makes the paint look sun bleached and the paper look
like it has been up for thirty years.

Six billboards go into the landscape on the approaches, each one a different
face, tall enough to read from a long way out, which is the whole point of a
billboard and also of a landmark in this game.
"""
import io, base64

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

paper = base64.b64encode(open('../shots/px_paper.png', 'rb').read()).decode()

# ------------------------------------------------------------- the paper tile
sub("var PHOTO_SAND=null, PHOTO_ROCK=null, PHOTO_PLAYA=null, PHOTO_METAL=null;",
    "var PHOTO_SAND=null, PHOTO_ROCK=null, PHOTO_PLAYA=null, PHOTO_METAL=null;\nvar PAPER_IMG=null;")

sub("""  PHOTO_PLAYA=tex('""",
"""  /* the weathering overlay is used as an Image, not as a texture, because it
     is composited into painted artwork rather than sampled in a shader */
  PAPER_IMG=new Image();
  PAPER_IMG.onload=function(){ if(window.__repaintBoards) window.__repaintBoards(); };
  PAPER_IMG.src='data:image/png;base64,%PAPER%';
  PHOTO_PLAYA=tex('""".replace('%PAPER%', paper))

# ------------------------------------------- painted panel helper + billboards
sub("""/* the windmill rotor got pushed on as a bare entry; pull it back out */""",
"""/* ---- painted faces ----
   Draw invented artwork, then multiply the photograph over it so the paint
   reads as sun bleached and the board reads as old. Repainted once the
   photograph has decoded, so there is never a blank frame. */
var BOARDS=[];
function paintedFace(w,h,draw){
  var c=document.createElement('canvas'); c.width=w; c.height=h;
  var t=new THREE.CanvasTexture(c);
  t.anisotropy=1; t.magFilter=THREE.LinearFilter; t.minFilter=THREE.LinearFilter;
  t.generateMipmaps=false;
  var entry={cv:c, tex:t, draw:draw};
  BOARDS.push(entry);
  repaintBoard(entry);
  return t;
}
function repaintBoard(e){
  var x=e.cv.getContext('2d');
  x.setTransform(1,0,0,1,0,0);
  x.clearRect(0,0,e.cv.width,e.cv.height);
  e.draw(x,e.cv.width,e.cv.height);
  if(PAPER_IMG && PAPER_IMG.complete && PAPER_IMG.naturalWidth){
    x.globalCompositeOperation='multiply';
    x.globalAlpha=0.85;
    for(var j=0;j<Math.ceil(e.cv.height/128);j++)
      for(var i=0;i<Math.ceil(e.cv.width/128);i++)
        x.drawImage(PAPER_IMG,i*128,j*128);
    /* a second, larger pass gives big sun bleached patches as well as grain */
    x.globalAlpha=0.40;
    x.drawImage(PAPER_IMG,0,0,e.cv.width,e.cv.height);
    x.globalCompositeOperation='source-over';
    x.globalAlpha=1;
  }
  e.tex.needsUpdate=true;
}
window.__repaintBoards=function(){ for(var i=0;i<BOARDS.length;i++) repaintBoard(BOARDS[i]); };

/* ---- the boards themselves. Generic roadside copy, nobody's brand. ---- */
(function(){
  function frameTxt(x,W,H,bg,ink,line1,line2,accent){
    x.fillStyle=bg; x.fillRect(0,0,W,H);
    x.fillStyle=accent; x.fillRect(0,0,W,Math.round(H*0.055));
    x.fillRect(0,H-Math.round(H*0.055),W,Math.round(H*0.055));
    x.fillStyle=ink;
    x.textAlign='center'; x.textBaseline='middle';
    x.font='700 '+Math.round(H*0.34)+'px "Chakra Petch",sans-serif';
    x.fillText(line1,W/2,line2?H*0.40:H*0.52);
    if(line2){
      x.font='600 '+Math.round(H*0.15)+'px "Chakra Petch",sans-serif';
      x.fillText(line2,W/2,H*0.70);
    }
  }
  function sunset(x,W,H){
    var g=x.createLinearGradient(0,0,0,H);
    g.addColorStop(0,'#3c2a63'); g.addColorStop(0.55,'#d4593f'); g.addColorStop(1,'#f0b45e');
    x.fillStyle=g; x.fillRect(0,0,W,H);
    x.fillStyle='#ffd98a';
    x.beginPath(); x.arc(W*0.5,H*0.58,H*0.20,0,6.284); x.fill();
    x.fillStyle='#2b1c46';
    x.beginPath(); x.moveTo(0,H);
    x.lineTo(W*0.22,H*0.60); x.lineTo(W*0.38,H*0.78); x.lineTo(W*0.58,H*0.46);
    x.lineTo(W*0.78,H*0.74); x.lineTo(W,H*0.55); x.lineTo(W,H); x.closePath(); x.fill();
  }
  var FACES=[
    function(x,W,H){ frameTxt(x,W,H,'#e8dcc2','#9c3a28','FUEL','90 MILES','#2f6f7a'); },
    function(x,W,H){ frameTxt(x,W,H,'#2f5f6b','#f2e6cc','COLD','DRINKS AHEAD','#e0a03c'); },
    function(x,W,H){ sunset(x,W,H); },
    function(x,W,H){ frameTxt(x,W,H,'#d8cdb4','#37506b','MOTEL','VACANCY','#c4452e'); },
    function(x,W,H){ frameTxt(x,W,H,'#8f3a2c','#f4e8cf','LAST','STOP','#e5b23c'); },
    function(x,W,H){ sunset(x,W,H); }
  ];
  /* out on the approaches, angled to face the middle of the basin */
  var SPOTS=[[-150,10],[126,-24],[-24,172],[62,-158],[178,44],[-172,-104]];
  var legM=styleMat(new THREE.MeshPhongMaterial({color:sc(0x6a5a54),specular:0x000000,
    shininess:0,flatShading:true}),{tex:'metal'});
  for(var i=0;i<SPOTS.length;i++){
    var bx2=SPOTS[i][0], bz=SPOTS[i][1];
    var g=new THREE.Group();
    g.position.set(bx2,height(bx2,bz),bz);
    g.rotation.y=Math.atan2(-bx2,-bz);
    var face=paintedFace(256,128,FACES[i%FACES.length]);
    var panelM=new THREE.MeshPhongMaterial({map:face,specular:0x000000,shininess:0});
    var bd=new THREE.Mesh(new THREE.BoxGeometry(11.5,5.8,0.34),panelM);
    bd.position.y=9.2; bd.castShadow=true; g.add(bd);
    [-4.1,4.1].forEach(function(lx){
      var leg=new THREE.Mesh(new THREE.CylinderGeometry(0.22,0.26,6.6,6),legM);
      leg.position.set(lx,3.3,0); leg.castShadow=true; g.add(leg);
    });
    var rail=new THREE.Mesh(new THREE.BoxGeometry(12.2,0.26,0.5),legM);
    rail.position.y=6.2; g.add(rail);
    scene.add(g);
  }
})();

/* the windmill rotor got pushed on as a bare entry; pull it back out */""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
