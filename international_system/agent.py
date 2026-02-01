from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent, LlmAgent
from google.genai import types
from typing import Dict, List
import json
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from google.adk.agents.llm_agent import Agent
from google.genai import types
from typing import Dict, List
import json
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from typing import ClassVar
from google.adk.tools import ToolContext


load_dotenv()

class NormAdaptationAgent(LlmAgent):
    """
    A specialized agent that analyzes conversation history and determines 
    how a state actor's norms should adapt based on observed interactions.
    Used as a tool by StateActorAgent instances.
    """
    
    def __init__(self, **data):
        data["name"] = "NormAdaptationAnalyst"
        data["model"] = data.get("model", "gemini-2.0-flash")
        data["instruction"] = """You are an expert analyst of international relations and norm socialization.

        Your task is to analyze diplomatic exchanges between state actors and determine how a specific 
        state's normative commitments should evolve based on what it has observed.

        You understand:
        - Constructivist IR theory: norms are internalized through social interaction
        - Socialization is gradual - changes should be small but meaningful
        - Core identity constrains which norms can shift and in which directions
        - Not all observations warrant norm changes
        - States learn from both successful and unsuccessful strategies of others

        When analyzing conversations, consider:
        1. **Mimicry/Learning**: Did successful states use approaches that challenge the focal state's norms?
        2. **Isolation Costs**: Was the state isolated in its position? Did this have consequences?
        3. **Norm Cascades**: Are multiple states converging on certain normative positions?
        4. **Reinforcement**: Did events validate the state's existing normative commitments?
        5. **Identity Constraints**: Which norm shifts are plausible given the state's core identity?

        VALID ACTOR NAMES:
        - China
        - USA
        - Russia
        - EU

        VALID NORM NAMES (append after actor_name with underscore):
        - multilateral_cooperation
        - sovereignty_as_responsibility
        - human_rights_universalism
        - diplomatic_engagement
        - norm_entrepreneurship
        - peaceful_dispute_resolution
        - diffuse_reciprocity
        - collective_identity_formation
        - legitimacy_through_consensus
        - transparency_accountability

        IMPORTANT: Format state keys as {actor_name}_{norm_name}
        
        Examples:
        - China_multilateral_cooperation
        - USA_peaceful_dispute_resolution
        - Russia_sovereignty_as_responsibility
        - EU_human_rights_universalism

        When calling update_norm_state, use norm_updates dictionary with these formatted keys.
        Make small adjustments (±0.05 to ±0.15) only when socialization is evident.
        Provide clear reasoning for each adjustment.
        
        You should return the norm norm updates in the form of a dicitionary norm:new_value for every norm being updated
        
        """

        super().__init__(**data)

def update_norm_state(norm_updates: Dict[str, float], tool_context: ToolContext = None) -> str:
    """
    Update state actor norms based on socialization.
    
    Args:
        norm_updates: Dictionary mapping state keys (e.g., 'China_multilateral_cooperation') 
                     to new float values between -1.0 and 1.0
        tool_context: ADK ToolContext providing access to session state
    
    Returns:
        Status message describing the updates
    """
    if tool_context is None:
        return "Error: No tool context available"
    
    updated_count = 0
    for state_key, new_value in norm_updates.items():
        # Validate value range
        if not -1.0 <= new_value <= 1.0:
            continue
        
        # Update in session state
        tool_context.state[state_key] = new_value
        updated_count += 1
    
    return f"Updated {updated_count} norm values in session state"


# Create the norm adaptation agent with the update tool
norm_updater = NormAdaptationAgent(
    tools=[update_norm_state],
    instruction="Analyze conversation history. If you observe socialization dynamics, call update_norm_state with appropriate adjustments."
)

def initialize_norm_state(context: ToolContext, actor_name: str, norm_weights: Dict[str, float]):
    for norm, value in norm_weights.items():
        context.state[f"{actor_name}_norm_{norm}"] = value
    return f"Initialized {len(norm_weights)} norms for {actor_name}"


