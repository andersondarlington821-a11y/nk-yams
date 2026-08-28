# NK's Premium Yams — Complete E-commerce Platform

Full-stack yam delivery platform with Node.js/Express backend, Neon PostgreSQL database, JWT authentication, and admin dashboard.

---

## ✅ What's Built

- **Backend API** — Express + PostgreSQL (complete CRUD)
- **Frontend** — Responsive HTML/CSS/JS (register, login, order, track)
- **Admin Dashboard** — Real-time order management + customer analytics
- **Auth System** — JWT tokens + bcrypt password hashing
- **Database** — Neon PostgreSQL (free serverless)
- **WhatsApp Alerts** — Instant order notifications via Green API
- **Docker Ready** — One-command containerized deployment

---

## 🚀 Quick Start (Docker — Recommended)

### 1. Install Docker Desktop
Download from **https://docker.com/get-started/** and start it.

### 2. Get Neon Database URL
1. Go to **https://console.neon.tech** (free signup)
2. Create project → copy connection string
3. Open `.env` and paste it into `DATABASE_URL`

### 3. Run
```powershell
.\start-docker.ps1
```

That's it! Your server will be live at **http://localhost:5000**

---

## 🛠️ Manual Setup (Without Docker)

### Requirements
- Node.js 18+ — https://nodejs.org
- Neon PostgreSQL account — https://console.neon.tech

### Steps
1. **Install dependencies**
   ```powershell
   npm install
   ```

2. **Configure environment**
   ```powershell
   cp .env.example .env
   ```
   Edit `.env` and add your Neon `DATABASE_URL`

3. **Start backend**
   ```powershell
   node server.js
   ```

4. **Start frontend preview** (in a second terminal)
   ```powershell
   powershell -ExecutionPolicy Bypass -File serve.ps1
   ```

---

## 📂 Project Structure

```
NK-s-Premium-sale-main/
├── server.js              # Main Express server
├── db.js                  # Neon PostgreSQL connection + schema
├── helpers.js             # JWT, order ID generator, WhatsApp
├── middleware.js          # Auth middleware (JWT + Admin)
├── package.json           # Node.js dependencies
├── .env                   # Environment variables (you create this)
├── .env.example           # Template for .env
├── Dockerfile             # Docker container config
├── start-docker.ps1       # One-click Docker launcher
├── public/                # Frontend files
│   ├── index.html         # Homepage (order form)
│   ├── register.html      # Customer registration
│   ├── login.html         # Customer login
│   └── admin.html         # Admin dashboard
└── README.md              # This file
```

---

## 🔌 API Endpoints

### Public Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/api/auth/register` | Create customer account |
| `POST` | `/api/auth/login` | Login (returns JWT token) |
| `GET` | `/api/orders/:orderId` | Track order by ID (public) |

### Authenticated Routes (requires JWT token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/auth/me` | Get current user profile |
| `GET` | `/api/orders/mine` | Get my orders |
| `POST` | `/api/orders` | Place new order |

### Admin Routes (requires `X-Admin-Token` header)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/orders` | Get all orders (filter + search) |
| `POST` | `/api/admin/orders/:id/status` | Update order status |
| `DELETE` | `/api/admin/orders/:id` | Delete order |
| `GET` | `/api/admin/users` | Get all customers |
| `DELETE` | `/api/admin/users/:id` | Delete customer |
| `GET` | `/api/admin/stats` | Dashboard statistics |

---

## 🗄️ Database Schema

### `users` Table
```sql
id              SERIAL PRIMARY KEY
user_id         VARCHAR(36) UNIQUE NOT NULL
full_name       VARCHAR(120) NOT NULL
email           VARCHAR(180) UNIQUE NOT NULL
phone           VARCHAR(20)
whatsapp_number VARCHAR(20)
password_hash   TEXT NOT NULL
role            VARCHAR(20) DEFAULT 'customer'
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ
```

