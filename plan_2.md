# Plan 2: Integrating Real ADK Agent Output with Frontend

## Problem Statement

The frontend is currently displaying mock/template data from `adkService.ts` instead of actual responses from the Python ADK agents. The service has placeholder comments like "In a real implementation, this would communicate with the Python ADK agents" and returns hardcoded responses.

## Root Cause Analysis

1. **Disconnected Systems**: The React frontend (TypeScript/JavaScript) and Python ADK agents are in separate runtime environments with no bridge
2. **Mock Data Implementation**: `adkService.ts` (lines 35-121) returns hardcoded template responses instead of calling real agents
3. **Missing Backend**: No server-side component to spawn Python processes and capture ADK CLI output
4. **No Real-time Communication**: No mechanism (WebSocket/SSE/polling) to stream agent responses as they occur

## Understanding the ADK CLI

From CLAUDE.md documentation:

```bash
# Running an agent
adk run international_system/agent.py

# With session saving
adk run --save_session --session_id my_session international_system/agent.py

# With replay (non-interactive)
adk run --replay path/to/input.json international_system/agent.py
```

**Input Format for Replay:**
```json
{
  "state": {"key": "value"},
  "queries": ["What is 2 + 2?", "What is the capital of France?"]
}
```

## Agent Architecture Analysis

From `international_system/agent.py`:

1. **SequentialAgent**: `simultaneous_reaction` runs 4 country agents + 1 norm updater sequentially
   - Order: USA → China → Russia → EU → NormAdaptationAgent

2. **LoopAgent**: `root_agent` repeats the sequential cycle 5 times

3. **Output Formats**:
   - **Country Agents**: Natural text like "[USA] said: The United States strongly condemns..."
   - **NormAdaptationAgent**: JSON output with structure:
     ```json
     {
       "iteration": 3,
       "analysis": "...",
       "norm_updates": { "China": {...}, "USA": {...}, "Russia": {...}, "EU": {...} },
       "reasoning": { "China": "...", "USA": "...", "Russia": "...", "EU": "..." }
     }
     ```

## Solution Architecture

### Option 1: Backend with WebSockets (RECOMMENDED)

**Pros:**
- Real-time bidirectional communication
- Can stream responses as agents respond
- Better user experience with live updates
- Industry standard for real-time apps

**Cons:**
- More complex to implement
- Requires managing WebSocket connections

**Architecture:**
```
[React Frontend] <--WebSocket--> [Node.js/Express Server] <--spawn--> [Python ADK CLI]
                                              |
                                              v
                                         Parse Output
                                         Emit Events
```

### Option 2: Server-Sent Events (SSE)

**Pros:**
- Simpler than WebSockets
- One-way streaming (sufficient for this use case)
- Built-in reconnection

**Cons:**
- One-way only (frontend to backend still needs HTTP)
- Less flexible than WebSockets

### Option 3: Long Polling

**Pros:**
- Simplest to implement
- Works with standard HTTP
- Good fallback option

**Cons:**
- Higher latency
- Less efficient
- Not truly real-time

## Detailed Implementation Plan

### Phase 1: Backend Service Creation

#### Step 1.1: Create Express Server
**Location:** `frontend/server/index.ts` or `backend/server.ts`

**Responsibilities:**
1. Handle WebSocket connections
2. Spawn Python ADK processes
3. Parse and forward agent responses
4. Manage simulation sessions
5. Handle errors and timeouts

**Key Dependencies:**
```json
{
  "express": "^4.18.0",
  "ws": "^8.0.0",
  "cors": "^2.8.5",
  "child_process": "built-in"
}
```

#### Step 1.2: Create ADK Process Manager
**Location:** `frontend/server/adkManager.ts`

**Responsibilities:**
1. Spawn ADK CLI processes using `child_process.spawn()`
2. Create input JSON for `--replay` mode
3. Capture stdout/stderr
4. Parse agent output in real-time
5. Detect country vs analyst responses

**Key Functions:**
```typescript
class AdkManager {
  // Start simulation with geopolitical event
  async startSimulation(event: string, initialNorms: CountryNorms): Promise<void>

  // Parse line-by-line output
  parseAgentOutput(line: string): ParsedMessage | null

  // Detect response type (country vs analyst)
  detectMessageType(line: string): 'country' | 'analyst' | 'system' | null

  // Clean up process on completion/error
  cleanup(): void
}
```

#### Step 1.3: Output Parsing Logic

**Challenge:** ADK CLI output mixes agent responses with system messages

