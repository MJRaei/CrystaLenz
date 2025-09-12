from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.scherrer_and_wh import prompts
from src.agents.xrd_agent.sub_agents.scherrer_and_wh.tools import scherrer_and_wh

scherrer_and_wh_agent = Agent(
    model="gemini-2.5-flash",
    name="scherrer_and_wh_agent",
    description="This agent calculates the Scherrer and Williamson-Hall parameters.",
    instruction=prompts.SCHERRER_AND_WH_INSTR,
    tools=[scherrer_and_wh],
    output_schema=schemas.ScherrerAndWHOutput,
    output_key="scherrer_and_wh_output",
)


# ----------- Testing ------------
# from google.adk.agents import SequentialAgent
# from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent
# from src.agents.xrd_agent.sub_agents.data_preprocessor.agent import data_preprocessor_agent
# from src.agents.xrd_agent.sub_agents.peak_finder.agent import peak_finder_agent

# root_agent = SequentialAgent(
#     name="root_agent",
#     description="The root agent for the XRD agent.",
#     sub_agents=[data_loader_agent, data_preprocessor_agent, peak_finder_agent, scherrer_and_wh_agent],
# )