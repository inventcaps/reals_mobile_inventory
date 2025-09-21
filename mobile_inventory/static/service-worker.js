const CACHE_NAME = "inventory-cache-v1";
const urlsToCache = [
  "/dashboard/",
  "/products/stock/",
  "/raw/stock/",
  "/static/css/bootstrap.min.css",
  "/static/js/bootstrap.bundle.min.js"
];

// Install → cache initial files
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("✅ Caching important files");
      return cache.addAll(urlsToCache);
    })
  );
});

// Activate → cleanup old cache kung meron
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log("🗑 Deleting old cache:", key);
            return caches.delete(key);
          }
        })
      )
    )
  );
});

// Fetch → stale-while-revalidate strategy
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request)
        .then(networkResponse => {
          // Update cache kung may bagong version
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          });
        })
        .catch(() => {
          // Kung offline at walang cache
          return cachedResponse;
        });

      return cachedResponse || fetchPromise;
    })
  );
});
