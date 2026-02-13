# Free PostgreSQL Database Setup (2-3 Minutes)

## Recommended: Neon (Serverless PostgreSQL)

### Why Neon?
- ✅ Free tier: 0.5GB storage (enough for development)
- ✅ No credit card required
- ✅ Auto-scaling to zero (no cost when idle)
- ✅ Setup time: 2-3 minutes
- ✅ Always-on, no sleep/wake delays

---

## Step-by-Step Setup

### Step 1: Create Neon Account (30 seconds)
1. Go to: https://neon.tech
2. Click **"Sign Up"** button (top right)
3. Choose **"Continue with Google"** or enter email
4. Verify email if needed

### Step 2: Create Database (1 minute)
1. After login, you'll see **"Create a project"** screen
2. Fill in:
   - **Project name**: `contextmeet-db` (or any name)
   - **PostgreSQL version**: `15` (recommended)
   - **Region**: Choose closest to you (e.g., US East, EU West)
3. Click **"Create project"**
4. Wait 10-15 seconds for provisioning

### Step 3: Get Connection String (30 seconds)
1. You'll see **"Connection Details"** immediately after creation
2. Look for **"Connection string"** section
3. Copy the string that looks like:
   ```
   postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **SAVE THIS** - you'll need it twice (for `DATABASE_URL` and `DATABASE_ASYNC_URL`)

### Step 4: Modify for Async Support (15 seconds)
You need TWO connection strings:

**For `DATABASE_URL` (sync):**
```bash
postgresql://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**For `DATABASE_ASYNC_URL` (async):**
```bash
postgresql+asyncpg://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

**ONLY DIFFERENCE:** Add `+asyncpg` after `postgresql`

---

## Update Your .env File

Open `backend/.env` and add:

```env
# Database Configuration (Neon - Free Online PostgreSQL)
DATABASE_URL=postgresql://your-username:your-password@ep-xyz-123.region.aws.neon.tech/neondb?sslmode=require
DATABASE_ASYNC_URL=postgresql+asyncpg://your-username:your-password@ep-xyz-123.region.aws.neon.tech/neondb?sslmode=require
```

**Replace the connection strings with your actual values from Neon dashboard!**

---

## Verify Connection (After Installing Dependencies)

After running `pip install -r requirements.txt`, test the connection:

```python
# test_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from backend.app.core.config import settings

async def test_connection():
    engine = create_async_engine(settings.DATABASE_ASYNC_URL)
    async with engine.connect() as conn:
        result = await conn.execute("SELECT version();")
        version = result.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run: `python test_db.py`

---

## Alternative Free Options

### Option 2: Supabase (If you need more features)
- Free tier: 500MB database + auth + storage
- Setup: https://supabase.com
- Connection string format same as Neon
- Takes ~5 minutes (more features = more setup)

### Option 3: Railway (If you need flexibility)
- Free tier: $5/month credit (database + deployments)
- Setup: https://railway.app
- Good for full-stack deployment later
- Takes ~3 minutes

---

## Free Tier Limits (Neon)

| Resource | Free Tier Limit |
|----------|----------------|
| Storage | 0.5 GB |
| Compute | Shared CPU |
| Data Transfer | 5 GB/month |
| Connections | 100 concurrent |
| Projects | 1 project |

**For ContextMeet development, this is MORE than enough.**

---

## Next Steps After Database Setup

1. ✅ Neon database created
2. ✅ Connection strings added to `backend/.env`
3. ⏭️ Continue with other environment variables (Google OAuth, Gmail, Telegram, Ollama)
4. ⏭️ Install backend dependencies: `pip install -r requirements.txt`
5. ⏭️ Run database migrations (create tables)
6. ⏭️ Start development server

---

## Troubleshooting

### Error: "password authentication failed"
- Go back to Neon dashboard
- Click **"Reset password"** button
- Copy the NEW connection string
- Update both `DATABASE_URL` and `DATABASE_ASYNC_URL` in `.env`

### Error: "SSL connection required"
- Make sure connection string ends with `?sslmode=require`
- Neon REQUIRES SSL for all connections

### Error: "too many connections"
- Free tier limit: 100 concurrent connections
- Check if you have multiple servers running
- Restart your application

---

## Security Notes

⚠️ **NEVER commit `.env` file to git**
⚠️ **NEVER share connection strings publicly**
⚠️ Connection string contains your password - treat like a secret key

---

## Total Setup Time: ~3 Minutes

✅ **You're done!** You now have a free, production-grade PostgreSQL database.

No installation, no Docker, no local setup needed.

**Proceed to:** `DETAILED_STEP_BY_STEP_SETUP.txt` (skip Phase 1 - PostgreSQL Installation)
