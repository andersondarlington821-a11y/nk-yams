# NK's Yams — Complete Setup Guide

The frontend is already running at http://localhost:8080 via `serve.ps1`.
The backend needs Docker (or Node.js) to run on port 5000.

---

## QUICKEST PATH — Docker (Recommended)

### Step 1: Install Docker Desktop
Go to https://docker.com/get-started/ and download Docker Desktop for Windows.
Install it, then **start Docker Desktop** from the Start menu. Wait for it to show "Docker Desktop is running" in the system tray.

### Step 2: Set up Neon Database (free)
1. Go to https://console.neon.tech — sign up (free)
2. Create a project called "nk-yams"
3. Click **Connection Details** → copy the connection string:
   ```
   postgresql://user:pass@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 3: Add your database URL to .env
Open the `.env` file in the project root and replace the DATABASE_URL line:
```
DATABASE_URL=postgresql://your-actual-neon-connection-string-here
```

### Step 4: Run the one-click start script
Open PowerShell in the project folder and run:
```powershell
.\start-docker.ps1
```
This will:
- Find Docker automatically
- Build the image
- Start the container on port 5000
- Open your browser

That's it. Your backend will be live at http://localhost:5000

---

## ALTERNATIVE PATH — Node.js directly (no Docker)

### Step 1: Install Node.js
Go to https://nodejs.org → download LTS → install → restart PowerShell.

### Step 2: Set DATABASE_URL in .env (same as above)

### Step 3: Run
```powershell
npm install
node server.js
```

---

## Step 5 (either path): Start the frontend preview

Open a **second** PowerShell window:
```powershell
powershell -ExecutionPolicy Bypass -File serve.ps1
```

---

## Access your app

| Page          | URL                                       |
|---------------|-------------------------------------------|
| Customer site | http://localhost:8080/index.html          |
| Register      | http://localhost:8080/register.html       |
| Login         | http://localhost:8080/login.html          |
| Admin panel   | http://localhost:8080/admin.html          |
| Admin password| `Nwauwankeiruka1981`                      |
| API health    | http://localhost:5000/health              |

---

## Deploying to Render (production)

1. Push project to GitHub
2. Go to https://render.com → New Web Service → connect repo
3. **Build command:** `npm install`
4. **Start command:** `node server.js`
5. Add all `.env` values as Environment Variables in Render's dashboard
6. Change `const API = 'http://localhost:5000'` in these files to your Render URL:
   - `public/index.html`
   - `public/register.html`
   - `public/login.html`
   - `public/admin.html`

---

## Docker quick-reference commands

```powershell
# View live logs
docker logs -f nks-yams-api

# Stop the container
docker stop nks-yams-api

# Restart the container
docker start nks-yams-api

# Rebuild after code changes
.\start-docker.ps1

# Remove everything and start fresh
docker stop nks-yams-api; docker rm nks-yams-api; docker rmi nks-yams
.\start-docker.ps1
```

---

## All API routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | /health | none | Server health check |
| POST | /api/auth/register | none | Create account |
| POST | /api/auth/login | none | Login |
| GET | /api/auth/me | JWT | Get current user |
| POST | /api/orders | JWT | Place order |
| GET | /api/orders/mine | JWT | My orders |
| GET | /api/orders/:id | none | Track order |
| GET | /api/admin/orders | Admin token | All orders |
| POST | /api/admin/orders/:id/status | Admin token | Update status |
| DELETE | /api/admin/orders/:id | Admin token | Delete order |
| GET | /api/admin/users | Admin token | All customers |
| DELETE | /api/admin/users/:id | Admin token | Remove customer |
| GET | /api/admin/stats | Admin token | Dashboard stats |
