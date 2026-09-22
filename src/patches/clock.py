# -*- coding: utf-8 -*-
"""The clock, at a speed you can actually live in.

"Let it drift" was a bad name and "Light drifts" was barely better: both
describe the mechanism rather than the thing. It moves the time of day. It is
now called that, and its partner button that jumps between the five is named
to match, so the two read as a pair:

    Time of day: Golden        <- pick one
    Time passes: no            <- and whether it moves

THE SPEED. It ran at 0.0055 per second, so a stage took 3 minutes and the whole
day took 15. Golden hour arrived and was gone before you had finished a run.
Three settings now, off by default:

    slowly    18 minutes a stage, about an hour and a half for a full day
    quickly    5 minutes a stage, about 25 minutes for a day

AND THE GOOD LIGHT LINGERS. An even rate gives Night exactly as much of your
attention as Golden, which is the wrong split for this game. Each time now
carries a dwell: Golden and Dusk hold roughly twice as long as Morning, so the
clock moves quickly through the flat light and slows down through the light
that is worth looking at.

The setting is remembered, like the pedal mode.
"""
import io

p = 'game.html'
s = io.open(p, encoding='utf-8').read()
n = 0

def sub(old, new):
    global s, n
    assert old in s, 'MISS: ' + old[:110].replace('\n', ' | ')
    s = s.replace(old, new, 1); n += 1

# ---- how long each time of day holds, relative to the others
sub("  { name:'Dawn',",    "  { name:'Dawn',    dwell:1.15,")
sub("  { name:'Morning',", "  { name:'Morning', dwell:0.70,")
sub("  { name:'Golden',",  "  { name:'Golden',  dwell:1.85,")
sub("  { name:'Dusk',",    "  { name:'Dusk',    dwell:2.00,")
sub("  { name:'Night',",   "  { name:'Night',   dwell:0.85,")

# ---- three speeds, off by default, remembered
sub("var TOD={ i:2, from:2, to:2, k:1, drift:false, glow:0.12, night:0 };",
    "var TOD={ i:2, from:2, to:2, k:1, drift:0, glow:0.12, night:0 };\n"
    "/* Rates in stages per second. The old single speed was 0.0055, a stage\n"
    "   every three minutes, which ran through golden hour before a lap was\n"
    "   over. `dwell` on each time then stretches the ones worth sitting in. */\n"
    "var CLOCK_NAMES=['no','slowly','quickly'], CLOCK_RATE=[0, 0.00092, 0.00333];")

sub("""  else if(TOD.drift){
    TOD.k+=dt*0.0055;                       /* a full hour every three minutes */
    if(TOD.k>=1){ TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; }
    applyTime(TOD.k);""",
"""  else if(TOD.drift){
    /* divided by the dwell of the time we are leaving, so the clock hurries
       through flat morning light and takes its time over golden and dusk */
    TOD.k+=dt*CLOCK_RATE[TOD.drift]/(TIMES[TOD.from].dwell||1);
    if(TOD.k>=1){ TOD.from=TOD.to; TOD.to=(TOD.to+1)%TIMES.length; TOD.k=0; }
    applyTime(TOD.k);""")

# ---- the two buttons, named for what they do
sub('    <button class="go ghost" id="b-drift">Light drifts: off</button>',
    '    <button class="go ghost" id="b-drift">Time passes: no</button>')
sub("""document.getElementById('b-drift').addEventListener('click',function(){
  TOD.drift=!TOD.drift; this.textContent='Light drifts: '+(TOD.drift?'on':'off');
});""",
"""function setClock(m){
  TOD.drift=m;
  var b=document.getElementById('b-drift');
  if(b) b.textContent='Time passes: '+CLOCK_NAMES[m];
  try{ localStorage.setItem('coilover.clock',String(m)); }catch(_){}
}
document.getElementById('b-drift').addEventListener('click',function(){
  setClock((TOD.drift+1)%CLOCK_NAMES.length);
});""")

sub("  this.textContent='Light: '+TIMES[TOD.to].name;",
    "  this.textContent='Time of day: '+TIMES[TOD.to].name;")
sub('    <button class="go ghost" id="b-time">Light: Golden</button>',
    '    <button class="go ghost" id="b-time">Time of day: Golden</button>')

# ---- and it is remembered
sub("  setPedalMode(Math.max(0,Math.min(PEDAL_NAMES.length-1,m)));",
    "  setPedalMode(Math.max(0,Math.min(PEDAL_NAMES.length-1,m)));\n"
    "  var ck=0; try{ ck=parseInt(localStorage.getItem('coilover.clock')||'0',10)||0; }catch(_){}\n"
    "  setClock(Math.max(0,Math.min(CLOCK_NAMES.length-1,ck)));")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('applied:', n)
