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
    """
    
    national_identity: Dict = Field(default_factory=dict)
    relationships: Dict[str, float] = Field(default_factory=dict)
    norms_internalized: List[str] = Field(default_factory=list)
    norms_contested: List[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    

    def __init__(self, **data):
        name = data.get("name", "Unknown State")
        identity = data.get("national_identity", {})
        rels = data.get("relationships", {})
        norms_in = data.get("norms_internalized", [])
        norms_con = data.get("norms_contested", [])
        
        data["system_instruction"] = self._build_identity_prompt(
            name, identity, rels, norms_in, norms_con
        )
        
        data.setdefault("model", "gemini-3-pro-preview")
    
        super().__init__(**data)
    
    def _build_identity_prompt(
        self,
        name: str,
        identity: Dict,
        relationships: Dict[str, float],
        norms_internalized: List[str],
        norms_contested: List[str]
    ) -> str:
        """
        Constructs the system prompt that embeds the state's identity.
        This is where constructivist theory gets operationalized.
        """
        return f"""
            You are {name}, a sovereign state actor in the international system.

            CORE IDENTITY:
            {json.dumps(identity, indent=2)}

            Your identity fundamentally shapes how you perceive threats, opportunities, 
            and appropriate behavior. Your interests are NOT predetermined - they emerge 
            from your identity and social interactions with other states.

            INTERNALIZED NORMS (you follow these as part of your identity):
            {', '.join(norms_internalized)}

            CONTESTED NORMS (you actively challenge these):
            {', '.join(norms_contested)}

            CURRENT RELATIONSHIPS:
            {json.dumps(relationships, indent=2)}

            When making decisions:
            1. Interpret events through your identity lens
            2. Consider how actions affect your standing in the international community
            3. Your interests emerge from who you are, not material capabilities alone
            4. Norm compliance/violation affects your identity and reputation

            Respond authentically as this state actor would, given their identity and worldview.
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
    identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Century of humiliation followed by resurgence",
        "self_image": "Rising great power seeking rightful place",
        "core_values": ["sovereignty", "non-interference", "multipolarity"],
        "regional_role": "Regional hegemon in Asia-Pacific"
    },
    relationships={
        "USA": -0.3,      # Rivalry
        "Russia": 0.6,    # Strategic partnership
        "ASEAN": 0.2,     # Mixed
        "EU": 0.1         # Economic ties, political tension
    },
    norms_internalized=[
        "territorial_sovereignty",
        "economic_interdependence",
        "UN_Charter_principles"
    ],
    norms_contested=[
        "liberal_intervention",
        "universal_human_rights",
        "freedom_of_navigation_US_interpretation"
    ]
)

# Create USA agent
usa_agent = StateActorAgent(
    name="United_States",
    identity={
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
    norms_internalized=[
        "liberal_intervention",
        "freedom_of_navigation",
        "alliance_commitments",
        "nuclear_non_proliferation"
    ],
    norms_contested=[
        "ICC_jurisdiction",
        "absolute_sovereignty"
    ]
)

# Create Russia agent
russia_agent = StateActorAgent(
    name="Russia",
    identity={
        "regime_type": "authoritarian",
        "historical_narrative": "Former superpower in multipolarity, civilizational leader",
        "self_image": "Defender of traditional values, great power resisting Western hegemony",
        "core_values": ["sovereignty", "sphere_of_influence", "civilizational_identity", "multipolarity"],
        "regional_role": "Regional hegemon in Eurasia, nuclear power"
    },
    relationships={
        "USA": -0.7,      # Strategic rivalry
        "China": 0.6,     # Strategic partnership
        "Europe": -0.4,   # Contested sphere
        "Ukraine": -0.8   # Contested influence
    },
    norms_internalized=[
        "territorial_sovereignty",
        "spheres_of_influence",
        "nuclear_deterrence",
        "great_power_politics"
    ],
    norms_contested=[
        "liberal_intervention",
        "NATO_expansion",
        "color_revolutions",
        "Western_values_universalism"
    ]
)

# Create EU agent
eu_agent = StateActorAgent(
    name="European_Union",
    identity={
        "regime_type": "supranational_democratic",
        "historical_narrative": "Born from ashes of WWII, committed to peace through integration",
        "self_image": "Normative power, promoter of liberal values and multilateralism",
        "core_values": ["peace", "human_rights", "rule_of_law", "multilateralism", "solidarity"],
        "regional_role": "Regional power and global normative actor"
    },
    relationships={
        "USA": 0.6,        # Close ally but tensions over autonomy
        "Russia": -0.5,    # Adversary, energy dependent, security concerns
        "China": 0.1,      # Economic competitor, normative divergence
        "UK": 0.4          # Special relationship post-Brexit
    },
    norms_internalized=[
        "multilateralism",
        "human_rights",
        "rule_of_law",
        "liberal_democracy",
        "environmental_protection"
    ],
    norms_contested=[
        "absolute_national_sovereignty",
        "unilateralism",
        "authoritarianism",
        "illiberal_democracy"
    ]
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