# Quick Start - Robot Von Bismarck

## 🚀 3 Steps to Run

### Step 1: Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project gen-lang-client-0834462342
```

### Step 2: Start the Application

```bash
cd frontend
npm run dev
```

### Step 3: Open Browser

Navigate to: **http://localhost:3000**

---

## ✅ Expected Terminal Output

```
=================================
Server running on port 3001
=================================

Checking GCP Reasoning Engine connection...
✓ Refreshed GCP access token (valid for 58 minutes)
✓ GCP connection ready

✓ Ready to accept simulation requests!

[FRONTEND] Compiled successfully!
[FRONTEND] Local: http://localhost:3000
```

---

## 🎮 Using the Application

1. **Enter a Geopolitical Event:**
   ```
   Major cyberattack on critical infrastructure attributed to a state actor
   ```

2. **Click "Start Simulation"**

3. **Wait 2-5 minutes** (agents are deliberating)

4. **View Results:**
   - Country responses (USA, China, Russia, EU)
   - Analyst reasoning
   - Norm evolution charts

---

## ❌ Troubleshooting

### Error: "gcloud: command not found"

**Install gcloud:**
- Windows: https://cloud.google.com/sdk/docs/install#windows
- Mac: `brew install google-cloud-sdk`
- Linux: `curl https://sdk.cloud.google.com | bash`

### Error: "Not authenticated with gcloud"

```bash
gcloud auth login
gcloud config set project gen-lang-client-0834462342
```

### Error: "Backend not reachable"

```bash
# Make sure backend is running
cd frontend
npm run server

# In another terminal, start frontend
npm start
```

---

## 📚 More Information

- **Full Setup Guide**: See `GCP_SETUP.md`
- **Implementation Details**: See `PLAN_4_IMPLEMENTATION.md`
- **Planning Document**: See `plan_4.md`

---

## 🎯 What Happens When You Run a Simulation

1. Frontend sends event to backend (localhost:3001)
2. Backend authenticates with GCP using gcloud token
3. Backend calls deployed Reasoning Engine
4. Multi-agent simulation runs:
   - USA agent responds
   - China agent responds
   - Russia agent responds
   - EU agent responds
   - Analyst evaluates and updates norms
   - (Repeats 5 times)
5. Backend receives all responses
6. Backend parses and returns to frontend
7. Frontend displays everything beautifully!

---

## 💡 Tips

- **First run takes longer** (token generation + cold start)
- **Subsequent runs are faster** (token cached for 58 min)
- **Check backend logs** for detailed progress
- **Refresh page** if connection error persists

---

## 🆘 Need Help?

1. Check `GCP_SETUP.md` for detailed troubleshooting
2. Verify gcloud works: `gcloud auth print-access-token`
3. Test backend health: `curl http://localhost:3001/api/health`
4. Check frontend console (F12) for errors

---

That's it! Enjoy your geopolitical simulation! 🌍
