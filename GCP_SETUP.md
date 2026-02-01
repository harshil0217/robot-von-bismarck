# GCP Reasoning Engine Setup Guide

## Prerequisites

1. **Google Cloud SDK (gcloud)** installed
2. **Authenticated** with gcloud
3. **Node.js** (v16+) installed

## Step 1: Install Google Cloud SDK

### Windows
```bash
# Download and run installer from:
https://cloud.google.com/sdk/docs/install#windows
```

### Mac
```bash
brew install google-cloud-sdk
```

### Linux
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Verify Installation
```bash
gcloud --version
# Should output: Google Cloud SDK X.X.X
```

## Step 2: Authenticate with Google Cloud

```bash
# Login to your Google Cloud account
gcloud auth login

# Set the project
gcloud config set project gen-lang-client-0834462342

# Test authentication
gcloud auth print-access-token
# Should output a long token starting with "ya29..."
```

## Step 3: Test GCP Reasoning Engine

Test the deployed reasoning engine manually:

```bash
# Get access token
TOKEN=$(gcloud auth print-access-token)

# Test the endpoint
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256:query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Test event: Trade tensions escalate between major powers"
  }'
```

**Expected Response:**
- JSON with agent outputs
- Should include country responses and analyst JSON

## Step 4: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 5: Run the Application

### Option 1: Run Both Together
```bash
cd frontend
npm run dev
```

This starts:
- **Backend** (port 3001) - Proxy to GCP
- **Frontend** (port 3000) - React app

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
cd frontend
npm run server
```

Expected output:
```
=================================
Server running on port 3001
=================================

Checking GCP Reasoning Engine connection...
✓ Refreshed GCP access token (valid for 58 minutes)
✓ GCP connection ready

✓ Ready to accept simulation requests!

=================================
Endpoints:
  GET  /api/health   - Check GCP connection
  POST /api/simulate - Start simulation
=================================
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## Step 6: Use the Application

1. Open browser to `http://localhost:3000`
2. Enter a geopolitical event:
   ```
   Major cyberattack on critical infrastructure attributed to a state actor
   ```
3. Click "Start Simulation"
4. Wait 2-5 minutes for agents to respond
5. View results:
   - Country responses in chat
   - Analyst reasoning
   - Norm visualizations

## Troubleshooting

### Error: "gcloud: command not found"

**Solution:** Install Google Cloud SDK (Step 1)

```bash
# Check if gcloud is in PATH
which gcloud

# If not found, add to PATH or reinstall
```

### Error: "Not authenticated with gcloud"

**Solution:** Run authentication commands

```bash
gcloud auth login
gcloud config set project gen-lang-client-0834462342
```

### Error: "Failed to get gcloud token"

**Solution:** Check authentication status

```bash
# View current auth
gcloud auth list

# Re-authenticate
gcloud auth login
```

### Error: "GCP API error (403): Permission denied"

**Solution:** Check IAM permissions

1. Go to GCP Console
2. Navigate to IAM & Admin
3. Ensure your account has `Reasoning Engine User` role
4. Contact project admin if needed

### Error: "GCP API error (404): Not found"

**Solution:** Verify Reasoning Engine exists

```bash
# Check if endpoint is correct
gcloud ai reasoning-engines list \
  --location=us-central1 \
  --project=gen-lang-client-0834462342
```

### Error: "Request timeout after 5 minutes"

**Possible causes:**
- Reasoning Engine is slow
- Network issues
- Engine is not responding

**Solution:**
- Check GCP Console for Reasoning Engine status
- Try manual curl test (Step 3)
- Check network connectivity

### Error: "Backend not reachable"

**Solution:** Ensure backend is running

```bash
# Check if backend is running
curl http://localhost:3001/api/health

# If not, start backend
cd frontend
npm run server
```

### Backend starts but shows "✗ Not authenticated"

**Solution:**
```bash
# Run in terminal
gcloud auth login

# Then restart backend
npm run server
```

## How It Works

### Architecture

```
┌─────────────────┐
│ React Frontend  │  http://localhost:3000
│  (Browser UI)   │
└────────┬────────┘
         │ HTTP POST
         ↓
┌─────────────────┐
│ Express Backend │  http://localhost:3001
│  (Proxy Server) │
└────────┬────────┘
         │ gcloud token + HTTP POST
         ↓
┌─────────────────────────────────────────┐
│ GCP Reasoning Engine                    │
│ (Deployed ADK Multi-Agent System)       │
│  - USA Agent                            │
│  - China Agent                          │
│  - Russia Agent                         │
│  - EU Agent                             │
│  - Norm Adaptation Analyst              │
└─────────────────────────────────────────┘
```

### Data Flow

1. **User Input**: Enter geopolitical event in browser
2. **Frontend → Backend**: POST to `/api/simulate` with event
3. **Backend → GCP**: Authenticate with gcloud token, POST to Reasoning Engine
4. **GCP Processing**: Multi-agent simulation runs (2-5 minutes)
5. **GCP → Backend**: Return all responses (country + analyst)
6. **Backend → Frontend**: Parse and send to browser
7. **Frontend Display**: Show responses, update norms, display analysis

## Token Management

**Automatic Token Refresh:**
- Backend caches gcloud tokens for 58 minutes
- Tokens expire after 60 minutes
- Backend auto-refreshes before expiry
- No manual intervention needed

**Token Storage:**
- Tokens are **never** stored in files
- Generated fresh from gcloud CLI
- Cached in memory only
- Secure and compliant

## Production Deployment

### Option 1: Deploy Backend to Cloud Run

```bash
cd frontend

# Build backend
npm run build:server

# Deploy to Cloud Run (auto-handles auth)
gcloud run deploy robot-von-bismarck-backend \
  --source server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Use Service Account (Recommended)

1. Create service account
2. Grant `Reasoning Engine User` role
3. Download key file
4. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```

## Cost Estimation

**GCP Reasoning Engine Costs:**
- Per query cost: ~$0.01 - $0.10 (depending on model)
- 5 iterations × 5 agents = ~25 LLM calls
- Estimated cost per simulation: **$0.25 - $2.50**

**Tips to Reduce Costs:**
- Use smaller models (gemini-flash vs gemini-pro)
- Reduce iterations (5 → 3)
- Cache results for testing

## Monitoring

**Backend Logs:**
```bash
# View detailed backend logs
npm run server

# Look for:
# ✓ GCP connection ready
# ✓ Refreshed GCP access token
# ✓ Received response from GCP
```

**GCP Console:**
1. Go to https://console.cloud.google.com
2. Navigate to Vertex AI → Reasoning Engines
3. View Reasoning Engine logs and metrics

## Next Steps

1. ✅ Test basic functionality
2. ✅ Run a full simulation
3. 📊 Monitor costs in GCP Console
4. 🔧 Optimize performance if needed
5. 🚀 Deploy to production (Cloud Run)

## Support

**Common Issues:**
- Authentication problems → Re-run `gcloud auth login`
- Timeout errors → Check Reasoning Engine status in GCP Console
- Parse errors → Check backend logs for raw GCP output

**Resources:**
- GCP Docs: https://cloud.google.com/vertex-ai/docs/reasoning-engine
- gcloud CLI: https://cloud.google.com/sdk/docs/cheatsheet
- Project GitHub: (your repo)