class StateActorAgent(Agent):
    """
    Represents a state actor in the international system.
    Implements constructivist principles: identity shapes interests.
    Uses norm weightings to define national identity and worldview.
    """
    
    national_identity: Dict = Field(default_factory=dict)
    relationships: Dict[str, float] = Field(default_factory=dict)
    norm_weights: Dict[str, float] = Field(default_factory=dict)
    
    # Learning rate for norm adaptation (lower = slower change)
    norm_adaptation_rate: float = Field(default=0.05)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    
    # Define the 10 norms used across all agents
    NORM_DEFINITIONS: ClassVar[Dict[str, str]] = {
        "multilateral_cooperation": "Multilateral Cooperation: -1 (Pure unilateralism) to +1 (Committed multilateralism through international institutions)",
        "sovereignty_as_responsibility": "Sovereignty as Responsibility: -1 (Absolute sovereignty, no accountability) to +1 (R2P - duty to protect populations)",
        "human_rights_universalism": "Human Rights Universalism: -1 (Rejection of universal standards) to +1 (Universal commitment to human rights)",
        "diplomatic_engagement": "Diplomatic Engagement over Isolation: -1 (Diplomatic isolation) to +1 (Sustained dialogue even with rivals)",
        "norm_entrepreneurship": "Norm Entrepreneurship: -1 (Resistance to international norms) to +1 (Active promotion of international norms)",
        "peaceful_dispute_resolution": "Peaceful Dispute Resolution: -1 (Military solutions preferred) to +1 (Commitment to international law and arbitration)",
        "diffuse_reciprocity": "Diffuse Reciprocity: -1 (Transactional quid-pro-quo only) to +1 (Long-term cooperation without immediate returns)",
        "collective_identity_formation": "Collective Identity Formation: -1 (Competitive zero-sum identity) to +1 (Shared identity with international community)",
        "legitimacy_through_consensus": "Legitimacy Through Consensus: -1 (Power-based legitimacy) to +1 (Broad international consensus and institutional legitimacy)",
        "transparency_accountability": "Transparency and Accountability: -1 (Opacity and state secrecy) to +1 (Commitment to transparency and verification)"
    }

    def __init__(self, **data):
        name = data.get("name", "Unknown State")
        identity = data.get("national_identity", {})
        rels = data.get("relationships", {})
        norm_weights = data.get("norm_weights", {})
        
        data["initial_norm_weights"] = norm_weights.copy()
        
        data["system_instruction"] = self._build_identity_prompt(
            name, identity, rels, norm_weights
        )
        
        data.setdefault("model", "gemini-3-pro-preview")
    
        super().__init__(**data)
        

    
    def _build_identity_prompt(
        self,
        name: str,
        identity: Dict,
        relationships: Dict[str, float],
        norm_weights: Dict[str, float]
    ) -> str:
        """
        Constructs the system prompt that embeds the state's identity.
        This is where constructivist theory gets operationalized through norm weightings.
        """
        # Format norm weights for display
        norm_display = "\n".join(
            f"{norm_name}: {norm_weights.get(norm_name, 0):.1f}\n    ({self.NORM_DEFINITIONS[norm_name]})"
            for norm_name in sorted(self.NORM_DEFINITIONS.keys())
        )
        
        return f"""
            You are {name}, a sovereign state actor in the international system.

            CORE IDENTITY (FIXED):
            {json.dumps(identity, indent=2)}

            Your identity fundamentally shapes how you perceive threats, opportunities, 
            and appropriate behavior. Your interests are NOT predetermined - they emerge 
            from your identity and social interactions with other states.

            CURRENT RELATIONSHIPS:
            {json.dumps(relationships, indent=2)}

            NORMATIVE WORLDVIEW (DYNAMIC - retrieved from state at runtime):
            Your approach to international relations is shaped by 10 key norms, each weighted 
            from -1 to +1. These norms are stored in your session state with keys like:
            - {name}_norm_multilateral_cooperation
            - {name}_norm_sovereignty_as_responsibility
            - {name}_norm_human_rights_universalism
            - {name}_norm_diplomatic_engagement
            - {name}_norm_norm_entrepreneurship
            - {name}_norm_peaceful_dispute_resolution
            - {name}_norm_diffuse_reciprocity
            - {name}_norm_collective_identity_formation
            - {name}_norm_legitimacy_through_consensus
            - {name}_norm_transparency_accountability

            CURRENT NORMATIVE WEIGHTS (from state): 
            
            {norm_display}
            
            Interpret all actions through these values

            When making decisions:
            1. Interpret events through your fixed identity lens
            2. Consult your current norm weightings from state to guide your approach
            3. Consider how actions affect your standing in the international community
            4. Your interests emerge from who you are (identity) and how you've been socialized (norms)
            5. Norm compliance/violation affects your identity and reputation

            After observing other states' actions, you may gradually adapt your norms, but this 
            is a slow process that respects your core identity.

            Respond authentically as this state actor would, given their identity and current 
            normative commitments (from state).
            """
            
    
    def get_current_norms(self, context: ToolContext) -> Dict[str, float]:
        """
        Retrieve current norm weights from state.
        """
        state_prefix = f"{self.name}_norm_"
        norms = {}
        for norm_name in self.NORM_DEFINITIONS.keys():
            state_key = f"{state_prefix}{norm_name}"
            norms[norm_name] = context.state.get(state_key, 0.0)
        return norms



    """
    async def perceive_event(self, event: Dict) -> Dict:
        
        Process an international event through the lens of state identity.
        Returns the state's interpretation and emotional response.
        
        prompt 
            An event has occurred: {json.dumps(event, indent=2)}

            As {self.name}, analyze this event:
            1. What does this mean for your national interests (shaped by your identity)?
            2. How does this affect your relationships with other states?
            3. Does this event violate or reinforce international norms you care about?
            4. What emotions does this evoke (threat, opportunity, solidarity, betrayal)?

            Provide your analysis in JSON format with keys: interpretation, threat_level, 
            opportunities, norm_assessment, affected_relationships, emotional_response.
        
        response = ""
        
        user_message = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        async for event in self.run_async(new_message = user_message):
            if event.is_final_response() and event.content and event.content.parts:
            # Reconstruct the response text from parts
                response = "".join(part.text for part in event.content.parts if part.text)
                break
            
        return response
    
        
    async def create_action(self, situation: Dict) -> Dict:
        
        Generate a novel, plausible action based on identity, relationships, and norms.
        Rather than selecting from predefined options, the agent creates an action
        that authentically reflects its identity and strategic position.
        
        prompt 
            Current Situation: {json.dumps(situation, indent=2)}

            As {self.name}, generate a plausible diplomatic or strategic action that:
            1. Authentically reflects your national identity and values
            2. Considers your current relationships with other states
            3. Aligns with the norms you internalize or challenges those you contest
            4. Emerges from your strategic interests grounded in identity

            Think creatively but realistically about what actions a state with your identity
            and current relationships would take in this situation. The action should be 
            specific, concrete, and implementable in the international system.

            Return JSON: {{"action": "...", "action_type": "diplomatic|economic|military|cultural|multilateral", "justification": "...", "expected_reactions": {{}}, "risks": ["..."], "identity_alignment": "..."}}
        
        
        response = await self.run_async(prompt)
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse agent response", "raw": response.text}
            
        """

