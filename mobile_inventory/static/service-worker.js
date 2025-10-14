const CACHE_NAME = "inventory-cache-v2";
const urlsToCache = [
  "/dashboard/",
  "/products/stock/",
  "/raw/stock/",
  "/history/",
  "/sales/",
  "/expenses/",
  "/login/",
  // CDN resources for offline use
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
  "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap"
];

// Install → cache initial files
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("✅ Caching important files");
      return cache.addAll(urlsToCache).catch(err => {
        console.error("❌ Cache installation failed:", err);
      });
    })
  );
  self.skipWaiting();
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
  return self.clients.claim();
});

// Fetch → Network First with Cache Fallback (para sa dynamic data)
self.addEventListener("fetch", event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip caching for non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  event.respondWith(
    // Try network first
    fetch(request)
      .then(networkResponse => {
        // Clone the response
        const responseToCache = networkResponse.clone();
        
        // Cache successful responses (200-299)
        if (networkResponse.ok) {
          caches.open(CACHE_NAME).then(cache => {
            cache.put(request, responseToCache);
          });
        }
        
        return networkResponse;
      })
      .catch(() => {
        // Network failed, try cache
        return caches.match(request).then(cachedResponse => {
          if (cachedResponse) {
            console.log("📦 Serving from cache (offline):", url.pathname);
            return cachedResponse;
          }
          
          // No cache available, return offline page for HTML requests
          if (request.headers.get('accept').includes('text/html')) {
            return new Response(
              `<!DOCTYPE html>
              <html>
              <head>
                <title>Offline - Real's Inventory</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                  body {
                    font-family: 'Poppins', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(to bottom, #FFE8B6 10%, #AED09E 50%, #77B254 100%);
                  }
                  .offline-card {
                    background: rgba(255, 255, 255, 0.9);
                    padding: 2rem;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                  }
                  h1 { color: #2f3e46; margin-bottom: 1rem; }
                  p { color: #555; }
                  button {
                    background: #77B254;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 10px;
                    cursor: pointer;
                    margin-top: 1rem;
                  }
                </style>
              </head>
              <body>
                <div class="offline-card">
                  <h1>📡 No Internet Connection</h1>
                  <p>You're offline. Please check your connection.</p>
                  <p>Cached pages are still available.</p>
                  <button onclick="window.history.back()">← Go Back</button>
                  <button onclick="location.reload()">🔄 Retry</button>
                </div>
              </body>
              </html>`,
              {
                headers: { 'Content-Type': 'text/html' }
              }
            );
          }
          
          // For other requests, return error
          return new Response('Offline - No cached data available', {
            status: 503,
            statusText: 'Service Unavailable'
          });
        });
      })
  );
});
