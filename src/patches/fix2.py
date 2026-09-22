# -*- coding: utf-8 -*-
"""Lambert lights per vertex in three.js, so it silently ignores flatShading
and the whole scene came out smooth. Phong lights per fragment and does
support it. Shininess 0 with black specular keeps it matte, so this is
Lambert's look plus real facets."""
import io, re

p = 'game.html'
s = io.open(p, encoding='utf-8').read()

before = s.count('MeshLambertMaterial')
s = s.replace('new THREE.MeshLambertMaterial({',
              'new THREE.MeshPhongMaterial({shininess:0,specular:0x000000,')
after = s.count('MeshLambertMaterial')

note_old = """  /* flatShading derives the facet normal in the fragment shader, so the
     low-poly look costs nothing on top of an indexed mesh */"""
note_new = """  /* Phong shades per fragment, so flatShading can derive the facet normal
     from screen space derivatives. That means the low poly look works on an
     indexed mesh, at a quarter of the vertex memory of a non indexed one. */"""
if note_old in s:
    s = s.replace(note_old, note_new, 1)

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('Lambert references before:', before, ' after:', after)
print('Phong materials now:', s.count('MeshPhongMaterial'))