**Parsing Strategy:**
1. **Country Responses**: Look for pattern `[COUNTRY] said:` or similar
2. **Analyst JSON**: Detect JSON blocks with `"iteration"`, `"norm_updates"`, `"reasoning"`
3. **System Messages**: Filter out ADK system logs
4. **Iteration Markers**: Track which iteration is current

**Regex Patterns:**
```typescript
const COUNTRY_PATTERN = /\[(USA|China|Russia|EU)\]\s*(?:said:)?\s*(.*)/i;
const JSON_START = /^\s*\{/;
const JSON_END = /^\s*\}/;
```

### Phase 2: Frontend Updates

#### Step 2.1: Replace Mock Service with WebSocket Client
**Location:** `frontend/src/services/adkService.ts`

**Changes:**
1. Remove all mock data (lines 37-179)
2. Implement WebSocket connection
3. Handle real-time messages
4. Parse incoming data
5. Emit events for UI updates

**New Structure:**
```typescript
export class AdkService {
  private ws: WebSocket | null = null;
  private callbacks: Map<string, Function> = new Map();

  connect(): Promise<void> {
    // Establish WebSocket connection
  }

  async startSimulation(event: string, norms: CountryNorms): Promise<void> {
    // Send start command via WebSocket
    this.ws.send(JSON.stringify({
      type: 'start',
      event: event,
      initialNorms: norms
    }));
  }

  onCountryResponse(callback: (response: CountryResponse) => void) {
    this.callbacks.set('country', callback);
  }

  onAnalystResponse(callback: (response: AnalystResponse) => void) {
    this.callbacks.set('analyst', callback);
  }

  onError(callback: (error: Error) => void) {
    this.callbacks.set('error', callback);
  }
}
```

#### Step 2.2: Update useSimulation Hook
**Location:** `frontend/src/hooks/useSimulation.ts`

**Changes:**
1. Remove iteration management logic (now handled by ADK LoopAgent)
2. Update to handle real-time WebSocket events
3. Add connection state management
4. Handle disconnections and reconnections

**Key Changes:**
```typescript
// Remove manual iteration logic (lines 64-121)
// Replace with event-driven approach

useEffect(() => {
  adkService.connect();

  adkService.onCountryResponse((response) => {
    setState(prev => ({
      ...prev,
      countryResponses: [...prev.countryResponses, response]
    }));
  });

  adkService.onAnalystResponse((response) => {
    setState(prev => ({
      ...prev,
      analystResponses: [...prev.analystResponses, response],
      currentNorms: response.norm_updates,
      currentIteration: response.iteration
    }));
  });

  return () => adkService.disconnect();
}, []);
```

### Phase 3: Output Parsing Implementation

#### Challenge 1: Country Response Format
**Expected Output from ADK:**
```
[USA] said: The United States strongly condemns this development...
```

**Parsing Logic:**
```typescript
function parseCountryResponse(line: string): CountryResponse | null {
  const match = line.match(/\[(USA|China|Russia|EU)\]\s*(?:said:)?\s*(.*)/i);
  if (match) {
    return {
      country: match[1] as CountryName,
      message: match[2].trim(),
      timestamp: new Date(),
      iteration: currentIteration // Track separately
    };
  }
  return null;
}
```

#### Challenge 2: Analyst JSON Parsing
**Expected Output:**
```json
{
  "iteration": 3,
  "analysis": "The rhetoric escalates further...",
  "norm_updates": {...},
  "reasoning": {...}
}
```

**Parsing Logic:**
```typescript
let jsonBuffer = '';
let inJsonBlock = false;

function parseAnalystOutput(line: string): AnalystResponse | null {
  // Detect JSON start
  if (line.trim().startsWith('{')) {
    inJsonBlock = true;
    jsonBuffer = line;
    return null;
  }

  // Accumulate JSON lines
  if (inJsonBlock) {
    jsonBuffer += line;

    // Detect JSON end
    if (line.trim().endsWith('}')) {
      try {
        const parsed = JSON.parse(jsonBuffer);
        if (parsed.iteration && parsed.norm_updates && parsed.reasoning) {
          inJsonBlock = false;
          jsonBuffer = '';
          return parsed as AnalystResponse;
        }
      } catch (e) {
        console.error('Failed to parse analyst JSON:', e);
      }
    }
  }

  return null;
}
```

#### Challenge 3: Handling Multi-line Responses

Country agents may output multi-paragraph responses. Need to:
1. Detect response start with `[COUNTRY]` marker
2. Accumulate lines until next country marker or analyst JSON
3. Group multi-line text into single response

