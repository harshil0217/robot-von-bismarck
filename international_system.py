from google.adk.agents import SequentialAgent, ParallelAgent
from state_actor import StateActorAgent
from typing import List, Dict
import json
import asyncio

class InternationalSystem:
    """
    Orchestrates the entire IR simulation.
    Manages state actors, norms, events, and turn-based simulation.
    """
    
    def __init__(self, state_actors: List[StateActorAgent]):
        self.state_actors = {agent.name: agent for agent in state_actors}
        self.international_norms = NormRegistry()
        self.world_state = WorldState()
        self.event_history = []
        self.turn_number = 0
        
    async def run_simulation_turn(self):
        """
        Execute one turn of the simulation.
        Implements turn-based synchronization for deterministic results.
        """
        self.turn_number += 1
        print(f"\n{'='*60}")
        print(f"TURN {self.turn_number}")
        print(f"{'='*60}\n")
        
        # Phase 1: All agents perceive current world state (parallel)
        print("Phase 1: Perception")
        perception_tasks = [
            agent.perceive_event(self.world_state.to_dict())
            for agent in self.state_actors.values()
        ]
        perceptions = await asyncio.gather(*perception_tasks)
        
        # Phase 2: Diplomatic communication round
        print("Phase 2: Diplomatic Communication")
        await self._diplomatic_round()
        
        # Phase 3: Action selection (parallel)
        print("Phase 3: Action Selection")
        action_tasks = [
            agent.select_action(
                self.world_state.to_dict(),
                available_actions=["cooperate", "defect", "signal", "sanction", 
                                    "negotiate", "build_coalition", "contest_norm"]
            )
            for agent in self.state_actors.values()
        ]
        actions = await asyncio.gather(*action_tasks)
        
        # Phase 4: Resolve actions and update world state
        print("Phase 4: Resolution")
        outcomes = self.world_state.resolve_actions(
            list(zip(self.state_actors.keys(), actions))
        )
        
        # Phase 5: Update relationships and norms
        print("Phase 5: Social Learning")
        await self._update_relationships(outcomes)
        self.international_norms.update(outcomes)
        
        # Phase 6: Memory consolidation
        print("Phase 6: Memory Update")
        for agent_name, agent in self.state_actors.items():
            await agent.update_memory({
                "turn": self.turn_number,
                "outcomes": outcomes,
                "own_action": next(a for n, a in zip(self.state_actors.keys(), actions) if n == agent_name)
            })
        
        return outcomes
    
    async def _diplomatic_round(self, num_rounds: int = 2):
        """
        Agents exchange messages in structured negotiation rounds.
        """
        for round_num in range(num_rounds):
            print(f"  Diplomatic Round {round_num + 1}")
            
            # Each agent generates messages to others
            messages = {}
            for agent_name, agent in self.state_actors.items():
                prompt = f"""
Given current relationships and situation, draft diplomatic messages to other states.
You may send messages to any subset of: {list(self.state_actors.keys())}

Format as JSON: {{"recipient": "message content", ...}}
Keep messages concise but strategically meaningful.
"""
                response = await agent.generate_content(
                    prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                messages[agent_name] = json.loads(response.text)
            
            # Distribute messages and let agents process them
            for recipient_name, recipient_agent in self.state_actors.items():
                incoming = {
                    sender: msg.get(recipient_name, "")
                    for sender, msg in messages.items()
                    if recipient_name in msg
                }
                
                if incoming:
                    # Agent processes incoming diplomatic signals
                    prompt = f"""
You received these diplomatic messages:
{json.dumps(incoming, indent=2)}

How do you interpret these signals? Update your perceptions of sender intentions.
Return JSON with your interpretations.
"""
                    interpretation = await recipient_agent.generate_content(
                        prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
    
    async def _update_relationships(self, outcomes: Dict):
        """
        Update bilateral relationships based on actions taken.
        Constructivist principle: Relationships are socially constructed.
        """
        for agent_name, agent in self.state_actors.items():
            prompt = f"""
Based on these outcomes: {json.dumps(outcomes, indent=2)}

Update your trust/rivalry levels with other states.
Consider: Did they cooperate or defect? Support or oppose you?
Did their actions align with norms you support?

Return JSON: {{"state_name": new_relationship_value, ...}}
Values between -1.0 (strong rivalry) and +1.0 (strong alliance).
"""
            response = await agent.generate_content(
                prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            updates = json.loads(response.text)
            for other_state, new_value in updates.items():
                if other_state in agent.relationships:
                    # Smooth update (moving average)
                    agent.relationships[other_state] = (
                        0.7 * agent.relationships[other_state] + 0.3 * new_value
                    )


class NormRegistry:
    """
    Tracks evolution of international norms.
    Constructivist principle: Norms emerge and change through practice.
    """
    
    def __init__(self):
        self.norms = {
            "sovereignty": {"strength": 0.9, "adopters": set(), "contesters": set()},
            "human_rights": {"strength": 0.6, "adopters": set(), "contesters": set()},
            "free_trade": {"strength": 0.7, "adopters": set(), "contesters": set()},
            "non_intervention": {"strength": 0.5, "adopters": set(), "contesters": set()},
        }
    
    def update(self, outcomes: Dict):
        """
        Update norm strength based on state behavior.
        """
        for actor, action_data in outcomes.items():
            if "norm_behavior" in action_data:
                for norm_id, behavior in action_data["norm_behavior"].items():
                    if norm_id in self.norms:
                        if behavior == "comply":
                            self.norms[norm_id]["adopters"].add(actor)
                            self.norms[norm_id]["strength"] += 0.01
                        elif behavior == "violate":
                            self.norms[norm_id]["contesters"].add(actor)
                            self.norms[norm_id]["strength"] -= 0.02
    
    def get_status(self) -> Dict:
        return {
            norm_id: {
                "strength": data["strength"],
                "adoption_rate": len(data["adopters"]) / max(len(data["adopters"]) + len(data["contesters"]), 1)
            }
            for norm_id, data in self.norms.items()
        }


class WorldState:
    """
    Maintains the current state of the international system.
    """
    
    def __init__(self):
        self.crises = []
        self.ongoing_negotiations = []
        self.recent_events = []
        self.resource_disputes = []
    
    def to_dict(self) -> Dict:
        return {
            "crises": self.crises,
            "negotiations": self.ongoing_negotiations,
            "recent_events": self.recent_events[-5:],  # Last 5 events
            "disputes": self.resource_disputes
        }
    
    def resolve_actions(self, actions: List[tuple]) -> Dict:
        """
        Determine outcomes based on all states' simultaneous actions.
        """
        outcomes = {}
        
        # Example resolution logic
        for state_name, action_data in actions:
            outcome = {
                "action_taken": action_data["selected_action"],
                "success": True,  # Simplified
                "consequences": []
            }
            
            # Track norm compliance
            if action_data["selected_action"] in ["sanction", "intervene"]:
                outcome["norm_behavior"] = {
                    "sovereignty": "violate",
                    "non_intervention": "violate"
                }
            elif action_data["selected_action"] == "cooperate":
                outcome["norm_behavior"] = {
                    "free_trade": "comply",
                    "multilateralism": "comply"
                }
            
            outcomes[state_name] = outcome
        
        return outcomes