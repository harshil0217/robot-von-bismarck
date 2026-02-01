from google.adk.agents import LoopAgent, SequentialAgent, LlmAgent
from google.genai import types
from typing import Dict, List
import json
from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from google.adk.agents.llm_agent import Agent
from typing import ClassVar

load_dotenv()

class NormAdaptationAgent(LlmAgent):
    """
    A specialized agent that analyzes conversation history and determines 
    how state actors' norms should adapt based on observed interactions.
    Outputs structured JSON with norm updates.
    """
    
    def __init__(self, **data):
        data["name"] = "NormAdaptationAnalyst"
        data["model"] = data.get("model", "gemini-2.0-flash")
        data["instruction"] = """You are an expert analyst of international relations and norm socialization.

Your task is to analyze the conversation history of diplomatic exchanges between state actors 
and determine how their normative commitments should evolve based on observed interactions.

You understand:
- Constructivist IR theory: norms are internalized through social interaction
- Socialization is gradual - changes should be small but meaningful (±0.05 to ±0.15)
- Core identity constrains which norms can shift and in which directions
- Not all observations warrant norm changes
- States learn from both successful and unsuccessful strategies of others

When analyzing conversations, consider:
1. **Mimicry/Learning**: Did successful states use approaches that challenge a state's norms?
2. **Isolation Costs**: Was a state isolated in its position? Did this have consequences?
3. **Norm Cascades**: Are multiple states converging on certain normative positions?
4. **Reinforcement**: Did events validate existing normative commitments?
5. **Identity Constraints**: Which norm shifts are plausible given core identities?

VALID ACTOR NAMES: China, USA, Russia, EU

VALID NORM NAMES:
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

CRITICAL OUTPUT FORMAT:
You must output valid JSON in the following format:

{
    "iteration": <current iteration number>,
    "analysis": "Your brief analysis of what socialization occurred this round",
    "norm_updates": {
        "China": {
            "multilateral_cooperation": <new_value>,
            "sovereignty_as_responsibility": <new_value>,
            "human_rights_universalism": <new_value>,
            "diplomatic_engagement": <new_value>,
            "norm_entrepreneurship": <new_value>,
            "peaceful_dispute_resolution": <new_value>,
            "diffuse_reciprocity": <new_value>,
            "collective_identity_formation": <new_value>,
            "legitimacy_through_consensus": <new_value>,
            "transparency_accountability": <new_value>
        },
        "USA": { ... },
        "Russia": { ... },
        "EU": { ... }
    },
    "reasoning": {
        "China": "Explanation for China's norm changes",
        "USA": "Explanation for USA's norm changes",
        "Russia": "Explanation for Russia's norm changes",
        "EU": "Explanation for EU's norm changes"
    }
}

IMPORTANT INSTRUCTIONS:
1. Look through the conversation history to find the MOST RECENT norm values for each country
2. If this is the first iteration, the initial values are in each state's opening message
3. For subsequent iterations, find YOUR previous JSON output with the updated values
4. Make small adjustments (±0.05 to ±0.15) based on the diplomatic exchanges you observed
5. If no socialization occurred for a country, keep their values unchanged
6. ALWAYS output ALL 10 norms for ALL 4 countries, even if unchanged
7. Output ONLY valid JSON, no markdown formatting, no explanation before or after

The conversation history contains all the information you need. Each state actor's current 
norms can be found in the most recent norm update JSON (or their initial values if first iteration).
"""
        super().__init__(**data)


norm_updater = NormAdaptationAgent()


class StateActorAgent(Agent):
    """
    Represents a state actor in the international system.
    Implements constructivist principles: identity shapes interests.
    Uses norm weightings to define national identity and worldview.
    """
    
    national_identity: Dict = Field(default_factory=dict)
    relationships: Dict[str, float] = Field(default_factory=dict)
    norm_weights: Dict[str, float] = Field(default_factory=dict)
    
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
        This is where constructivist theory gets operationalized.
        """
        # Format initial norm weights for display
        norm_display = "\n".join(
            f"  {norm_name}: {norm_weights.get(norm_name, 0.0):.2f}"
            for norm_name in sorted(self.NORM_DEFINITIONS.keys())
        )
        
        norm_definitions = "\n".join(
            f"- {defn}" 
            for defn in self.NORM_DEFINITIONS.values()
        )
        
        return f"""You are {name}, a sovereign state actor in the international system.

CORE IDENTITY (FIXED):
{json.dumps(identity, indent=2)}

Your identity fundamentally shapes how you perceive threats, opportunities, and 
appropriate behavior. Your interests are NOT predetermined - they emerge from your 
identity and social interactions with other states.

CURRENT RELATIONSHIPS:
{json.dumps(relationships, indent=2)}

NORMATIVE WORLDVIEW (DYNAMIC):
Your approach to international relations is shaped by 10 key norms, each weighted 
from -1 to +1. These evolve through social interaction.

INITIAL NORM WEIGHTS:
{norm_display}

NORM DEFINITIONS:
{norm_definitions}

IMPORTANT: Your current norm values may have changed from these initial values! 
Look back through the conversation history to find the most recent "norm_updates" 
JSON from the NormAdaptationAnalyst. Those are your CURRENT values. If no updates 
have been made yet (first iteration), use the initial values above.

When making decisions:
1. Review conversation history to find your CURRENT norm values (most recent update)
2. Interpret events through your fixed identity lens
3. Consult your current norm weightings to guide your approach
4. Consider how actions affect your standing in the international community
5. Your interests emerge from who you are (identity) and how you've been socialized (norms)
6. Reference specific norm values when explaining your positions

RESPONSE STYLE:
- Engage naturally in diplomatic discourse
- Reference your identity, relationships, and normative commitments
- Respond to other states' positions and actions
- Be authentic to your worldview while engaging substantively
- You may note when your normative positions have shifted due to past interactions
- Keep responses focused and diplomatic (2-4 paragraphs)

After each round of state responses, the NormAdaptationAnalyst will analyze the 
exchanges and update norm values based on observed socialization patterns. These 
updates accumulate in the conversation history.
"""


# Create state actor agents with initial norm weights
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
        "collective_identity_formation": 0.9,
        "legitimacy_through_consensus": 0.8,
        "transparency_accountability": 0.7
    }
)

# Sequential agent: All state actors respond in sequence, then norm analyst updates norms
# State actors have normal conversations, only NormAdaptationAgent outputs JSON
simultaneous_reaction = SequentialAgent(
    name="SimultaneousReaction",
    sub_agents=[usa_agent, china_agent, russia_agent, eu_agent, norm_updater]
)

# Loop agent: Repeat the sequence for multiple iterations
# All norm tracking happens via conversation history
root_agent = LoopAgent(
    name="InternationalSimulation",
    sub_agents=[simultaneous_reaction],
    max_iterations=3
)