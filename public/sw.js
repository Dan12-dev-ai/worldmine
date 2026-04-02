const CACHE_NAME = 'worldmine-v1';
const OFFLINE_URL = '/offline.html';

// Assets to cache for offline functionality
const STATIC_ASSETS = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/_next/static/css/app.css',
  '/_next/static/js/app.js'
];

// News cache - cache daily mini news for offline reading
const NEWS_CACHE_NAME = 'worldmine-news-v1';

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME && cacheName !== NEWS_CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - handle requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }

  // Handle news requests
  if (url.pathname.startsWith('/api/market-news')) {
    event.respondWith(handleNewsRequest(request));
    return;
  }

  // Handle static assets
  if (request.destination === 'static' || request.destination === 'image') {
    event.respondWith(handleStaticAsset(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(request));
    return;
  }

  // Default: network first
  event.respondWith(fetch(request));
});

// Handle API requests with network-first strategy
async function handleApiRequest(request) {
  try {
    // Try network first
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed for API request, trying cache');
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response
    return new Response(
      JSON.stringify({ 
        error: 'Network unavailable', 
        offline: true,
        message: 'This request requires an internet connection'
      }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle news requests with cache-first strategy
async function handleNewsRequest(request) {
  const cache = await caches.open(NEWS_CACHE_NAME);
  
  try {
    // Try cache first for news
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      // Update cache in background
      fetch(request).then((response) => {
        if (response.ok) {
          cache.put(request, response.clone());
        }
      });
      
      return cachedResponse;
    }
    
    // Fetch from network
    const response = await fetch(request);
    
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed for news request, trying cache');
    
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return empty news response
    return new Response(
      JSON.stringify({ 
        data: [], 
        offline: true,
        message: 'News unavailable offline'
      }),
      {
        status: 200,
        statusText: 'OK',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  const cache = await caches.open(CACHE_NAME);
  
  // Try cache first
  const cachedResponse = await cache.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    // Fetch from network
    const response = await fetch(request);
    
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Network failed for static asset');
    throw error;
  }
}

// Handle navigation requests
async function handleNavigationRequest(request) {
  try {
    // Try network first
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.log('[SW] Network failed for navigation, serving offline page');
    
    // Serve offline page
    const cachedOfflinePage = await caches.match(OFFLINE_URL);
    if (cachedOfflinePage) {
      return cachedOfflinePage;
    }
    
    // Return basic offline response
    return new Response(
      `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Worldmine - Offline</title>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: #0a0e27;
              color: white;
              display: flex;
              align-items: center;
              justify-content: center;
              min-height: 100vh;
              margin: 0;
              padding: 20px;
              text-align: center;
            }
            .offline-container {
              max-width: 400px;
            }
            h1 { color: #00d4ff; margin-bottom: 20px; }
            .icon { font-size: 64px; margin-bottom: 20px; }
            button {
              background: #00d4ff;
              color: #0a0e27;
              border: none;
              padding: 12px 24px;
              border-radius: 8px;
              cursor: pointer;
              font-weight: bold;
              margin-top: 20px;
            }
            button:hover { background: #00b8e6; }
          </style>
        </head>
        <body>
          <div class="offline-container">
            <div class="icon">🌍</div>
            <h1>Worldmine Offline</h1>
            <p>You're currently offline. Some features may not be available.</p>
            <p>Cached news and marketplace data are still accessible.</p>
            <button onclick="window.location.reload()">Try Again</button>
          </div>
        </body>
      </html>
      `,
      {
        status: 200,
        statusText: 'OK',
        headers: { 'Content-Type': 'text/html' }
      }
    );
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'background-sync-news') {
    event.waitUntil(syncNewsData());
  }
});

// Sync news data in background
async function syncNewsData() {
  try {
    const response = await fetch('/api/market-news');
    const data = await response.json();
    
    const cache = await caches.open(NEWS_CACHE_NAME);
    await cache.put('/api/market-news', new Response(JSON.stringify(data)));
    
    console.log('[SW] News data synced successfully');
  } catch (error) {
    console.log('[SW] News sync failed:', error);
  }
}

// Push notifications (for compliance alerts, news updates)
self.addEventListener('push', (event) => {
  console.log('[SW] Push message received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from Worldmine',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open Worldmine',
        icon: '/icons/checkmark.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/xmark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Worldmine', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification click received');
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('https://worldmine.vercel.app')
    );
  }
});

console.log('[SW] Service worker loaded');
