# Robot Von Bismarck - Geopolitical Simulation System

A sophisticated multi-agent system that simulates geopolitical interactions between major world powers (USA, China, Russia, EU) and models how their ideological norms evolve through diplomatic exchanges, based on constructivist international relations theory.

## 🌍 Project Overview

This project implements a constructivist IR framework where state actors have dynamic normative worldviews that evolve through social interaction. Countries respond to geopolitical events based on their identities, and their norms adapt gradually through repeated diplomatic exchanges.

### Key Features

- **Multi-Agent Simulation:** Four country agents with distinct identities and initial norm positions
- **Dynamic Norm Evolution:** 10 ideological dimensions that shift through interaction
- **Expert Analysis:** AI analyst that interprets socialization patterns and updates norms
- **Interactive Frontend:** React-based visualization of real-time simulation results
- **Constructivist Theory:** Implementation of academic IR theory in practice

## 🏗️ Architecture

```
robot-von-bismarck/
├── international_system/     # Python ADK agents
│   ├── agent.py             # Country and analyst agents
│   └── __init__.py
├── frontend/                # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── services/        # ADK integration
│   │   ├── hooks/           # React state management
│   │   └── types/           # TypeScript definitions
│   └── public/
│       └── initial_norms.json
├── initial_norms.json       # Starting norm values
├── PLAN.md                 # Detailed implementation plan
└── CLAUDE.md               # Original specifications
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with Google ADK installed
- Node.js 16+ and npm
- Git

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository>
   cd robot-von-bismarck
   ```

2. **Backend Setup:**
   ```bash
   # Install ADK and dependencies (see Google ADK documentation)
   pip install google-adk
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access Application:**
   Open [http://localhost:3000](http://localhost:3000)

### Running Simulations

#### Via Frontend (Recommended)
1. Navigate to the web interface
2. Enter a geopolitical event (e.g., "Major trade sanctions imposed")
3. Click "Start Simulation"
4. Watch countries respond and norms evolve over 5 iterations

#### Via Command Line
```bash
# From international_system directory
adk run agent.py

# Or using TypeScript
npx @google/adk-devtools run agent.ts
```

## 🎯 How It Works

### The 10 Ideological Norms

Each country is characterized by positions on 10 key norms (scale: -1 to +1):

1. **Multilateral Cooperation** - Preference for international institutions
2. **Sovereignty as Responsibility** - R2P vs. absolute sovereignty  
3. **Human Rights Universalism** - Universal vs. relative standards
4. **Diplomatic Engagement** - Dialogue vs. isolation
5. **Norm Entrepreneurship** - Promoting vs. resisting international norms
6. **Peaceful Dispute Resolution** - Law vs. force
7. **Diffuse Reciprocity** - Long-term vs. transactional cooperation
8. **Collective Identity Formation** - Shared vs. competitive identity
9. **Legitimacy Through Consensus** - Institutional vs. power-based legitimacy
10. **Transparency & Accountability** - Openness vs. secrecy

### Country Profiles

**🇺🇸 USA:** Democratic hegemon, promotes liberal international order
- High: Human rights, multilateral cooperation (selective), norm entrepreneurship
- Mixed: Sovereignty (R2P supporter but sovereignty-conscious)

**🇨🇳 China:** Rising power, sovereignty-focused, selective engagement  
- High: Sovereignty as non-interference, diplomatic engagement (bilateral)
- Low: Human rights universalism, multilateral cooperation (Western-led)

**🇷🇺 Russia:** Great power, challenges Western hegemony
- High: Sovereignty (absolute), opposition to Western norms
- Low: Human rights universalism, transparency, consensus legitimacy

**🇪🇺 EU:** Normative power, multilateralism champion
- High: Multilateral cooperation, human rights, peaceful resolution
- Strong: Transparency, consensus-building, norm entrepreneurship

### Simulation Process

1. **Event Input:** Geopolitical scenario introduced
2. **Sequential Response:** Each country responds based on identity + norms  
3. **Norm Analysis:** AI analyst examines interactions for socialization patterns
4. **Norm Updates:** Values adjusted based on observed social dynamics
5. **Iteration:** Process repeats for 5 rounds to show evolution

### Constructivist Principles

- **Identity → Interests:** Core identity shapes how events are interpreted
- **Norms Are Social:** Values emerge from interaction, not just material interests  
- **Gradual Socialization:** Change happens through repeated contact
- **Legitimacy Matters:** International standing affects behavior
- **Context Dependency:** History and relationships influence responses

## 📊 Frontend Features

### Real-Time Visualization
- **Country Response Grid:** Four panels with flag emojis and color coding
- **Interactive Norms Charts:** Bar charts and radar plots of value evolution  
- **Analysis Dashboard:** Expert interpretation and reasoning
- **Progress Tracking:** Iteration counter and simulation controls

### UI Components
- **Chat Interface:** Input field for geopolitical events
- **Agent Grid:** Sequential country responses with timestamps
- **Norms Panel:** Interactive visualizations with tooltips
- **Analysis Modal:** Detailed reasoning and change explanations

## 🔧 Technical Implementation

### Backend (Python + ADK)
- **StateActorAgent:** Core country agent class with identity/norms
- **NormAdaptationAgent:** AI analyst for socialization detection
- **SequentialAgent:** Orchestrates country response sequence
- **LoopAgent:** Manages 5-iteration cycles

### Frontend (React + TypeScript)
- **useSimulation Hook:** Manages simulation state and ADK communication
- **Component Architecture:** Modular UI with clear separation of concerns
- **Service Layer:** Abstracts ADK integration with mock fallbacks
- **Type Safety:** Full TypeScript coverage for robust development

### Data Flow
```
User Input → ADK Service → Country Agents → Responses
     ↓