**Solution:**
```typescript
let currentResponse: Partial<CountryResponse> | null = null;

function accumulateCountryResponse(line: string): CountryResponse | null {
  const countryMatch = line.match(/\[(USA|China|Russia|EU)\]/i);

  if (countryMatch) {
    // New country response starting
    if (currentResponse) {
      const completed = currentResponse as CountryResponse;
      currentResponse = {
        country: countryMatch[1] as CountryName,
        message: line.replace(/\[.*?\]\s*(?:said:)?\s*/, ''),
        iteration: currentIteration,
        timestamp: new Date()
      };
      return completed;
    } else {
      currentResponse = {
        country: countryMatch[1] as CountryName,
        message: line.replace(/\[.*?\]\s*(?:said:)?\s*/, ''),
        iteration: currentIteration,
        timestamp: new Date()
      };
    }
  } else if (currentResponse && line.trim()) {
    // Continuation of current response
    currentResponse.message += '\n' + line;
  }

  return null;
}
```

### Phase 4: Error Handling and Edge Cases

#### Error Case 1: Python Environment Issues
**Problem:** Python/ADK not installed or wrong version
**Solution:**
1. Check Python availability on server startup
2. Verify ADK installation
3. Provide clear error messages to frontend
4. Graceful degradation to mock data (with warning)

#### Error Case 2: Agent Timeout
**Problem:** Agent takes too long to respond
**Solution:**
1. Set process timeout (e.g., 5 minutes)
2. Kill process after timeout
3. Notify frontend of timeout
4. Allow retry option

#### Error Case 3: Malformed Agent Output
**Problem:** Agent outputs unexpected format
**Solution:**
1. Robust parsing with fallbacks
2. Log unparseable lines for debugging
3. Don't crash on parse errors
4. Send partial data to frontend

#### Error Case 4: WebSocket Disconnection
**Problem:** Network issues or server restart
**Solution:**
1. Automatic reconnection with exponential backoff
2. Save simulation state on server
3. Resume from last known state
4. Show connection status in UI

### Phase 5: Testing Strategy

#### Unit Tests
1. Test output parsing functions with sample data
2. Test JSON extraction from mixed output
3. Test multi-line accumulation logic
4. Test error handling paths

**Sample Test Data:**
```typescript
describe('parseCountryResponse', () => {
  it('should parse simple country response', () => {
    const line = '[USA] said: We condemn this action';
    const result = parseCountryResponse(line, 1);
    expect(result.country).toBe('USA');
    expect(result.message).toBe('We condemn this action');
  });

  it('should handle country name case variations', () => {
    const line = '[china] The People\'s Republic responds...';
    const result = parseCountryResponse(line, 1);
    expect(result.country).toBe('China');
  });
});
```

#### Integration Tests
1. Mock ADK CLI output
2. Test end-to-end flow from input to display
3. Test WebSocket message handling
4. Test state updates in React components

#### Manual Testing
1. Run actual ADK simulation
2. Verify all 5 iterations complete
3. Check norm visualization updates
4. Verify analyst reasoning displays correctly

## Implementation Checklist

### Backend (Critical Path)
- [ ] Create Express server with WebSocket support
- [ ] Implement ADK process spawning with `child_process`
- [ ] Create input JSON builder for ADK `--replay` mode
- [ ] Implement line-by-line output parser
- [ ] Add country response pattern matching
- [ ] Add analyst JSON detection and parsing
- [ ] Handle multi-line response accumulation
- [ ] Implement iteration tracking
- [ ] Add error handling and timeouts
- [ ] Test with actual ADK agent

### Frontend Updates
- [ ] Add WebSocket client to `adkService.ts`
- [ ] Remove mock data and delays
- [ ] Update `useSimulation` hook for event-driven updates
- [ ] Add WebSocket connection state management
- [ ] Handle reconnection logic
- [ ] Add error display in UI
- [ ] Test with backend integration

### Optional Enhancements
- [ ] Add simulation pause/resume
- [ ] Implement simulation history/replay
- [ ] Add progress indicators during agent thinking
- [ ] Save/load simulation sessions
- [ ] Export results to JSON/PDF

## Critical Technical Decisions

### Decision 1: ADK CLI Invocation Method

**Option A: Interactive Mode (`adk run`)**
- Pros: Simpler, closer to documented usage
- Cons: Harder to control programmatically, requires stdin interaction

**Option B: Replay Mode (`adk run --replay`) ✓ RECOMMENDED**
- Pros: Non-interactive, predictable, easier to automate
- Cons: Requires creating input JSON

**Decision:** Use replay mode with generated input JSON

### Decision 2: Initial Norms Passing

**Challenge:** How to pass `initial_norms.json` to ADK agents?

**Option A: File-based**
- Write norms to temp file
- Pass file path to ADK

