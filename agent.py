from google.adk.agents import LoopAgent, ParallelAgent, SequentialAgent, LlmAgent
from google.adk.runners import Runner
from actors import usa_agent, china_agent, russia_agent, eu_agent
import asyncio

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