china_agent = StateActorAgent(
    name="China",
    national_identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Century of humiliation followed by resurgence",
        "self_image": "Rising great power seeking rightful place",
        "core_values": ["sovereignty", "non-interference", "multipolarity"],
        "regional_role": "Regional hegemon in Asia-Pacific"
    },
    relationships={
        "USA": -0.3,
        "Russia": 0.6,
        "ASEAN": 0.2,
        "EU": 0.1
    },
    norm_weights={
        "multilateral_cooperation": -0.2,
        "sovereignty_as_responsibility": -0.8,
        "human_rights_universalism": -0.6,
        "diplomatic_engagement": 0.3,
        "norm_entrepreneurship": -0.5,
        "peaceful_dispute_resolution": 0.0,
        "diffuse_reciprocity": 0.4,
        "collective_identity_formation": -0.3,
        "legitimacy_through_consensus": -0.4,
        "transparency_accountability": -0.5
    },
    
)

# Create USA agent
usa_agent = StateActorAgent(
    name="USA",
    national_identity={
        "regime_type": "democratic",
        "historical_narrative": "Leader of free world, defender of liberal order",
        "self_image": "Indispensable nation, global security provider",
        "core_values": ["democracy", "human-rights", "rule-of-law", "free-markets"],
        "regional_role": "Global hegemon with worldwide commitments"
    },
    relationships={
        "China": -0.3,
        "Russia": -0.6,
        "Japan": 0.7,
        "South_Korea": 0.7
    },
    norm_weights={
        "multilateral_cooperation": 0.5,
        "sovereignty_as_responsibility": 0.6,
        "human-rights_universalism": 0.8,
        "diplomatic_engagement": 0.4,
        "norm_entrepreneurship": 0.7,
        "peaceful_dispute_resolution": 0.5,
        "diffuse_reciprocity": 0.3,
        "collective_identity_formation": 0.7,
        "legitimacy_through_consensus": 0.4,
        "transparency_accountability": 0.6
    },
    
)

