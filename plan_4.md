# Plan 4: Google Cloud Reasoning Engine Integration

## Overview

The ADK agents are now deployed as a Google Cloud Reasoning Engine. This is **much simpler** than local WebSocket/SSE approaches - just HTTP POST requests to a deployed API.

## Backend API Details

**Endpoint:**
```
POST https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256:query
```

**Authentication:**
```bash
Authorization: Bearer <TOKEN>
# Get token: gcloud auth print-access-token
```

**Request Format:**
```json
{
  "input": "Your geopolitical event here"
}
```

**Expected Response:**
The agent will return responses as they're generated (country responses + analyst updates).

## Architecture Decision

### Option A: Direct Browser → GCP (WILL FAIL)
```
React Browser → CORS → ❌ GCP Reasoning Engine
```
**Why it fails:**
- CORS policy blocks browser requests to GCP APIs
- Can't set Authorization header from browser (security)
- No way to get gcloud token in browser

### Option B: Browser → Backend Proxy → GCP (RECOMMENDED)
```
React Browser → Express Backend → GCP Reasoning Engine
              (localhost:3001)    (authenticated)
```
**Why it works:**
- Backend can authenticate with GCP
- Backend controls CORS
- Backend can stream responses to frontend
- Clean separation of concerns

## Critical Issues to Solve

### Issue 1: Authentication Token Management

**Problem:** Need to get and refresh gcloud access tokens

**Solutions Evaluated:**

**❌ Bad: Hardcode token**
```typescript
const TOKEN = "ya29.a0Ad52N3..."; // Expires in 1 hour!
```
- Tokens expire after 1 hour
- Security risk if committed to git
- Won't work for deployment

**✅ Good: Generate on server startup**
```typescript
// Server startup
const token = execSync('gcloud auth print-access-token').toString().trim();
```
- Fresh token each time
- No security risk
- Requires gcloud CLI installed

**✅ Better: Refresh tokens automatically**
```typescript
let cachedToken = null;
let tokenExpiry = null;

async function getToken() {
  if (cachedToken && Date.now() < tokenExpiry) {
    return cachedToken;
  }

  cachedToken = execSync('gcloud auth print-access-token').toString().trim();
  tokenExpiry = Date.now() + 3500000; // 58 minutes (tokens last 60 min)
  return cachedToken;
}
```
- Caches token for 58 minutes
- Auto-refreshes before expiry
- Minimal `gcloud` calls

**Decision: Use auto-refresh approach**

### Issue 2: CORS Handling

**Problem:** GCP API blocks browser requests

**Solution:** Express backend acts as proxy

```typescript
app.use(cors({
  origin: 'http://localhost:3000', // React app
  credentials: true
}));
```

### Issue 3: Response Streaming

**Problem:** Don't know if GCP Reasoning Engine streams or returns all at once

**Possible scenarios:**

**Scenario A: Single JSON response**
```json
{
  "output": "All agent responses at once..."
}
```
- Simple to handle
- Parse and extract country/analyst responses
- Display all at once (not ideal UX)

**Scenario B: Streaming responses**
```
data: [USA] said: ...
data: [China] said: ...
data: {"iteration": 1, "norm_updates": ...}
```
- Better UX (real-time updates)
- Need to parse stream
- Forward to frontend via SSE or polling

**Decision: Plan for both, test to determine which**

### Issue 4: Response Parsing

**Problem:** Need to extract country responses and analyst JSON from output

**Expected output format (from CLAUDE.md):**
```
[EU] said: I stand amidst a cacophony...
[USA] said: The United States condemns...
{"iteration": 3, "analysis": "...", "norm_updates": {...}, "reasoning": {...}}
```

**Parser Requirements:**
1. Detect country response pattern: `[COUNTRY] said:`
2. Detect analyst JSON pattern: `{"iteration":`
3. Handle multi-line responses
4. Preserve message formatting

**Reuse existing parser from plan_2.md:**
```typescript
// Already implemented in frontend/server/outputParser.ts
const parser = new OutputParser();
const parsed = parser.parseLine(line);
```

### Issue 5: Initial Norms Passing

**Problem:** How to pass `initial_norms.json` to the agent?

**Option A: Append to input**
```json
{
  "input": "Geopolitical event...\n\nInitial Norms: {...}"
}
```
- Simple
- Agent might not parse correctly

**Option B: Separate context field**
```json
{
  "input": "Geopolitical event...",
  "context": {
    "initial_norms": {...}
  }
}
```
- Cleaner
- Need to check if API supports this

