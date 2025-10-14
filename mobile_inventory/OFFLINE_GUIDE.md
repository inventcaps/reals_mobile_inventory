# 📱 Offline Functionality Guide

## ✅ What Works Offline

Your Real's Mobile Inventory app now supports **full offline viewing** of cached data!

### Scenario: Internet → No Internet

**Step-by-step:**

1. **With Internet (Online):**
   - Open the app and login
   - Visit pages: Dashboard, Product Stock, Raw Stock, History, Sales, Expenses
   - Service Worker automatically caches all pages and data

2. **Internet Lost (Offline):**
   - You'll see: **🔴 Offline** indicator in navbar
   - Orange banner appears: "📡 No Internet - Viewing Cached Data"
   - All previously visited pages remain accessible
   - You can still view all cached lists and data

3. **Internet Returns (Back Online):**
   - Indicator changes to: **🟢 Online**
   - Orange banner disappears
   - Data automatically refreshes with latest from server

---

## 🎯 How It Works

### Service Worker Strategy: **Network First with Cache Fallback**

```
Internet Available:
  ├─ Fetch fresh data from server
  ├─ Update cache with new data
  └─ Display fresh data

Internet Lost:
  ├─ Try to fetch from server (fails)
  ├─ Fallback to cached data
  └─ Display cached data with offline indicator
```

### What Gets Cached:

✅ **Pages:**
- `/dashboard/` - Dashboard with stats
- `/products/stock/` - Product inventory list
- `/raw/stock/` - Raw materials list
- `/history/` - History log
- `/sales/` - Sales records
- `/expenses/` - Expenses records
- `/login/` - Login page

✅ **Assets:**
- Bootstrap CSS & JS (from CDN)
- Google Fonts (Poppins)
- All static files

✅ **Dynamic Data:**
- Product lists with stock levels
- Raw material inventory
- Sales and expense records
- History logs
- All data from visited pages

---

## 🔍 Visual Indicators

### 1. **Connection Status Badge** (Top Right)
- 🟢 Online - Connected to internet
- 🔴 Offline - No internet connection

### 2. **Offline Banner** (Top of Page)
- Orange banner: "📡 No Internet - Viewing Cached Data"
- Only appears when offline

### 3. **Console Logs**
- "✅ Service Worker registered"
- "📦 Serving from cache (offline): /products/stock/"
- "✅ Back online"
- "⚠️ You are offline"

---

## 📋 Testing Offline Mode

### Method 1: Chrome DevTools
1. Open Chrome DevTools (F12)
2. Go to **Network** tab
3. Change "Online" dropdown to **"Offline"**
4. Navigate through the app - everything still works!

### Method 2: Airplane Mode
1. Visit all pages while online
2. Turn on **Airplane Mode**
3. Refresh or navigate - cached pages load!

### Method 3: Disconnect WiFi
1. Browse the app normally
2. Disconnect WiFi/Ethernet
3. Continue browsing cached pages

---

## ⚠️ Limitations

### What DOESN'T Work Offline:

❌ **Login/Logout**
- Requires server authentication
- Must be online to login

❌ **Creating/Editing Data**
- POST/PUT/DELETE requests need internet
- Cannot add products, sales, expenses offline

❌ **Fresh Data**
- Offline mode shows **cached/stale data**
- Data may be outdated until you go back online

❌ **Uncached Pages**
- Pages you never visited while online won't be available
- Must visit at least once while online to cache

---

## 🚀 Best Practices

### For Users:

1. **Pre-cache Important Pages**
   - Visit all pages you need while online
   - This ensures they're available offline

2. **Check Connection Status**
   - Look for 🟢 Online / 🔴 Offline indicator
   - Orange banner means you're viewing old data

3. **Refresh When Back Online**
   - Click browser refresh to get latest data
   - Service Worker auto-updates cache

### For Developers:

1. **Cache Version Updates**
   - Change `CACHE_NAME` version when updating
   - Old caches are automatically deleted