### `orders` Table
```sql
id               SERIAL PRIMARY KEY
order_id         VARCHAR(8) UNIQUE NOT NULL
user_id          VARCHAR(36) REFERENCES users(user_id)
customer_name    VARCHAR(120) NOT NULL
phone            VARCHAR(20) NOT NULL
delivery_address TEXT NOT NULL
yam_type         VARCHAR(50) NOT NULL
price_per_tuber  INT NOT NULL
quantity         INT NOT NULL
total_price      INT NOT NULL
status           VARCHAR(30) DEFAULT 'pending'
notes            TEXT
created_at       TIMESTAMPTZ DEFAULT NOW()
updated_at       TIMESTAMPTZ
```

**Statuses:** `pending`, `confirmed`, `dispatched`, `delivered`, `cancelled`

**Yam Types:** `Water Yam`, `Yellow Yam`, `White Yam`

---

## 🔐 Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | ✅ Yes |
| `JWT_SECRET` | Secret key for JWT tokens | Recommended |
| `JWT_EXPIRES` | Token expiry (default: 7d) | No |
| `ADMIN_TOKEN` | Admin panel access token | ✅ Yes |
| `PORT` | Server port (default: 5000) | No |
| `GREEN_API_ID` | WhatsApp API instance ID | Optional |
| `GREEN_API_TOKEN` | WhatsApp API token | Optional |
| `ADMIN_WHATSAPP` | Admin WhatsApp number | Optional |
| `WHATSAPP_ENABLED` | Enable/disable WhatsApp | Optional |

---

## 📱 WhatsApp Notifications (Optional)

Get instant order alerts on WhatsApp:

1. Sign up at **https://green-api.com**
2. Get your `Instance ID` and `Token`
3. Add them to `.env`:
   ```
   GREEN_API_ID=your_instance_id
   GREEN_API_TOKEN=your_token
   ADMIN_WHATSAPP=2347034547179@c.us
   WHATSAPP_ENABLED=true
   ```

---

## 🌐 Deployment (Render)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/nk-yams.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to **https://render.com** → New Web Service
2. Connect your GitHub repo
3. **Build Command:** `npm install`
4. **Start Command:** `node server.js`
5. Add all `.env` variables in Render's Environment section
6. Deploy!

### 3. Update Frontend API URL
In these files, change `http://localhost:5000` to your Render URL:
- `public/index.html`
- `public/register.html`
- `public/login.html`
- `public/admin.html`

---

## 🐳 Docker Commands

```powershell
# Start server (builds image if needed)
.\start-docker.ps1

# View live logs
docker logs -f nks-yams-api

# Stop server
docker stop nks-yams-api

# Restart server
docker start nks-yams-api

# Rebuild from scratch
docker stop nks-yams-api
docker rm nks-yams-api
docker rmi nks-yams
.\start-docker.ps1
```

---

## 🔧 Development

### Run in development mode (auto-restart on file changes)
```powershell
npm run dev
```

### Test API health
```powershell
curl http://localhost:5000/health
```

### Access admin panel
1. Open **http://localhost:8080/admin.html**
2. Password: `Nwauwankeiruka1981`

---

## 📊 Features

✅ Customer registration + login  
✅ JWT authentication  
✅ Place yam orders (3 types, custom quantity)  
✅ Track orders by ID  
✅ Admin dashboard with real-time stats  
✅ Order management (update status, add notes, delete)  
✅ Customer management (view all, search, delete)  
✅ WhatsApp order notifications  
✅ Responsive mobile-friendly UI  
✅ Secure password hashing (bcrypt)  
✅ PostgreSQL with automatic migrations  
✅ Docker containerized  
✅ Production-ready  

---

## 🆘 Troubleshooting

### "DATABASE_URL is not configured"
→ Add your Neon connection string to `.env`

### "Docker is not running"
→ Start Docker Desktop from the Start menu

### "npm install" fails
→ Delete `node_modules` and `package-lock.json`, then run `npm install` again

### Admin panel shows "Authentication failed"
→ Check that `ADMIN_TOKEN` in `.env` matches the one in `admin.html`

### Orders not appearing in admin panel
→ Check browser console for errors  
→ Verify `DATABASE_URL` is correct  
→ Check server logs: `docker logs nks-yams-api`

---

## 📝 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs: `docker logs -f nks-yams-api`
3. Test the health endpoint: `http://localhost:5000/health`

---

**Built with ❤️ for NK's Premium Yams**
