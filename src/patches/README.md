# The patch scripts

Seventy-nine one-shot Python scripts. Each one opened `src/game.html`, made a
set of exact string substitutions, and wrote it back. None of them will run
now — every anchor they look for has long since been edited by a later script,
and they assert rather than fail silently, which is the point.

They are here because of what is at the top of each one. Every script opens
with a docstring saying what was wrong, how it was established that it was
wrong, and what was done about it. Together they are the reasoning behind the
game in the order it happened, which the finished file cannot show you:

- `light.py` — the shader collapsed the whole lighting result to one brightness
  number before using it, so every light colour in five times of day was being
  discarded at that line. Forcing the sun to pure green moved the frame 10.8%.
- `fix7.py` — the rally crackle had never fired once, at any frame rate,
  because it compared two adjacent smoothed frames of throttle.
- `tc.py` — why 52,000 N of drive made a car undriveable, and why the answer
  was traction control rather than a smaller engine.
- `gates2.py` — what the gates were actually worth before they became a
  circuit, which was almost nothing.
- `marisol4.py` — why a lofted body can never read as a truck, and the
  admission that the method was wrong rather than the numbers.

The naming is chronological within a topic: `aero.py` then `aero2.py` then
`aero3.py` is three passes at the same problem, and reading them in order shows
two of them being wrong before the third one worked.

The measured figures quoted in the docstrings were taken through the headless
harness the game exposes under `?debug` — `window.coilover.tick(seconds)` steps
the simulation without a browser frame, which is how a claim like "0 fires at
every rate from 25 to 144" was checked rather than asserted.
