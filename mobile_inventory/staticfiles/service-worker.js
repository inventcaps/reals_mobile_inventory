const CACHE_NAME = "inventory-cache-v1";
const urlsToCache = [
  "/dashboard/",
  "/products/stock/",
  "/static/css/bootstrap.min.css",
  "/static/js/bootstrap.bundle.min.js"
];

// Install → cache files
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("Caching important files");
      return cache.addAll(urlsToCache);
    })
  );
});

// Activate → cleanup old cache if any
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
});

// Fetch → serve from cache if offline
self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
