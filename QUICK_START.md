# Quick Start Guide

## Prerequisites

1. **Node.js** installed (v16+)
2. **Python** installed with Google ADK
3. **Environment variables** set up (`.env` file with `GEMINI_API_KEY`)

## Running the Application

### Option 1: Easy Start (Windows)

Double-click `start.bat` or run:
```bash
start.bat
```

### Option 2: Easy Start (Mac/Linux)

```bash
chmod +x start.sh
./start.sh
```

### Option 3: Manual Start

```bash
cd frontend
npm run dev
```

## What You'll See

```
[FRONTEND] Compiled successfully!
[FRONTEND] webpack compiled successfully
[FRONTEND] You can now view frontend in the browser.
[FRONTEND]   Local:            http://localhost:3000

[BACKEND] Server running on port 3001
[BACKEND] WebSocket server ready
```

## Open the Application

Navigate to: **http://localhost:3000**

## Test the Connection

1. Open browser console (F12)
2. Look for: `WebSocket connected`
3. If you see `Connection Error`, make sure both servers are running

## Run Your First Simulation

1. Enter a geopolitical event:
   ```
   Rising tensions over resource control in the Arctic
   ```

2. Click "Start Simulation"

3. Watch as:
   - USA responds (10-30 seconds)
   - China responds (10-30 seconds)
   - Russia responds (10-30 seconds)
   - EU responds (10-30 seconds)
   - Analyst updates norms (10-30 seconds)
   - Cycle repeats 5 times

4. Total simulation time: ~5-10 minutes

## Troubleshooting

### "Connection Error: WebSocket connection timeout"
**Problem:** Backend not running
**Solution:**
```bash
cd frontend
npx kill-port 3001
npm run dev
```

### "Port 3000/3001 already in use"
**Solution:**
```bash
cd frontend
npx kill-port 3000
npx kill-port 3001
npm run dev
```

### Backend server doesn't show output
**Problem:** Concurrently not showing backend logs
**Solution:** Run servers separately in two terminals:

**Terminal 1:**
```bash
cd frontend
npm run server:watch
```

**Terminal 2:**
```bash
cd frontend
npm start
```

### "ADK process error"
**Problem:** Python/ADK not set up
**Solution:**
```bash
pip install google-adk
# Make sure .env has GEMINI_API_KEY=your_key_here
```

## Stopping the Application

Press **Ctrl+C** in the terminal where `npm run dev` is running. This will stop both servers.

## Next Steps

- See `frontend/RUNNING.md` for detailed documentation
- See `IMPLEMENTATION_SUMMARY.md` for architecture details
- Check `plan_2.md` for implementation rationale

## Need Help?

1. Check backend logs in terminal
2. Check frontend console (F12 in browser)
3. Ensure `.env` file exists with valid API key
4. Verify Python ADK works: `adk run international_system/agent.py`
