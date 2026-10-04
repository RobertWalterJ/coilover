/* Coilover offline shell.
   The page is network first, so an update lands the moment you open it with a
   signal. three.js and the icons are cache first because they never change.
   Both fall back to the cache when there is no signal at all. */
var CACHE = 'coilover-v2';
/* All apps share one origin, so only ever touch our own caches. */
var OWN = /^coilover-v\d+$/;
var SHELL = ['./', './index.html', './vendor/three.min.js', './manifest.webmanifest',
             './icons/icon-192.png', './icons/icon-512.png'];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(SHELL); })
    .then(function(){ return self.skipWaiting(); }));
});

self.addEventListener('activate', function(e){
  e.waitUntil(caches.keys().then(function(ks){
    return Promise.all(ks.map(function(k){ return (OWN.test(k) && k !== CACHE) ? caches.delete(k) : null; }));
  }).then(function(){ return self.clients.claim(); }));
});

self.addEventListener('fetch', function(e){
  var req = e.request;
  if (req.method !== 'GET') return;
  var path = new URL(req.url).pathname;
  var isPage = req.mode === 'navigate' || path === '/' || /index\.html$/.test(path);

  if (isPage) {
    e.respondWith(fetch(req).then(function(res){
      var copy = res.clone();
      caches.open(CACHE).then(function(c){ c.put('./index.html', copy); });
      return res;
    }).catch(function(){ return caches.open(CACHE).then(function(c){ return c.match('./index.html'); }); }));
    return;
  }
  /* The manifest is never cached first, so install identity cannot go stale. */
  if (/manifest\.webmanifest$/.test(path)) return;
  e.respondWith(caches.open(CACHE).then(function(c){ return c.match(req); }).then(function(hit){
    return hit || fetch(req).then(function(res){
      var copy = res.clone();
      caches.open(CACHE).then(function(c){ c.put(req, copy); });
      return res;
    });
  }));
});
