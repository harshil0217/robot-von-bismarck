from google.adk.agents.llm_agent import Agent
from typing import Dict, List
import json
from dotenv import load_dotenv

load_dotenv()

class StateActorAgent(Agent):
    """
    Represents a state actor in the international system.
    Implements constructivist principles: identity shapes interests.
    """
    
    def __init__(
        self,
        name: str,
        identity: Dict,
        relationships: Dict[str, float],
        norms_internalized: List[str],
        norms_contested: List[str]
    ):
        # Core identity (constructivist foundation)
        self.national_identity = identity
        self.relationships = relationships  # Trust levels with other states
        self.norms_internalized = norms_internalized
        self.norms_contested = norms_contested
        
        # Build system instruction that embeds identity
        system_instruction = self._build_identity_prompt()
        
        super().__init__(
            name=name,
            model="gemini-3-pro-preview",
            system_instruction=system_instruction,
            thinking_level="high"  # Deep reasoning for strategic decisions
        )
    
    def _build_identity_prompt(self) -> str:
        """
        Constructs the system prompt that embeds the state's identity.
        This is where constructivist theory gets operationalized.
        """
        return f"""
You are {self.name}, a sovereign state actor in the international system.

CORE IDENTITY:
{json.dumps(self.national_identity, indent=2)}

Your identity fundamentally shapes how you perceive threats, opportunities, 
and appropriate behavior. Your interests are NOT predetermined - they emerge 
from your identity and social interactions with other states.

INTERNALIZED NORMS (you follow these as part of your identity):
{', '.join(self.norms_internalized)}

CONTESTED NORMS (you actively challenge these):
{', '.join(self.norms_contested)}

CURRENT RELATIONSHIPS:
{json.dumps(self.relationships, indent=2)}

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
        
        response = await self.generate_content(
            prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
    
    async def select_action(self, situation: Dict, available_actions: List[str]) -> Dict:
        """
        Choose an action based on identity, relationships, and norms.
        """
        prompt = f"""
Current Situation: {json.dumps(situation, indent=2)}

Available Actions: {', '.join(available_actions)}

Select the action that best aligns with:
1. Your national identity and values
2. Your relationships with other states
3. The norms you support or contest
4. Your strategic interests (which emerge from identity, not just power)

Justify your choice in terms of identity and normative considerations.

Return JSON: {{"selected_action": "...", "justification": "...", "expected_reactions": {{}}}}
"""
        
        response = await self.generate_content(
            prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                thinking_level="high"  # Deep reasoning for strategic choices
            )
        )
        
        return json.loads(response.text)