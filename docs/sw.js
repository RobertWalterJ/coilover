/* Coilover offline shell.
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
  var isPage = req.mode === 'navigate' || path === '/' || /index\.html$/.test(path);

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
