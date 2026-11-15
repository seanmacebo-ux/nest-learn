// Nest Learn service worker: network only, no caching (so the app is installable
// in Chrome but phones never get stuck on an old copy, unlike The Nest's old SW).
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => { e.respondWith(fetch(e.request)); });
