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

    async def perceive_event(self, event: Dict) -> Dict:
        """
        Process an international event through the lens of state identity.
        Returns the state's interpretation and emotional response.
        """
        prompt = f"""
            An event has occurred: {json.dumps(event, indent=2)}

            As {self.name}, analyze this event:
            1. What does this mean for your national interests (shaped by your identity)?
            2. How does this affect your relationships with other states?
            3. Does this event violate or reinforce international norms you care about?
            4. What emotions does this evoke (threat, opportunity, solidarity, betrayal)?

            Provide your analysis in JSON format with keys: interpretation, threat_level, 
            opportunities, norm_assessment, affected_relationships, emotional_response.
        """
        response = ""
        
        async for event in self.run_async(prompt):
            if event.is_final_response() and event.content and event.content.parts:
            # Reconstruct the response text from parts
                response = "".join(part.text for part in event.content.parts if part.text)
                break
            
            return response
    
        
    async def create_action(self, situation: Dict) -> Dict:
        """
        Generate a novel, plausible action based on identity, relationships, and norms.
        Rather than selecting from predefined options, the agent creates an action
        that authentically reflects its identity and strategic position.
        """
        prompt = f"""
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
        """
        
        response = await self.run_async(prompt)
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse agent response", "raw": response.text}