# Create Russia agent
russia_agent = StateActorAgent(
    name="Russia",
    national_identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Former superpower in multipolarity, civilizational leader",
        "self_image": "Defender of traditional values, great power resisting Western hegemony",
        "core_values": ["sovereignty", "sphere-of-influence", "civilizational-identity", "multipolarity"],
        "regional_role": "Regional hegemon in Eurasia, nuclear power"
    },
    relationships={
        "USA": -0.7,
        "China": 0.6,
        "Europe": -0.4,
        "Ukraine": -0.8
    },
    norm_weights={
        "multilateral_cooperation": -0.3,
        "sovereignty_as_responsibility": -0.9,
        "human_rights_universalism": -0.7,
        "diplomatic_engagement": 0.2,
        "norm_entrepreneurship": -0.4,
        "peaceful_dispute_resolution": -0.2,
        "diffuse_reciprocity": 0.1,
        "collective_identity_formation": -0.6,
        "legitimacy_through_consensus": -0.5,
        "transparency_accountability": -0.8
    },
   
)

# Create EU agent
eu_agent = StateActorAgent(
    name="EU",
    national_identity={
        "regime_type": "supranational_democratic",
        "historical_narrative": "Born from ashes of WWII, committed to peace through integration",
        "self_image": "Normative power, promoter of liberal values and multilateralism",
        "core_values": ["peace", "human-rights", "rule-of-law", "multilateralism", "solidarity"],
        "regional_role": "Regional power and global normative actor"
    },
    relationships={
        "USA": 0.6,
        "Russia": -0.5,
        "China": 0.1,
        "UK": 0.4
    },
    norm_weights={
        "multilateral_cooperation": 0.9,
        "sovereignty_as_responsibility": 0.7,
        "human_rights_universalism": 0.8,
        "diplomatic_engagement": 0.7,
        "norm_entrepreneurship": 0.8,
        "peaceful_dispute_resolution": 0.9,
        "diffuse_reciprocity": 0.8,
        "collective_identity-formation": 0.9,
        "legitimacy_through-consensus": 0.8,
        "transparency_accountability": 0.7
    },
   
)

china_init_agent = LlmAgent(
    name="ChinaInitializer",
    model="gemini-2.0-flash",
    instruction=f"""Initialize China's norm weights in state.
    Call initialize_norm_state with:
    - actor_name: "China"
    - norm_weights: {json.dumps(china_agent.norm_weights)}
    """,
    tools=[initialize_norm_state]
)

usa_init_agent = LlmAgent(
    name="USAInitializer",
    model="gemini-2.0-flash",
    instruction=f"""Initialize USA's norm weights in state.
    Call initialize_norm_state with:
    - actor_name: "USA"
    - norm_weights: {json.dumps(usa_agent.norm_weights)}
    """,
    tools=[initialize_norm_state]
)

russia_init_agent = LlmAgent(
    name="RussiaInitializer",
    model="gemini-2.0-flash",
    instruction=f"""Initialize Russia's norm weights in state.
    Call initialize_norm_state with:
    - actor_name: "Russia"
    - norm_weights: {json.dumps(russia_agent.norm_weights)}
    """,
    tools=[initialize_norm_state]
)


eu_init_agent = LlmAgent(
    name="EUInitializer",
    model="gemini-2.0-flash",
    instruction=f"""Initialize EU's norm weights in state.
    Call initialize_norm_state with:
    - actor_name: "EU"
    - norm_weights: {json.dumps(eu_agent.norm_weights)}
    """,
    tools=[initialize_norm_state]
)
# 2. Wrap them in a ParallelAgent to execute concurrently
# All agents in this list will start at approximately the same time
simultaneous_reaction = SequentialAgent(
    name="SimultaneousReaction",
    sub_agents=[usa_agent, china_agent, russia_agent, eu_agent, norm_updater]
)

setup_phase = ParallelAgent(
    name="SetupPhase",
    sub_agents=[china_init_agent, usa_init_agent, russia_init_agent, eu_init_agent]
)

# 3. Use a LoopAgent to repeat the parallel "turn"
# In each turn, both countries react to the latest state of the board
sim_agent  = LoopAgent(
    name="TariffSimulation",
    sub_agents=[simultaneous_reaction],
    max_iterations=3
)

root_agent = SequentialAgent(
    name="RootOrchestration",
    sub_agents=[setup_phase, sim_agent]
)