**Option C: Already in agent**
```python
# Initial norms might be hardcoded in agent.py
```
- No need to pass
- Check agent.py to confirm

**Decision: Test Option A first, fallback to checking if norms are in agent**

### Issue 6: Error Handling

**Critical errors to handle:**

1. **gcloud not installed**
```typescript
try {
  const token = execSync('gcloud auth print-access-token');
} catch (error) {
  throw new Error('gcloud CLI not found. Install from cloud.google.com/sdk/docs/install');
}
```

2. **Not authenticated with gcloud**
```typescript
// Error: "ERROR: (gcloud.auth.print-access-token) Your credentials are invalid"
// Solution: Run `gcloud auth login`
```

3. **GCP API errors**
```typescript
if (response.status === 401) {
  // Token expired or invalid
  // Regenerate token
}
if (response.status === 403) {
  // No permission
  // Check IAM roles
}
if (response.status === 404) {
  // Reasoning Engine not found
  // Check endpoint URL
}
```

4. **Network errors**
```typescript
try {
  const response = await fetch(GCP_ENDPOINT, ...);
} catch (error) {
  if (error.code === 'ENOTFOUND') {
    throw new Error('No internet connection');
  }
  throw error;
}
```

5. **Timeout (long-running simulation)**
```typescript
// Set generous timeout (5 minutes)
const controller = new AbortController();
const timeout = setTimeout(() => controller.abort(), 300000);

const response = await fetch(url, {
  signal: controller.signal,
  ...options
});
```

## Implementation Plan

### Phase 1: Backend Proxy Server (2-3 hours)

#### Step 1.1: Create GCP Service

**File: `frontend/server/gcpService.ts`**

```typescript
import { execSync } from 'child_process';

const GCP_ENDPOINT = 'https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256:query';

export class GcpReasoningEngine {
  private cachedToken: string | null = null;
  private tokenExpiry: number | null = null;

  /**
   * Get fresh access token (cached for 58 minutes)
   */
  private async getToken(): Promise<string> {
    // Return cached if still valid
    if (this.cachedToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      return this.cachedToken;
    }

    try {
      // Get new token from gcloud
      this.cachedToken = execSync('gcloud auth print-access-token', {
        encoding: 'utf-8'
      }).trim();

      // Cache for 58 minutes (tokens last 60)
      this.tokenExpiry = Date.now() + (58 * 60 * 1000);

      console.log('✓ Refreshed GCP access token');
      return this.cachedToken;
    } catch (error) {
      throw new Error('Failed to get gcloud token. Run: gcloud auth login');
    }
  }

  /**
   * Query the reasoning engine
   */
  async query(input: string): Promise<any> {
    const token = await this.getToken();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 300000); // 5 min

    try {
      const response = await fetch(GCP_ENDPOINT, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input }),
        signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorText = await response.text();

        if (response.status === 401) {
          // Token expired, clear cache and retry
          this.cachedToken = null;
          this.tokenExpiry = null;
          throw new Error('Token expired. Retrying...');
        }

        throw new Error(`GCP API error (${response.status}): ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeout);

      if (error.name === 'AbortError') {
        throw new Error('Request timeout after 5 minutes');
      }

      throw error;
    }
  }

  /**
   * Check if gcloud is installed and authenticated
   */
  async healthCheck(): Promise<{ healthy: boolean; message: string }> {
    try {
      execSync('gcloud --version', { encoding: 'utf-8' });
    } catch (error) {
      return {
        healthy: false,
        message: 'gcloud CLI not installed. Install from cloud.google.com/sdk/docs/install'
      };
    }

    try {
      await this.getToken();
      return {
        healthy: true,
        message: 'GCP connection ready'
      };
    } catch (error) {
      return {
        healthy: false,
        message: 'Not authenticated. Run: gcloud auth login'
      };
    }
  }
}

export const gcpService = new GcpReasoningEngine();
```

#### Step 1.2: Update Express Server

**File: `frontend/server/index.ts`**

Replace WebSocket logic with simple HTTP endpoints:

```typescript
import express from 'express';
import cors from 'cors';
import { gcpService } from './gcpService';
import { OutputParser } from './outputParser';

const app = express();
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

const PORT = 3001;

// Health check
app.get('/api/health', async (req, res) => {
  const health = await gcpService.healthCheck();
  res.json(health);
});

