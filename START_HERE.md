# 🚀 START HERE — NK's Yams Platform

## ✅ Current Status

### What's Running Now:
- ✅ **Frontend preview server** — Port 8080 (RUNNING)
  - http://localhost:8080/index.html
  - http://localhost:8080/register.html
  - http://localhost:8080/login.html
  - http://localhost:8080/admin.html

### What's NOT Running:
- ❌ **Backend API server** — Port 5000 (NOT STARTED YET)

---

## 📝 What That Error Message Means

When you see:
> **"Backend server is offline. Registration will not work until the Node.js server is running on port 5000."**

This means:
- ✅ The **HTML pages load** (you can see them)
- ❌ The **backend API is not running** (forms won't work)
- ❌ You can't register, login, or place orders yet

**This is NORMAL!** You just need to start the backend server.

---

## 🔧 How to Fix It (Start the Backend)

### Option 1: Docker (Recommended — 3 Steps)

#### Step 1: Install Docker Desktop
📥 Download: https://docker.com/get-started/  
⏱️ 5 minutes

#### Step 2: Get Neon Database URL
1. Go to https://console.neon.tech (free signup)
2. Create project
3. Copy the connection string (looks like this):
   ```
   postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Open the `.env` file in this folder
5. Replace the `DATABASE_URL` line with your actual connection string

⏱️ 3 minutes

#### Step 3: Start Backend
Open PowerShell in this folder and run:
```powershell
.\start-docker.ps1
```

⏱️ 2 minutes first time, instant after

---

### Option 2: Node.js Directly (No Docker)

#### Step 1: Install Node.js
📥 Download from: https://nodejs.org (get the LTS version)  
⏱️ 5 minutes

#### Step 2: Get Neon Database (same as above)
Add your DATABASE_URL to `.env` file

#### Step 3: Install Dependencies & Start
```powershell
npm install
node server.js
```

---

## ✅ Once Backend is Running

You'll see:
```
✅  Server running at http://localhost:5000
✅  Connected — DB time: 2026-08-04...
```

Then **refresh your browser** and:
- ✅ Registration will work
- ✅ Login will work
- ✅ Orders will work
- ✅ Admin dashboard will load data
- ✅ The error banner will disappear

---

## 🌐 Complete URL Map

| Page | URL | Status | Needs Backend? |
|------|-----|--------|----------------|
| Order Form | http://localhost:8080/index.html | ✅ Loads | ✅ Yes (to submit orders) |
| Register | http://localhost:8080/register.html | ✅ Loads | ✅ Yes (to create account) |
| Login | http://localhost:8080/login.html | ✅ Loads | ✅ Yes (to authenticate) |
| Admin | http://localhost:8080/admin.html | ✅ Loads | ✅ Yes (to see data) |
| API Health | http://localhost:5000/health | ❌ Not running | — |

---

## 🆘 Quick Troubleshooting

### "Backend server is offline" — This is your current issue
**Fix:** Start the backend (see instructions above)

### Docker won't start
**Fix:** Make sure Docker Desktop is running (check system tray)

### "DATABASE_URL is not configured"
**Fix:** Add your Neon connection string to `.env` file

### Pages show but forms don't work
**Fix:** Backend is not running — run `.\start-docker.ps1`

---

## 📚 More Help

- **Quick Start:** `GETTING_STARTED.md` (3-step guide)
- **Full Docs:** `README.md` (everything explained)
- **Setup Guide:** `SETUP.md` (detailed instructions)
- **Commands:** `QUICK_REFERENCE.txt` (one-page cheat sheet)

---

## 🎯 What to Do Right Now

1. ✅ **Install Docker Desktop** (if you haven't)
2. ✅ **Get Neon database URL** and add to `.env`
3. ✅ **Run** `.\start-docker.ps1`
4. ✅ **Refresh browser** — everything will work!

That's it! 🎉
