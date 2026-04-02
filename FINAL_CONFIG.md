# 🚀 Worldmine Final Configuration Guide

## 📋 Essential Environment Variables (5 Variables Only)

Copy these **exact 5 environment variables** into your Vercel and Render dashboards:

---

### 🔧 Vercel Frontend Variables

#### 1. Supabase URL
```
VITE_SUPABASE_URL=https://your-project.supabase.co
```
**Where to get:** Supabase Project Settings → API → Project URL

#### 2. Supabase Anonymous Key
```
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key-here
```
**Where to get:** Supabase Project Settings → API → anon public

#### 3. Backend API URL
```
VITE_API_URL=https://your-render-app.onrender.com
```
**Where to get:** Render dashboard → Your app → Domain

#### 4. Admin User ID
```
VITE_ADMIN_USER_ID=your-admin-user-id-here
```
**Where to get:** Supabase Authentication → Users → Copy admin user ID

#### 5. Auth Secret
```
VITE_AUTH_SECRET=your-super-secret-auth-key-here
```
**Where to get:** Generate a secure random string (64+ characters)

---

### 🖥️ Render Backend Variables

#### 6. Supabase Service Role Key (Server-only)
```
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here
```
**Where to get:** Supabase Project Settings → API → service_role (NEVER expose to frontend)

#### 7. Environment
```
ENVIRONMENT=production
```

#### 8. Port
```
PORT=8000
```

---

## 🔗 Complete Connection Setup

### Frontend (Vercel) → Backend (Render)
```
Frontend: https://worldmine.vercel.app
Backend:  https://your-app.onrender.com
Database: https://your-project.supabase.co
```

### API Endpoints
```
Health Check: https://your-app.onrender.com/api/health
API Docs:    https://your-app.onrender.com/docs
Root:        https://your-app.onrender.com/
```

---

## ✅ Validation Checklist

### Before Deployment:
- [ ] All 5 frontend variables set in Vercel
- [ ] Service role key set in Render (backend only)
- [ ] Supabase project created and URL confirmed
- [ ] Render app deployed and URL confirmed
- [ ] CORS configured for `https://worldmine.vercel.app`

### After Deployment:
- [ ] Frontend loads at `https://worldmine.vercel.app`
- [ ] Backend responds at `https://your-app.onrender.com/api/health`
- [ ] KeepAlive pings working (check browser console)
- [ ] Supabase connection successful
- [ ] No CORS errors in browser

---

## 🚀 Deployment Commands

### Frontend (Vercel):
```bash
npm run build
vercel --prod
```

### Backend (Render):
```bash
cd ai-agent
pip install -r requirements.txt
python app.py
```

---

## 🔧 Configuration Files

### Frontend Configuration:
- `vercel.json` - SPA routing only
- `vite.config.ts` - Build optimization
- `.env.example` - Environment variable template

### Backend Configuration:
- `ai-agent/app.py` - FastAPI server
- `ai-agent/main.py` - AI agent logic
- `ai-agent/cors_config.py` - CORS settings

---

## 🛡️ Security Notes

### ✅ Safe for Frontend (Vercel):
- `VITE_SUPABASE_URL` - Public project URL
- `VITE_SUPABASE_ANON_KEY` - Public anonymous key
- `VITE_API_URL` - Backend URL
- `VITE_ADMIN_USER_ID` - Admin user ID
- `VITE_AUTH_SECRET` - Frontend auth secret

### ❌ NEVER Expose to Frontend:
- `SUPABASE_SERVICE_ROLE_KEY` - Admin access key
- Database passwords
- Private API keys
- Service credentials

---

## 🎯 Keep-Alive System

The KeepAlive component automatically:
- Pings `/api/health` every 10 minutes
- Prevents Render free tier from sleeping
- Runs invisibly in the background
- Logs status to browser console

**No manual configuration required!**

---

## 📞 Troubleshooting

### Common Issues:

#### 1. CORS Errors
```bash
# Check backend CORS configuration
# Ensure frontend URL is in allowed origins
```

#### 2. Supabase Connection
```bash
# Verify URL and keys are correct
# Check Supabase project status
```

#### 3. Backend Sleeping
```bash
# Check KeepAlive logs in browser console
# Verify /api/health endpoint responds
```

#### 4. Build Failures
```bash
# Clear node_modules and reinstall
npm install
npm run build
```

---

## 🏁 Ready to Deploy!

Once you set these 5 environment variables, Worldmine will be fully operational with:
- ✅ Frontend on Vercel
- ✅ Backend on Render  
- ✅ Database on Supabase
- ✅ Keep-Alive system active
- ✅ CORS properly configured
- ✅ Production-ready build

**Your global mineral trading platform will be live!** 🚀💎🌍
