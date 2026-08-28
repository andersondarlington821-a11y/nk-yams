# 🚀 Getting Started — NK's Yams Platform

## What You Need to Do (3 Steps)

### Step 1: Install Docker Desktop
📥 **Download:** https://docker.com/get-started/  
✅ **Install & Start** Docker Desktop  
⏱️ Takes ~5 minutes

---

### Step 2: Get Your Neon Database
🌐 **Sign up:** https://console.neon.tech (FREE)

1. Click **"Create Project"**
2. Name it: `nk-yams`
3. Click **"Connection Details"** 
4. Copy the connection string (looks like this):
   ```
   postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

5. Open the `.env` file in this folder
6. Replace the `DATABASE_URL` line with your actual connection string:
   ```
   DATABASE_URL=postgresql://your-actual-string-here
   ```

⏱️ Takes ~3 minutes

---

### Step 3: Start the Server
💻 **Right-click** `start-docker.ps1` → **"Run with PowerShell"**

OR open PowerShell in this folder and run:
```powershell
.\start-docker.ps1
```

⏱️ First build takes ~2 minutes, then instant on future runs

---

## ✅ You're Done!

Your platform is now live:

| Page | URL | Password |
|------|-----|----------|
| **Customer Site** | http://localhost:8080/index.html | — |
| **Register** | http://localhost:8080/register.html | — |
| **Login** | http://localhost:8080/login.html | — |
| **Admin Dashboard** | http://localhost:8080/admin.html | `Nwauwankeiruka1981` |
| **API Server** | http://localhost:5000 | — |

---

## 🎯 What Works Right Now

✅ Customers can register accounts  
✅ Customers can log in  
✅ Customers can place yam orders  
✅ Customers can track their orders  
✅ Admin can view all orders  
✅ Admin can update order status  
✅ Admin can see customer list  
✅ Admin sees live dashboard stats  
✅ All data saves to Neon PostgreSQL  
✅ Secure JWT authentication  
✅ Passwords are encrypted  

---

## 🔧 Common Issues

### "Docker is not running"
→ Open Docker Desktop from Start menu and wait for it to say "Running"

### "DATABASE_URL is not configured"
→ You haven't added your Neon connection string to the `.env` file yet

### Server starts but pages show errors
→ Make sure the frontend is running too:
```powershell
powershell -ExecutionPolicy Bypass -File serve.ps1
```

### Can't log into admin panel
→ Password is `Nwauwankeiruka1981` (case-sensitive)  
→ Make sure `ADMIN_TOKEN` in `.env` matches the token in `public/admin.html`

---

## 📱 Want WhatsApp Order Notifications?

1. Go to https://green-api.com and create a free account
2. Get your **Instance ID** and **Token**
3. Add them to `.env`:
   ```
   GREEN_API_ID=your_instance_id
   GREEN_API_TOKEN=your_token
   ADMIN_WHATSAPP=2347034547179@c.us
   WHATSAPP_ENABLED=true
   ```
4. Restart the server: `.\start-docker.ps1`

Now you'll get instant WhatsApp messages when customers place orders!

---

## 🌐 Deploy to Production (Render.com)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "NK's Yams platform"
   git push
   ```

2. **Deploy on Render:**
   - Go to https://render.com
   - New Web Service → Connect your repo
   - Build: `npm install`
   - Start: `node server.js`
   - Add all `.env` variables in Environment section
   - Deploy!

3. **Update frontend files** with your Render URL:
   - In `public/index.html`, `register.html`, `login.html`, `admin.html`
   - Change `http://localhost:5000` to `https://your-app.onrender.com`

---

## 💡 Development Tips

### View live server logs
```powershell
docker logs -f nks-yams-api
```

### Stop the server
```powershell
docker stop nks-yams-api
```

### Restart after code changes
```powershell
.\start-docker.ps1
```
(It automatically rebuilds if you changed the code)

### Test the API directly
```powershell
curl http://localhost:5000/health
```

---

## 📚 Next Steps

1. ✅ **Test the customer flow:**
   - Register an account
   - Log in
   - Place an order
   - Check "My Orders"

2. ✅ **Test the admin panel:**
   - Log into admin.html
   - View the order you just placed
   - Update its status to "confirmed"
   - Check the dashboard stats

3. ✅ **Customize:**
   - Edit prices in `public/index.html`
   - Change admin password in `public/admin.html`
   - Update branding/colors in the CSS

4. ✅ **Deploy to production** (see instructions above)

---

## 🆘 Need Help?

1. Check `README.md` for full documentation
2. Look at server logs: `docker logs -f nks-yams-api`
3. Test health endpoint: http://localhost:5000/health
4. Verify `.env` has all required values

---

**🎉 You're all set! Start taking orders!**
