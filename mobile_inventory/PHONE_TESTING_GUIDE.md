# 📱 Paano I-test sa Phone - Complete Guide

## ✅ Your Computer's IP Address

**WiFi IP:** `192.168.1.197`

---

## 🚀 Step-by-Step Instructions

### Step 1: Update ALLOWED_HOSTS

Kailangan i-allow ang IP address mo sa Django settings.

**Option A: Create .env file (Recommended)**

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file and update this line:
   ```
   ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.197
   ```

**Option B: Temporary (Quick Test)**

Edit `settings.py` line 18:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,192.168.1.197', cast=Csv())
```

---

### Step 2: Run Server with 0.0.0.0

Kailangan i-bind sa lahat ng network interfaces:

```bash
python manage.py runserver 0.0.0.0:8001
```

**Important:** Use `0.0.0.0` instead of `localhost`!

---

### Step 3: Connect Phone to Same WiFi

1. **Computer WiFi:** Connected to your home WiFi
2. **Phone WiFi:** Connect to SAME WiFi network
3. Both devices must be on: **Same network**

---

### Step 4: Open sa Phone Browser

Sa phone mo, open any browser (Chrome, Safari, etc.):

```
http://192.168.1.197:8001
```

Or try:
```
http://192.168.1.197:8001/dashboard/
```

---

## 🔥 Quick Commands

### Full Setup:

```bash
# 1. Create .env file
copy .env.example .env

# 2. Edit .env and add:
# ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.197

# 3. Run server
python manage.py runserver 0.0.0.0:8001
```

### Access URLs:

- **From Computer:** http://localhost:8001
- **From Phone:** http://192.168.1.197:8001

---

## 🧪 Testing Offline Mode sa Phone

### Step 1: Cache the Pages (Online)
1. Open http://192.168.1.197:8001 sa phone
2. Login
3. Visit all pages:
   - Dashboard
   - Product Stock
   - Raw Materials
   - History
   - Sales
   - Expenses

### Step 2: Go Offline
1. Turn on **Airplane Mode** sa phone
2. Or disconnect from WiFi

### Step 3: Test Offline Access
1. Open the app (should still work!)
2. Navigate through cached pages
3. See the **🔴 Offline** indicator
4. Orange banner: "📡 No Internet - Viewing Cached Data"

### Step 4: Go Back Online
1. Turn off Airplane Mode
2. Indicator changes to **🟢 Online**
3. Data refreshes automatically

---

## 🔧 Troubleshooting

### Problem: "This site can't be reached"

**Solutions:**

1. **Check if server is running**
   ```bash
   python manage.py runserver 0.0.0.0:8001
   ```

2. **Check firewall**
   - Windows Firewall might be blocking
   - Allow Python through firewall

3. **Verify same WiFi**
   - Computer and phone on same network
   - Not using mobile data

4. **Check IP address**
   - Run `ipconfig` again
   - IP might have changed
   - Use the WiFi adapter IP (192.168.1.x)

### Problem: "DisallowedHost" error

**Solution:**

Add your IP to ALLOWED_HOSTS in `.env`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.197
```

Then restart server.

### Problem: Can't access from phone but works on computer

**Solutions:**

1. **Disable Windows Firewall temporarily**
   - Control Panel → Windows Defender Firewall
   - Turn off (for testing only)

2. **Or add firewall rule:**
   ```bash
   netsh advfirewall firewall add rule name="Django Dev Server" dir=in action=allow protocol=TCP localport=8001
   ```

3. **Check antivirus**
   - Some antivirus blocks incoming connections
   - Temporarily disable or add exception

---

## 📱 Install as PWA on Phone

Once you can access the app:

### Android (Chrome):
1. Open http://192.168.1.197:8001
2. Menu (⋮) → "Add to Home screen"
3. App installs like native app!

### iOS (Safari):
1. Open http://192.168.1.197:8001
2. Share button → "Add to Home Screen"
3. App appears on home screen

**Benefits:**
- Works offline
- Fullscreen mode
- Faster loading
- Looks like native app

---

## 🌐 Alternative: Use ngrok (Internet Access)

If same WiFi doesn't work, use ngrok for public URL:

### Step 1: Install ngrok
Download from: https://ngrok.com/download

### Step 2: Run ngrok
```bash
ngrok http 8001
```

### Step 3: Get Public URL
Ngrok gives you a URL like:
```
https://abc123.ngrok.io
```

### Step 4: Update ALLOWED_HOSTS
Add ngrok URL to `.env`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,abc123.ngrok.io
```

### Step 5: Access from Phone
Use the ngrok URL on any device, anywhere!

**Note:** Free ngrok URLs change every restart.

---

## 📊 Network Requirements

### Same WiFi Method:
- ✅ Free
- ✅ Fast (local network)
- ✅ No internet needed
- ❌ Only works on same WiFi

### ngrok Method:
- ✅ Works anywhere
- ✅ Public URL
- ❌ Requires internet
- ❌ Free tier has limits

---

## 🔒 Security Notes

**For Testing Only:**

- Don't expose to public internet with DEBUG=True
- Use ngrok only for testing
- Remove your IP from ALLOWED_HOSTS after testing
- For production, use proper hosting

---

## 📝 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  PHONE TESTING QUICK REFERENCE          │
├─────────────────────────────────────────┤
│  Your IP: 192.168.1.197                 │
│  Port: 8001                             │
│                                         │
│  Command:                               │
│  python manage.py runserver 0.0.0.0:8001│
│                                         │
│  Phone URL:                             │
│  http://192.168.1.197:8001              │
│                                         │
│  Requirements:                          │
│  ✓ Same WiFi network                    │
│  ✓ Firewall allowed                     │
│  ✓ ALLOWED_HOSTS updated                │
└─────────────────────────────────────────┘
```

---

## 🎯 Complete Testing Workflow

```
1. Update .env
   └─ Add IP to ALLOWED_HOSTS

2. Start server
   └─ python manage.py runserver 0.0.0.0:8001

3. Connect phone to WiFi
   └─ Same network as computer

4. Open on phone
   └─ http://192.168.1.197:8001

5. Test online features
   └─ Login, browse all pages

6. Test offline mode
   └─ Airplane mode, still works!

7. Install as PWA (optional)
   └─ Add to Home Screen
```

---

**Last Updated:** October 14, 2025  
**Your WiFi IP:** 192.168.1.197  
**Server Port:** 8001
