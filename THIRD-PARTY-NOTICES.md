# What is in here that is not mine

Coilover has one dependency and no assets. Everything you see in the game —
every texture, every sound, every vehicle, the terrain, the sky — is generated
by the code at load time. There are no image files, no audio files and no
models in this repository, which is why the whole thing is one HTML file.

## three.js r128 — MIT

The renderer. <https://threejs.org>

Copyright © 2010–2026 three.js authors. Licensed under the MIT License, the
full text of which is at <https://github.com/mrdoob/three.js/blob/dev/LICENSE>.

A minified copy is vendored at `app/vendor/three.min.js` (and the generated
`docs/vendor/three.min.js`) so the installed app runs with no network at all.
The Artifact build in `src/game.html` loads the same version from cdnjs
instead.

Only the core UMD build is used. Nothing from `three/examples` is imported,
which is a deliberate constraint: it keeps the game to a single file with one
script tag, and it is why things like the lofted vehicle bodies and the
posterising shader injection are written out by hand rather than pulled from a
helper.

## Fonts — SIL Open Font License 1.1

Chakra Petch and Azeret Mono, served from Google Fonts.
<https://fonts.google.com/specimen/Chakra+Petch> ·
<https://fonts.google.com/specimen/Azeret+Mono>

Both are under the OFL, which permits this use. They are linked rather than
vendored, so an offline install falls back to the system stack named alongside
them in the CSS.
