# -*- coding: utf-8 -*-
"""Generate the PWA shell for Coilover: icons, manifest, service worker.
Icons are drawn from primitives rather than loaded, so there is no asset to
lose. Run once, or again if the palette changes."""
import io, os, zlib, struct

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.makedirs('app/icons', exist_ok=True)


def write_png(path, S):
    SKY_HI = (0x6a, 0x4b, 0x7e)
    SKY_LO = (0xef, 0x9b, 0x4f)
    SUN    = (0xff, 0xe0, 0xa8)
    DUNE   = (0xd7, 0x9a, 0x55)
    DUNE_D = (0xb9, 0x74, 0x3a)
    TRUCK  = (0x17, 0x94, 0x8a)
    TYRE   = (0x24, 0x26, 0x2c)
    SPRING = (0xf0, 0xa0, 0x22)

    px = [[SKY_HI] * S for _ in range(S)]
    u = S / 32.0

    # sky gradient, banded on purpose so it reads as low poly
    for y in range(S):
        t = y / float(S)
        if t < 0.62:
            k = t / 0.62
            px[y] = [(int(SKY_HI[0] + (SKY_LO[0] - SKY_HI[0]) * k),
                      int(SKY_HI[1] + (SKY_LO[1] - SKY_HI[1]) * k),
                      int(SKY_HI[2] + (SKY_LO[2] - SKY_HI[2]) * k))] * S

    def rect(x0, y0, x1, y1, c):
        for y in range(max(0, int(y0)), min(S, int(y1))):
            for x in range(max(0, int(x0)), min(S, int(x1))):
                px[y][x] = c

    def disc(cx, cy, r, c):
        for y in range(max(0, int(cy - r)), min(S, int(cy + r) + 1)):
            for x in range(max(0, int(cx - r)), min(S, int(cx + r) + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    px[y][x] = c

    def tri(p0, p1, p2, c):
        xs = [p0[0], p1[0], p2[0]]; ys = [p0[1], p1[1], p2[1]]
        for y in range(max(0, int(min(ys))), min(S, int(max(ys)) + 1)):
            for x in range(max(0, int(min(xs))), min(S, int(max(xs)) + 1)):
                d1 = (x - p1[0]) * (p0[1] - p1[1]) - (p0[0] - p1[0]) * (y - p1[1])
                d2 = (x - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (y - p2[1])
                d3 = (x - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (y - p0[1])
                if not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0)):
                    px[y][x] = c

    disc(22 * u, 15 * u, 4.2 * u, SUN)
    # two faceted dune ridges
    tri((0, 22 * u), (13 * u, 14.5 * u), (32 * u, 21 * u), DUNE_D)
    rect(0, 21 * u, S, S, DUNE_D)
    tri((0, 25 * u), (17 * u, 19 * u), (32 * u, 24.5 * u), DUNE)
    rect(0, 24.5 * u, S, S, DUNE)
    # the truck, blocky and side on
    rect(7.5 * u, 20.0 * u, 24.5 * u, 24.0 * u, TRUCK)
    rect(11.0 * u, 16.6 * u, 20.0 * u, 20.2 * u, TRUCK)
    rect(9.6 * u, 23.6 * u, 10.6 * u, 26.4 * u, SPRING)
    rect(21.4 * u, 23.6 * u, 22.4 * u, 26.4 * u, SPRING)
    disc(10.1 * u, 26.4 * u, 3.5 * u, TYRE)
    disc(21.9 * u, 26.4 * u, 3.5 * u, TYRE)

    raw = b''.join(b'\x00' + bytes(v for pxl in row for v in pxl) for row in px)

    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)

    io.open(path, 'wb').write(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', S, S, 8, 2, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(raw, 9))
        + chunk(b'IEND', b''))


write_png('app/icons/icon-192.png', 192)
write_png('app/icons/icon-512.png', 512)

io.open('app/manifest.webmanifest', 'w', encoding='utf-8', newline='\n').write('''{
  "name": "Coilover",
  "short_name": "Coilover",
  "description": "A desert basin, a big truck, and suspension you can watch working.",
  "start_url": ".",
  "scope": ".",
  "display": "fullscreen",
  "orientation": "any",
  "background_color": "#1a1016",
  "theme_color": "#17121b",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable" }
  ]
}
''')

io.open('app/sw.js', 'w', encoding='utf-8', newline='\n').write('''/* Coilover offline shell.
   The page is network first, so an update lands the moment you open it with a
   signal. three.js and the icons are cache first because they never change.
   Both fall back to the cache when there is no signal at all. */
var CACHE = 'coilover-v1';
var SHELL = ['./', './index.html', './vendor/three.min.js', './manifest.webmanifest',
             './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(SHELL); })
    .then(function(){ return self.skipWaiting(); }));
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.map(function(k){ return k === CACHE ? null : caches.delete(k); }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener('fetch', function(e){
  var req = e.request;
  if (req.method !== 'GET') return;
  var path = new URL(req.url).pathname;
  var isPage = req.mode === 'navigate' || path === '/' || /index\\.html$/.test(path);

  if (isPage) {
    e.respondWith(fetch(req).then(function(res){
      var copy = res.clone();
      caches.open(CACHE).then(function(c){ c.put('./index.html', copy); });
      return res;
    }).catch(function(){ return caches.match('./index.html'); }));
    return;
  }
  e.respondWith(caches.match(req).then(function(hit){
    return hit || fetch(req).then(function(res){
      var copy = res.clone();
      caches.open(CACHE).then(function(c){ c.put(req, copy); });
      return res;
    });
  }));
});
''')

print('icons:', os.path.getsize('app/icons/icon-192.png'), os.path.getsize('app/icons/icon-512.png'))
print('manifest and sw written')