// Start simulation
app.post('/api/simulate', async (req, res) => {
  const { event, initialNorms } = req.body;

  if (!event) {
    return res.status(400).json({ error: 'Event is required' });
  }

  try {
    console.log('Starting simulation:', event);

    // Call GCP Reasoning Engine
    const result = await gcpService.query(event);

    // Parse the response
    const parser = new OutputParser();
    const responses = parseGcpOutput(result, parser);

    res.json({
      success: true,
      responses
    });
  } catch (error) {
    console.error('Simulation error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

function parseGcpOutput(result: any, parser: OutputParser) {
  // Extract output from GCP response
  const output = result.output || result.response || JSON.stringify(result);

  const countryResponses = [];
  const analystResponses = [];

  // Parse line by line
  const lines = output.split('\n');
  for (const line of lines) {
    const parsed = parser.parseLine(line);
    if (parsed) {
      if ('country' in parsed) {
        countryResponses.push(parsed);
      } else if ('iteration' in parsed) {
        analystResponses.push(parsed);
      }
    }
  }

  return { countryResponses, analystResponses };
}

app.listen(PORT, async () => {
  console.log(`Server running on port ${PORT}`);

  // Check GCP connection on startup
  const health = await gcpService.healthCheck();
  if (health.healthy) {
    console.log('✓', health.message);
  } else {
    console.error('✗', health.message);
  }
});
```

### Phase 2: Frontend Updates (1-2 hours)

#### Step 2.1: Replace WebSocket with HTTP

**File: `frontend/src/services/adkService.ts`**

```typescript
export class AdkService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:3001') {
    this.baseUrl = baseUrl;
  }

  /**
   * Check backend health
   */
  async checkHealth(): Promise<{ healthy: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  /**
   * Start simulation
   */
  async startSimulation(event: string, initialNorms: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event, initialNorms })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to start simulation');
    }

    return response.json();
  }
}

export const adkService = new AdkService();
```

#### Step 2.2: Update React Hook

**File: `frontend/src/hooks/useSimulation.ts`**

```typescript
const startSimulation = useCallback(async (geopoliticalEvent: string) => {
  if (state.isRunning) {
    throw new Error('Simulation already running');
  }

  setIsLoading(true);
  setConnectionError(null);

  try {
    setState(prev => ({
      ...prev,
      isRunning: true,
      geopoliticalEvent,
      countryResponses: [],
      analystResponses: []
    }));

    // Call backend API (blocks until complete)
    const result = await adkService.startSimulation(geopoliticalEvent, initialNorms);

    // Update state with all responses
    setState(prev => ({
      ...prev,
      isRunning: false,
      countryResponses: result.responses.countryResponses,
      analystResponses: result.responses.analystResponses,
      currentNorms: result.responses.analystResponses[result.responses.analystResponses.length - 1]?.norm_updates || initialNorms
    }));
  } catch (error) {
    setState(prev => ({ ...prev, isRunning: false }));
    setConnectionError(error.message);
    throw error;
  } finally {
    setIsLoading(false);
  }
}, [state.isRunning, initialNorms]);
```

### Phase 3: Testing & Debugging (1-2 hours)

#### Test 1: Backend Authentication
```bash
cd frontend
npm run server

# Expected output:
# Server running on port 3001
# ✓ GCP connection ready
```

**If error:** "gcloud CLI not installed"
```bash
# Install gcloud
# https://cloud.google.com/sdk/docs/install
```

**If error:** "Not authenticated"
```bash
gcloud auth login
gcloud config set project gen-lang-client-0834462342
```

#### Test 2: Manual API Test
```bash
# Get token
TOKEN=$(gcloud auth print-access-token)

# Test endpoint
curl -X POST \
  https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256:query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": "Test: Trade dispute escalates"}'
