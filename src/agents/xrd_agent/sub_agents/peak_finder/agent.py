from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.peak_finder import prompts
from src.agents.xrd_agent.sub_agents.peak_finder.tools import find_and_fit_peaks

peak_finder_agent = Agent(
    model="gemini-2.5-flash",
    name="peak_finder_agent",
    description="This agent finds and fits peaks in the XRD data.",
    instruction=prompts.PEAK_FINDER_INSTR,
    tools=[find_and_fit_peaks],
    output_schema=schemas.PeakFinderOutput,
    output_key="peak_finder_output",
)


# ----------- Testing ------------
# from google.adk.agents import SequentialAgent
# from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent
# from src.agents.xrd_agent.sub_agents.data_preprocessor.agent import data_preprocessor_agent

# root_agent = SequentialAgent(
#     name="root_agent",
#     description="The root agent for the XRD agent.",
#     sub_agents=[data_loader_agent, data_preprocessor_agent, peak_finder_agent],
# )