2. **Add New Pages to Cache**
   - Edit `urlsToCache` array in `service-worker.js`
   - Include new routes for offline access

3. **Monitor Cache Size**
   - Large datasets may exceed cache limits
   - Consider pagination for better performance

---

## 🔧 Configuration

### Service Worker Settings

**File:** `static/service-worker.js`

```javascript
// Cache version - increment when updating
const CACHE_NAME = "inventory-cache-v2";

// Pages to cache on install
const urlsToCache = [
  "/dashboard/",
  "/products/stock/",
  "/raw/stock/",
  "/history/",
  "/sales/",
  "/expenses/",
  // Add more pages here
];
```

### Connection Check Interval

**File:** `templates/base.html`

```javascript
// Check connectivity every 5 seconds
setInterval(() => {
  fetch('/dashboard/', { method: 'HEAD', cache: 'no-cache' })
    // ... connectivity check logic
}, 5000); // Change interval here (milliseconds)
```

---

## 📊 Cache Management

### View Cached Data (Chrome DevTools)

1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Cache Storage** → `inventory-cache-v2`
4. See all cached URLs and responses

### Clear Cache

**Option 1: Manual (DevTools)**
1. Application → Cache Storage
2. Right-click cache → Delete

**Option 2: Code Update**
- Change `CACHE_NAME` to `"inventory-cache-v3"`
- Old cache auto-deletes on next visit

**Option 3: Browser Settings**
- Clear browsing data
- Select "Cached images and files"

---

## 🐛 Troubleshooting

### Problem: Offline mode not working

**Solutions:**
1. Check if Service Worker is registered
   - Console should show: "✅ Service Worker registered"
2. Visit pages while online first
3. Check DevTools → Application → Service Workers
4. Unregister and re-register Service Worker

### Problem: Seeing old data even when online

**Solutions:**
1. Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Clear cache and reload
3. Check if 🟢 Online indicator is showing

### Problem: Service Worker not updating

**Solutions:**
1. Change `CACHE_NAME` version number
2. Click "Update" in DevTools → Application → Service Workers
3. Close all tabs and reopen

---

## 📱 PWA Installation

Your app can be installed as a Progressive Web App:

1. **Chrome Desktop:**
   - Click install icon in address bar
   - Or: Menu → Install Real's Inventory

2. **Chrome Mobile:**
   - Menu → Add to Home Screen
   - App opens in standalone mode

3. **Benefits:**
   - Works like native app
   - Better offline experience
   - Faster loading
   - Home screen icon

---

## 🎓 How to Use

### Typical Workflow:

```
Morning (With WiFi):
├─ Login to app
├─ Visit Dashboard
├─ Check Product Stock
├─ Check Raw Materials
└─ Review Sales/Expenses

Field Work (No WiFi):
├─ Open app (works offline!)
├─ View cached product list
├─ Check stock levels
├─ Review history
└─ Take notes for later

Back Online:
├─ App auto-detects connection
├─ Refresh to get latest data
└─ Submit any pending updates
```

---

## 📈 Performance

### Cache Size Limits:
- Chrome: ~6% of free disk space
- Firefox: ~10% of free disk space
- Safari: ~50MB

### Load Times:
- **Online (First Visit):** ~2-3 seconds
- **Online (Cached):** ~500ms
- **Offline (Cached):** ~100-200ms ⚡

---

## 🔒 Security Notes

- Cached data stored locally on device
- Cleared when browser cache is cleared
- Sensitive data should still require authentication
- Logout clears session but not cache

---

## 📞 Support

If offline mode isn't working:

1. Check browser console for errors
2. Verify Service Worker is active
3. Ensure pages were visited while online
4. Try clearing cache and revisiting pages

---

**Last Updated:** October 14, 2025  
**Cache Version:** v2  
**Browser Support:** Chrome, Firefox, Edge, Safari (iOS 11.3+)
