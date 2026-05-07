// Road Planner — Service Worker (offline support)
const STATIC_CACHE = 'rp-static-v4';
const TILES_CACHE = 'rp-tiles-v1';
const STATIC_URLS = [
  './route.html',
  
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://cdn.jsdelivr.net/npm/sortablejs@1.15.2/Sortable.min.js'
];

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(STATIC_CACHE).then(cache =>
      Promise.allSettled(STATIC_URLS.map(url =>
        cache.add(new Request(url, { mode: url.startsWith('http') ? 'cors' : 'same-origin' }))
          .catch(e => console.warn('SW precache fail:', url, e))
      ))
    )
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys
        .filter(k => k !== STATIC_CACHE && k !== TILES_CACHE)
        .map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  // Map tiles — cache-first, store on success
  const isTile =
    url.hostname.includes('mt0.google.com') || url.hostname.includes('mt1.google.com') ||
    url.hostname.includes('mt2.google.com') || url.hostname.includes('mt3.google.com') ||
    url.hostname.includes('arcgisonline.com') ||
    url.hostname.includes('tile.openstreetmap.org');
  if (isTile) {
    event.respondWith(
      caches.open(TILES_CACHE).then(async cache => {
        const cached = await cache.match(request);
        if (cached) return cached;
        try {
          const resp = await fetch(request);
          if (resp.ok || resp.type === 'opaque') cache.put(request, resp.clone()).catch(() => {});
          return resp;
        } catch(e) {
          return cached || new Response('', { status: 504 });
        }
      })
    );
    return;
  }

  // OSRM — network-only (route depends on waypoints; not worth caching)
  if (url.hostname.includes('project-osrm.org')) return;

  // Static / app shell — stale-while-revalidate
  if (STATIC_URLS.some(u => request.url.includes(u.replace('./', '')))) {
    event.respondWith(
      caches.match(request).then(cached => {
        const networkPromise = fetch(request).then(resp => {
          if (resp.ok) caches.open(STATIC_CACHE).then(c => c.put(request, resp.clone())).catch(() => {});
          return resp;
        }).catch(() => cached);
        return cached || networkPromise;
      })
    );
    return;
  }

  // Default: try network, fall back to cache if offline
  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
