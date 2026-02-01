# Running the Robot Von Bismarck Frontend

This application consists of two parts:
1. **Backend Server** - Node.js/Express server with WebSocket support that spawns Python ADK agents
2. **Frontend** - React application that displays the simulation

## Prerequisites

1. **Node.js** (v16 or higher)
2. **Python** (v3.8 or higher)
3. **Google ADK** installed and configured
4. **Environment variables** set up (`.env` file in project root)

## Installation

From the `frontend` directory:

```bash
npm install
```

## Running the Application

### Option 1: Run Both Together (Recommended)

This will start both the backend server and the frontend development server:

```bash
npm run dev
```

- Frontend will be available at: `http://localhost:3000`
- Backend WebSocket server will run on: `ws://localhost:3001`

### Option 2: Run Separately

**Terminal 1 - Backend Server:**
```bash
npm run server:watch
```

**Terminal 2 - Frontend:**
```bash
npm start
```

## How It Works

### 1. Backend Server (`server/index.ts`)
- Listens for WebSocket connections on port 3001
- Receives simulation start requests from frontend
- Spawns Python ADK CLI process using `child_process`
- Parses ADK agent output line-by-line
- Sends parsed responses back to frontend via WebSocket

### 2. Output Parser (`server/outputParser.ts`)
- Parses country responses: `[USA] said: ...`
- Parses analyst JSON: `{"iteration": 1, "norm_updates": {...}, ...}`
- Handles multi-line responses
- Accumulates JSON across line breaks

### 3. ADK Manager (`server/adkManager.ts`)
- Creates temporary input JSON file for ADK
- Spawns: `adk run --replay <input.json> international_system/agent.py`
- Captures stdout and passes to parser
- Handles process lifecycle and cleanup

### 4. Frontend Service (`src/services/adkService.ts`)
- Establishes WebSocket connection to backend
- Event-driven architecture with `.on()` handlers
- Auto-reconnection with exponential backoff
- Emits events for country responses, analyst updates, errors

### 5. React Hook (`src/hooks/useSimulation.ts`)
- Manages simulation state
- Connects to WebSocket on component mount
- Registers event handlers for real-time updates
- Updates UI as responses arrive

## Architecture Flow

```
User Input (Geopolitical Event)
    ↓
React Frontend (localhost:3000)
    ↓ (WebSocket)
Node.js Backend (localhost:3001)
    ↓ (spawn child process)
Python ADK CLI (`adk run --replay ...`)
    ↓
ADK Agents (USA, China, Russia, EU, NormAdaptationAnalyst)
    ↓ (stdout)
Output Parser (parse country responses & analyst JSON)
    ↓ (WebSocket)
React Frontend (display in real-time)
```

## Debugging

### Check Backend Server
```bash
# View backend logs
npm run server
```

Look for:
- `Server running on port 3001`
- `WebSocket server ready`
- `Client connected` (when frontend connects)

### Check ADK Process
The backend will log:
- `Starting ADK process...`
- `ADK output: [line]` for each line of agent output
- `ADK process exited with code 0` on completion

### Check Frontend Connection
Open browser console (F12), look for:
- `Connecting to WebSocket server: ws://localhost:3001`
- `WebSocket connected`
- `Received message: [type]`

### Common Issues

**Issue: "WebSocket connection timeout"**
- Solution: Make sure backend server is running (`npm run server`)
- Check that port 3001 is not blocked by firewall

**Issue: "ADK process error"**
- Solution: Ensure Python ADK is installed (`pip install google-adk`)
- Check that `.env` file has correct API keys
- Verify `international_system/agent.py` exists

**Issue: "Failed to parse JSON"**
- Solution: Check ADK agent output format
- Ensure NormAdaptationAgent returns valid JSON
- Look at backend console for unparsed lines

**Issue: Country responses not appearing**
- Solution: Check if ADK agents are outputting `[Country] said:` format
- Look at backend logs for `ADK output:`
- Verify parser is detecting country markers

## Testing Without ADK (Mock Mode)

If you want to develop the frontend without running actual ADK agents, you can add a fallback mock mode:

1. Set environment variable: `USE_MOCK_DATA=true`
2. Backend will return mock responses instead of spawning ADK

(Note: This feature is not yet implemented but can be added if needed)

## Building for Production

```bash
# Build frontend
npm run build

# Build backend
npm run build:server

# The built files will be in:
# - Frontend: ./build/
# - Backend: ./server/dist/
```

## Environment Variables

Create `.env` file in project root:

```
# Google AI API Key (for ADK agents)
GEMINI_API_KEY=your_key_here

# Optional: Custom backend port
PORT=3001
```

## File Structure

```
frontend/
├── server/                    # Backend Node.js server
│   ├── index.ts              # Express + WebSocket server
│   ├── adkManager.ts         # ADK process spawning
│   ├── outputParser.ts       # Parse ADK output
│   ├── types.ts              # TypeScript types
│   └── tsconfig.json         # Backend TypeScript config
├── src/                       # React frontend
│   ├── services/
│   │   └── adkService.ts     # WebSocket client
│   ├── hooks/
│   │   └── useSimulation.ts  # Simulation state hook
│   ├── components/           # React components
│   └── App.tsx              # Main app component
├── public/
│   └── initial_norms.json   # Initial norm values
└── package.json
```

## Troubleshooting

### Port Already in Use

If port 3000 or 3001 is already in use:

```bash
# Kill process on port 3000 (frontend)
npx kill-port 3000

# Kill process on port 3001 (backend)
npx kill-port 3001
```

### ADK Not Found

```bash
# Install ADK globally
pip install google-adk

# Or in venv
cd ../
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install google-adk
```

### TypeScript Errors

```bash
# Clear TypeScript cache
rm -rf node_modules/.cache

# Reinstall
npm install
```

## Next Steps

- Run `npm run dev` to start both servers
- Open `http://localhost:3000` in browser
- Enter a geopolitical event
- Watch as country agents respond in real-time
- View norm updates in the sidebar
- See final analysis after 5 iterations

## Need Help?

Check the following:
1. Backend console logs for errors
2. Browser console (F12) for frontend errors
3. ADK CLI works manually: `adk run international_system/agent.py`
4. Python environment is activated
5. All dependencies are installed (`npm install`)