**Option B: Context in query**
- Include norms in geopolitical event query
- Agent reads from context

**Option C: Agent initialization** ✓ IMPLEMENTED
- Norms already hardcoded in `agent.py` lines 231-329
- NormAdaptationAgent reads from conversation history
- No changes needed!

**Decision:** No changes needed; initial norms are in agent definitions

### Decision 3: Output Streaming vs Buffering

**Option A: Line-by-line streaming** ✓ RECOMMENDED
- Parse and emit as each line arrives
- Real-time updates in UI
- Better UX

**Option B: Buffer entire output**
- Wait for process completion
- Parse everything at once
- Simpler parsing but worse UX

**Decision:** Stream line-by-line with accumulation for multi-line responses

## Potential Bugs and Prevention

### Bug 1: Race Condition in Multi-line Parsing
**Risk:** Lines arrive out of order or split incorrectly
**Prevention:**
- Use streaming accumulation buffer
- Track state (current country, in JSON block)
- Test with various output formats

### Bug 2: JSON Parsing Across Line Breaks
**Risk:** Analyst JSON split across multiple stdout flushes
**Prevention:**
- Accumulate JSON in buffer
- Parse only when complete (matching braces)
- Handle nested objects correctly

### Bug 3: Country Name Variations
**Risk:** Agent outputs "USA" vs "United States" vs "US"
**Prevention:**
- Normalize country names
- Use case-insensitive matching
- Map variations to standard names

### Bug 4: Iteration Tracking Desync
**Risk:** Frontend iteration count doesn't match ADK loop
**Prevention:**
- Parse iteration from analyst JSON (authoritative)
- Don't rely on frontend counters
- Validate iteration sequence (1,2,3,4,5)

### Bug 5: Memory Leaks with Long-Running Processes
**Risk:** Server memory grows with accumulated output
**Prevention:**
- Clear buffers after parsing
- Limit max output size
- Kill process if output exceeds threshold

## Testing Before Deployment

### Step 1: Test ADK CLI Manually
```bash
cd C:\Users\harsh\robot-von-bismarck

# Create test input
echo '{
  "state": {},
  "queries": ["Test event: Major cyberattack on critical infrastructure"]
}' > test_input.json

# Run with replay
adk run --replay test_input.json international_system/agent.py

# Verify output format matches expectations
```

### Step 2: Test Parser with Captured Output
1. Capture ADK output to file
2. Feed to parser function
3. Verify all responses extracted
4. Check norm updates parsed correctly

### Step 3: Test Backend WebSocket
1. Start backend server
2. Connect with WebSocket client (e.g., `wscat`)
3. Send start command
4. Verify messages received in correct format

### Step 4: Test Full Integration
1. Start backend
2. Start frontend
3. Input test geopolitical event
4. Verify all 5 iterations complete
5. Check all country responses displayed
6. Verify norm charts update
7. Check analyst reasoning visible

## Success Criteria

✓ Frontend connects to backend via WebSocket
✓ Backend successfully spawns ADK Python process
✓ All country responses parsed and displayed in real-time
✓ Analyst JSON extracted and norms updated correctly
✓ All 5 iterations complete successfully
✓ No mock data visible (all responses from real agents)
✓ Error handling works for common failure modes
✓ UI updates smoothly without lag or flickering

## Rollback Plan

If integration fails:
1. Keep mock data as fallback mode
2. Add environment variable `USE_MOCK_DATA=true/false`
3. Toggle based on ADK availability
4. Display warning banner when in mock mode
5. Allows frontend development to continue independently

## Timeline Estimate

- **Backend Development**: 4-6 hours
  - Express server setup: 1 hour
  - ADK process manager: 2 hours
  - Output parsing: 2-3 hours
  - Testing: 1 hour

- **Frontend Updates**: 2-3 hours
  - WebSocket client: 1 hour
  - Remove mock data: 30 min
  - Update hooks: 1 hour
  - Testing: 30 min

- **Integration & Testing**: 2-3 hours
  - End-to-end testing: 1 hour
  - Bug fixes: 1-2 hours

**Total: 8-12 hours**

## Next Steps

1. **Validate approach** with stakeholder
2. **Test ADK CLI manually** to confirm output format
3. **Start backend development** (server + ADK manager)
4. **Implement parsing logic** with thorough testing
5. **Update frontend** to consume real data
6. **Integration testing** with full flow
7. **Deploy and monitor** for issues

This plan provides a comprehensive, bug-aware approach to connecting the React frontend with the Python ADK agents, with clear strategies for handling the complex parsing challenges and potential edge cases.
