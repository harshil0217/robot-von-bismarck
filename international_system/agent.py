from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent, LlmAgent
from google.adk.runners import Runner
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

load_dotenv()

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
    NORM_DEFINITIONS = {
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

            CORE IDENTITY:
            {json.dumps(identity, indent=2)}

            Your identity fundamentally shapes how you perceive threats, opportunities, 
            and appropriate behavior. Your interests are NOT predetermined - they emerge 
            from your identity and social interactions with other states.

            NORMATIVE WORLDVIEW (scaled -1 to +1):
            These norm weightings define your approach to international relations:
            
            {norm_display}

            CURRENT RELATIONSHIPS:
            {json.dumps(relationships, indent=2)}

            When making decisions:
            1. Interpret events through your identity lens and normative worldview
            2. Your norm weightings fundamentally shape how you respond to situations
            3. Consider how actions affect your standing in the international community
            4. Your interests emerge from who you are, not material capabilities alone
            5. Norm compliance/violation affects your identity and reputation

            Respond authentically as this state actor would, given their identity and normative commitments.
        """


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
    }
)

# Create USA agent
usa_agent = StateActorAgent(
    name="United_States",
    national_identity={
        "regime_type": "democratic",
        "historical_narrative": "Leader of free world, defender of liberal order",
        "self_image": "Indispensable nation, global security provider",
        "core_values": ["democracy", "human_rights", "rule_of_law", "free_markets"],
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
        "human_rights_universalism": 0.8,
        "diplomatic_engagement": 0.4,
        "norm_entrepreneurship": 0.7,
        "peaceful_dispute_resolution": 0.5,
        "diffuse_reciprocity": 0.3,
        "collective_identity_formation": 0.7,
        "legitimacy_through_consensus": 0.4,
        "transparency_accountability": 0.6
    }
)

# Create Russia agent
russia_agent = StateActorAgent(
    name="Russia",
    national_identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Former superpower in multipolarity, civilizational leader",
        "self_image": "Defender of traditional values, great power resisting Western hegemony",
        "core_values": ["sovereignty", "sphere_of_influence", "civilizational_identity", "multipolarity"],
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
    }
)

# Create EU agent
eu_agent = StateActorAgent(
    name="European_Union",
    national_identity={
        "regime_type": "supranational_democratic",
        "historical_narrative": "Born from ashes of WWII, committed to peace through integration",
        "self_image": "Normative power, promoter of liberal values and multilateralism",
        "core_values": ["peace", "human_rights", "rule_of_law", "multilateralism", "solidarity"],
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
        "collective_identity_formation": 0.9,
        "legitimacy_through_consensus": 0.8,
        "transparency_accountability": 0.7
    }
)

# 2. Wrap them in a ParallelAgent to execute concurrently
# All agents in this list will start at approximately the same time
simultaneous_reaction = SequentialAgent(
    name="SimultaneousReaction",
    sub_agents=[usa_agent, china_agent, russia_agent, eu_agent]
)

# 3. Use a LoopAgent to repeat the parallel "turn"
# In each turn, both countries react to the latest state of the board
root_agent  = LoopAgent(
    name="TariffSimulation",
    sub_agents=[simultaneous_reaction],
    max_iterations=3
)