Analysis Agent → Norm Updates → Frontend Visualization
     ↓  
Next Iteration (5x) → Final Results
```

## 📈 Example Use Cases

### Academic Research
- Study norm emergence in international relations
- Test constructivist hypotheses about socialization
- Analyze great power competition dynamics

### Policy Analysis  
- Simulate response to trade wars, sanctions, conflicts
- Explore diplomatic strategy effectiveness
- Model alliance formation and breakdown

### Education
- Interactive IR theory demonstration
- Case study development for classrooms
- Training for diplomatic simulation exercises

## 🛠️ Development

### Adding New Countries
1. Define identity profile in `agent.py`
2. Set initial norm values in `initial_norms.json`  
3. Add country metadata to frontend `types/simulation.ts`
4. Update UI components for new flag/colors

### Modifying Norms
1. Update norm definitions in both backend and frontend
2. Adjust visualization components for new scales
3. Update analyst prompts for new norm interpretations

### Custom Scenarios
- Modify `initial_norms.json` for different starting conditions
- Create scenario templates with pre-filled events
- Implement saved simulation states

### Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend testing with ADK
adk test agent.py
```

## 📚 Academic Background

This implementation draws from:

- **Constructivist IR Theory:** Wendt, Finnemore, Checkel, Risse
- **Norm Socialization:** Flockhart, Schimmelfennig, Johnston  
- **Great Power Relations:** Keohane, Ikenberry, Mearsheimer
- **Multi-Agent Systems:** Cederman, Axelrod, Harrison

## 🤝 Contributing

### Research Collaboration
- Norm definition refinement based on IR literature
- Country profile validation with area experts
- Socialization pattern analysis and improvement

### Technical Development  
- Backend integration improvements
- Frontend UX enhancements
- Performance optimization
- Additional visualization options

### Documentation
- Academic paper citations and methodology
- User guides and tutorial development
- Case study creation

## 📄 License & Citation

[Specify license]

**Citing This Work:**
```
[Author]. Robot Von Bismarck: A Multi-Agent Simulation of Geopolitical 
Norm Evolution. [Year]. [Repository URL].
```

## 🔗 Resources

- [Google ADK Documentation](https://github.com/google/adk)
- [Constructivist IR Theory Reading List](link)
- [International Relations Norms Database](link)
- [Diplomatic Simulation Best Practices](link)

---

**Built for advancing understanding of international relations through computational simulation**

*"Politics is the art of the possible, the attainable — the art of the next best."* - Otto von Bismarck