```

**Expected:** JSON response with agent output

#### Test 3: Full Stack Test
1. Start backend: `npm run server`
2. Start frontend: `npm start`
3. Enter test event
4. Verify responses appear

### Phase 4: Error Handling & Edge Cases

#### Edge Case 1: Empty Response
```typescript
if (!result || !result.output) {
  throw new Error('No output from reasoning engine');
}
```

#### Edge Case 2: Malformed Output
```typescript
try {
  const parsed = parser.parseLine(line);
} catch (error) {
  console.warn('Failed to parse line:', line);
  // Continue parsing other lines
}
```

#### Edge Case 3: Token Expiry Mid-Request
```typescript
// Auto-retry with fresh token
if (response.status === 401) {
  this.cachedToken = null;
  return this.query(input); // Retry once
}
```

#### Edge Case 4: Network Timeout
```typescript
// Show progress to user
setState({ statusMessage: 'Waiting for agents (this may take 2-5 minutes)...' });
```

## File Structure

```
frontend/
├── server/
│   ├── index.ts              # Express server with /api/simulate endpoint
│   ├── gcpService.ts         # NEW: GCP Reasoning Engine client
│   ├── outputParser.ts       # Reuse from plan_2.md
│   └── types.ts              # Existing types
├── src/
│   ├── services/
│   │   └── adkService.ts     # HTTP client (no WebSocket)
│   ├── hooks/
│   │   └── useSimulation.ts  # Simplified (no streaming)
│   └── ...
```

## Comparison with Previous Plans

| Feature | Plan 2 (WebSocket) | Plan 3 (SSE) | Plan 4 (GCP) |
|---------|-------------------|--------------|--------------|
| Complexity | High | Medium | **Low** |
| Real-time Updates | Yes | Yes | No (batch) |
| Authentication | N/A | N/A | **gcloud token** |
| CORS Issues | WebSocket | None | **Backend proxy** |
| Stability | Poor (React issues) | Good | **Excellent** |
| Setup Time | 6-10 hours | 4-6 hours | **2-4 hours** |
| Deployment | Complex | Medium | **Simple** |

## Potential Issues & Solutions

### Issue: Slow Response Time

**Problem:** GCP API might take 2-5 minutes for full simulation

**Solution:** Show loading state with message
```typescript
<Box>
  <CircularProgress />
  <Typography>
    Agents are deliberating (this may take 2-5 minutes)...
  </Typography>
</Box>
```

### Issue: Response Format Unknown

**Problem:** Don't know exact format of GCP response

**Solution:** Log everything and adapt
```typescript
console.log('GCP Response:', JSON.stringify(result, null, 2));
// Adjust parser based on actual format
```

### Issue: gcloud Not in PATH

**Problem:** Backend can't find gcloud command

**Solution:** Full path to gcloud
```typescript
const GCLOUD_PATH = process.env.GCLOUD_PATH || 'gcloud';
execSync(`${GCLOUD_PATH} auth print-access-token`);
```

## Implementation Checklist

### Backend
- [ ] Create `frontend/server/gcpService.ts`
- [ ] Update `frontend/server/index.ts`
- [ ] Add health check endpoint
- [ ] Test gcloud authentication
- [ ] Test GCP API call manually
- [ ] Add error handling
- [ ] Add request timeout
- [ ] Test with actual reasoning engine

### Frontend
- [ ] Update `adkService.ts` (remove WebSocket)
- [ ] Update `useSimulation.ts` (HTTP-based)
- [ ] Add loading states
- [ ] Add error messages
- [ ] Test full flow
- [ ] Handle slow responses

### Testing
- [ ] Verify gcloud installed
- [ ] Verify authentication works
- [ ] Test manual curl request
- [ ] Test backend /api/simulate
- [ ] Test frontend integration
- [ ] Test error cases
- [ ] Test with real geopolitical event

## Success Criteria

- [ ] Backend authenticates with GCP successfully
- [ ] Backend can query reasoning engine
- [ ] Responses parsed correctly
- [ ] Country responses displayed
- [ ] Analyst updates displayed
- [ ] Norms visualization updates
- [ ] Error messages are clear
- [ ] No CORS errors
- [ ] No authentication errors

## Rollback Plan

If GCP integration fails:
1. Keep existing WebSocket code
2. Add feature flag: `USE_GCP=true/false`
3. Toggle based on environment
4. Debug GCP issues separately

## Timeline

- **Phase 1 (Backend)**: 2-3 hours
- **Phase 2 (Frontend)**: 1-2 hours
- **Phase 3 (Testing)**: 1-2 hours
- **Phase 4 (Polish)**: 1 hour
- **Total**: 5-8 hours

## Dependencies

**Required:**
- `gcloud` CLI installed
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project gen-lang-client-0834462342`
- IAM permissions to call Reasoning Engine

**Optional:**
- Environment variable for custom gcloud path
- Token caching for faster requests

## Next Steps After Implementation

1. Test with various geopolitical events
2. Optimize response parsing
3. Add retry logic for failures
4. Add response caching
5. Deploy backend to cloud
6. Add authentication for frontend users

## Conclusion

This approach is **significantly simpler** than WebSocket/SSE because:
- No process management (agents already deployed)
- No stdout parsing complexity (JSON API)
- No connection stability issues
- Standard HTTP request/response

The main complexity is **GCP authentication**, which we handle with automatic token refresh.

This is the **right architecture** for a deployed reasoning engine!
