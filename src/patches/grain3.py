# -*- coding: utf-8 -*-
"""Grain that belongs to the world, and a brake that fills the way you push it.

THE DIRTY SCREEN. You were reading it exactly right, and the cause is that
there were two grains doing different jobs. The good one is in world space and
was only ever applied to the terrain, so the sand had texture and every rock,
bush, peak, gate and landmark stayed perfectly smooth. To cover for that, a
paper grain ran over the whole frame in screen space at four times its old
strength, and a screen space grain does not move when the world moves, which is
precisely what makes it read as a dirty screen rather than as surface.

So: world grain becomes the default on everything static, the screen paper
grain drops to a trace, and the haze itself is now modulated by the same tile
so distance carries texture too rather than arriving as clean wash. The truck
is the one thing kept out of it, because a world projected texture on a moving
object swims across it as it drives.

Instanced meshes needed care. The rocks and scrub are InstancedMesh, and in
this build `transformed` has not had the instance matrix applied yet at the
point the world position is taken, so every rock would have sampled the same
patch of tile. Guarded with USE_INSTANCING.

THE BRAKE GAUGE. Inverted, as asked. You pull down, so it now fills downward
from the top of the ring instead of upward from the bottom.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:100].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ------------------------------------------- grain on by default, world space
sub("""function styleMat(mm,opts){
  opts=opts||{};""",
"""function styleMat(mm,opts){
  opts=opts||{};
  /* Grain is the world's surface, so everything static wears it. Only things
     that move opt out, because a world projected tile slides across a moving
     object instead of sticking to it. */
  if(opts.grain===undefined) opts.grain=!opts.nograin;""")

sub("  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':''); };",
    "  mm.customProgramCacheKey=function(){ return 'sty'+(opts.grain?'G':'')+(opts.rim?'R':''); };")

# instancing: take the world position after the instance matrix, or every rock
# samples the same texel and the whole scatter shares one patch of tile
sub("""    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')
      .replace('#include <begin_vertex>',
               '#include <begin_vertex>\\nvWPosS=(modelMatrix*vec4(transformed,1.0)).xyz;');""",
"""    sh.vertexShader=sh.vertexShader
      .replace('#include <common>','#include <common>\\nvarying vec3 vWPosS;')
      .replace('#include <begin_vertex>',
               ['#include <begin_vertex>',
                '#ifdef USE_INSTANCING',
                '  vWPosS=(modelMatrix*instanceMatrix*vec4(transformed,1.0)).xyz;',
                '#else',
                '  vWPosS=(modelMatrix*vec4(transformed,1.0)).xyz;',
                '#endif'].join('\\n'));""")

# ---- the haze carries the same tile, so distance is textured, not clean wash
sub("""      'float hzH = 1.0 - smoothstep( uHazeLo, uHazeHi, vWPosS.y );',
      'float hzD = smoothstep( uHazeN, uHazeF, dS );',
      'pcS = mix( pcS, uHazeC, hzD * ( 0.30 + 0.70 * hzH ) * uHazeA );');""",
"""      'float hzH = 1.0 - smoothstep( uHazeLo, uHazeHi, vWPosS.y );',
      'float hzD = smoothstep( uHazeN, uHazeF, dS );'"""
+ """);
    /* the haze is made of the same grain, so the far field is atmosphere with
       texture in it rather than a clean sheet of colour */
    if(opts.grain) body.push('hzD *= 1.0 + grainS * 0.85;');
    body.push(
      'pcS = mix( pcS, uHazeC, clamp( hzD, 0.0, 1.0 ) * ( 0.30 + 0.70 * hzH ) * uHazeA );');""")

# ---------------------------------------- the truck opts out, it moves
sub("""  function smat(col,extra){ return styleMat(mat(col,extra),{}); }""",
    """  function smat(col,extra){ return styleMat(mat(col,extra),{nograin:true}); }""")
sub("""  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95]});""",
    """  var paint  = styleMat(mat(0x3f9dab),{rim:[2.4,0.95],nograin:true});""")
sub("""  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45]});""",
    """  var roofM  = styleMat(mat(0xf0ece0),{rim:[3.0,0.45],nograin:true});""")

# ------------------------------ the screen paper drops to a trace
sub("uSat:{value:1.20}, uVig:{value:0.16}, uGrain:{value:0.075},",
    "uSat:{value:1.20}, uVig:{value:0.16}, uGrain:{value:0.016},")

# ------------------------------------------------- the brake gauge, inverted
sub("""      else { IN.brake=0.50; pedalGauge(brakeEl,0,0.50,0.50,0,0,0); }""",
    """      else { IN.brake=0.50; pedalGauge(brakeEl,0,0.50,1-0.50,1,0,0); }""")
sub("""      if(PEDAL_MODE===2){ IN.brake=1; pedalGauge(brakeEl,0,1,1,0,0,0); }""",
    """      if(PEDAL_MODE===2){ IN.brake=1; pedalGauge(brakeEl,0,1,0,1,0,0); }""")
sub("""      IN.brake=Math.max(0.08,Math.min(1,0.50+(e.clientY-t.oy)/160));
      pedalGauge(brakeEl,0,IN.brake,IN.brake,0,0,0);""",
    """      IN.brake=Math.max(0.08,Math.min(1,0.50+(e.clientY-t.oy)/160));
      /* you pull down, so it fills downward from the top */
      pedalGauge(brakeEl,0,IN.brake,1-IN.brake,1,0,0);""")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
