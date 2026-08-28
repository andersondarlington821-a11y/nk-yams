# 🚀 Deployment Guide — NK's Yams Platform

## Quick Overview
1. ✅ Deploy Backend on Render (get API URL)
2. ✅ Update Frontend API URLs
3. ✅ Deploy Frontend on Vercel
4. ✅ Test Everything

---

## 📦 STEP 1: Deploy Backend on Render

### 1.1 Push Code to GitHub

```powershell
git init
git add .
git commit -m "Initial commit - NK Yams platform"
git remote add origin https://github.com/YOUR_USERNAME/nk-yams.git
git branch -M main
git push -u origin main
```

### 1.2 Deploy on Render

1. Go to **https://render.com**
2. Sign up or login
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name:** `nk-yams-api`
   - **Region:** Select closest region
   - **Branch:** `main`
   - **Root Directory:** (leave blank)
   - **Build Command:** `npm install`
   - **Start Command:** `node server.js`
   - **Instance Type:** Free

6. **Environment Variables** (click "Advanced"):
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_Q5iCbta9WSGT@ep-steep-forest-a2y2fjl8-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require
   JWT_SECRET=nkyam_jwt_super_secret_change_in_prod_2026_CHANGE_THIS
   JWT_EXPIRES=7d
   ADMIN_TOKEN=7Xk9mP2nQ8rS5tU3vW7yZ4bC6dF8gH1jL9
   PORT=5000
   GREEN_API_ID=7107601889
   GREEN_API_TOKEN=5e85cf0d650b451cb3ea6c15bfdde997ae51787937b149c198
   ADMIN_WHATSAPP=2347034547179@c.us
   WHATSAPP_ENABLED=false
   ```

7. Click **"Create Web Service"**

⏱️ **Wait 5-10 minutes** for deployment

You'll get a URL like: **`https://nk-yams-api.onrender.com`**

### 1.3 Test Backend

Visit: `https://nk-yams-api.onrender.com/health`

Should return:
```json
{"status":"OK","timestamp":"...","db":true,"dbTime":"..."}
```

---

## 🌐 STEP 2: Update Frontend API URLs

**IMPORTANT:** Replace `https://nk-yams-api.onrender.com` with YOUR actual Render URL!

Update the `API` constant in these files:

### Files to Update:
1. `public/index.html` (line ~200)
2. `public/register.html` (line ~330)
3. `public/login.html` (line ~195)
4. `public/admin.html` (line ~670)

**Change FROM:**
```javascript
const API = 'http://localhost:5000';
```

**Change TO:**
```javascript
const API = 'https://YOUR-RENDER-URL.onrender.com';
```

### Quick Find & Replace (PowerShell):

```powershell
# Replace localhost with your Render URL in all HTML files
$renderUrl = "https://nk-yams-api.onrender.com"  # UPDATE THIS!
Get-ChildItem public\*.html | ForEach-Object {
    (Get-Content $_.FullName) -replace "http://localhost:5000", $renderUrl | Set-Content $_.FullName
}
```

---

## 📤 STEP 3: Deploy Frontend on Vercel

### 3.1 Create `vercel.json` Config

Already created in root folder! Contains:
```json
{
  "cleanUrls": true,
  "trailingSlash": false,
  "rewrites": [
    { "source": "/", "destination": "/public/index.html" },
    { "source": "/register", "destination": "/public/register.html" },
    { "source": "/login", "destination": "/public/login.html" },
    { "source": "/admin", "destination": "/public/admin.html" }
  ]
}
```

### 3.2 Deploy to Vercel

**Option A: Vercel CLI**

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

Follow prompts:
- Set up and deploy? **Y**
- Which scope? (choose your account)
- Link to existing project? **N**
- Project name? `nk-yams`
- Directory with code? `./`
- Override settings? **N**

**Option B: Vercel Dashboard**

1. Go to **https://vercel.com**
2. Sign up/login with GitHub
3. Click **"Add New..."** → **"Project"**
4. Import your GitHub repository
5. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** (leave empty)
   - **Output Directory:** `public`
6. Click **"Deploy"**

⏱️ **Wait 2-3 minutes**

You'll get a URL like: **`https://nk-yams.vercel.app`**

---

## ✅ STEP 4: Test Your Deployment

### Backend Tests
- Health: `https://YOUR-RENDER-URL.onrender.com/health`
- Should return: `{"status":"OK","db":true}`

### Frontend Tests
1. Visit: `https://nk-yams.vercel.app`
2. Check: Error banner should NOT appear
3. Try: Register new account
4. Try: Login
5. Try: Place an order
6. Try: Admin panel (password: `Nwauwankeiruka1981`)

---

## 🔄 STEP 5: Future Updates

### Update Backend:
```powershell
git add .
git commit -m "Update backend"
git push
```
Render auto-deploys on push! ✅

### Update Frontend:
```powershell
git add .
git commit -m "Update frontend"
git push
```
Vercel auto-deploys on push! ✅

---

## 🆘 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check Render logs: Dashboard → Logs
- Verify DATABASE_URL is correct
- Ensure all environment variables are set

**"Database connection failed"**
- Check Neon database is active
- Verify connection string format
- Try `sslmode=require` without channel_binding

### Frontend Issues

**"Backend server is offline" banner appears**
- Check API URL is correct in HTML files
- Test backend health endpoint manually
- Check CORS settings (should allow all origins)

**Forms don't work**
- Open browser DevTools (F12) → Console
- Check for CORS errors
- Verify API URL has HTTPS (not HTTP)

---

## 📋 Deployment Checklist

### Backend (Render)
- [ ] Code pushed to GitHub
- [ ] Render web service created
- [ ] All environment variables added
- [ ] Build command: `npm install`
- [ ] Start command: `node server.js`
- [ ] Health endpoint returns 200 OK
- [ ] Database connection working

### Frontend (Vercel)
- [ ] API URLs updated in all HTML files
- [ ] vercel.json created
- [ ] Project deployed to Vercel
- [ ] All pages load correctly
- [ ] Forms submit successfully
- [ ] No CORS errors in console

### Final Tests
- [ ] Register new account works
- [ ] Login works
- [ ] Place order works
- [ ] Admin panel loads
- [ ] Database persists data

---

## 🎉 You're Live!

**Frontend:** `https://nk-yams.vercel.app`  
**Backend:** `https://nk-yams-api.onrender.com`  
**Admin:** `https://nk-yams.vercel.app/admin`

**Password:** `Nwauwankeiruka1981`

---

## 💡 Pro Tips

1. **Free Tier Limits:**
   - Render: Backend sleeps after 15 min inactivity (first request slow)
   - Vercel: Unlimited bandwidth for hobby projects

2. **Custom Domains:**
   - Render: Settings → Custom Domain
   - Vercel: Settings → Domains

3. **Monitoring:**
   - Render logs: Real-time in dashboard
   - Vercel analytics: Built-in (upgrade for more)

4. **Security:**
   - Change JWT_SECRET in production
   - Use strong ADMIN_TOKEN
   - Enable WhatsApp notifications

---

**Ready to deploy? Start with Step 1!** 🚀
