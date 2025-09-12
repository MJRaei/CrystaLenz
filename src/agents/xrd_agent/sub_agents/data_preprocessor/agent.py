from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.data_preprocessor import prompts
from src.agents.xrd_agent.sub_agents.data_preprocessor.tools import preprocess_xrd_data

data_preprocessor_agent = Agent(
    model="gemini-2.5-flash",
    name="data_preprocessor_agent",
    description="This agent preprocesses the XRD data.",
    instruction=prompts.DATA_PREPROCESSOR_INSTR,
    tools=[preprocess_xrd_data],
    output_schema=schemas.DataPreprocessorOutput,
    output_key="data_preprocessor_output",
)


# ----------- Testing ------------
# from google.adk.agents import SequentialAgent
# from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent

# root_agent = SequentialAgent(
#     name="root_agent",
#     description="The root agent for the XRD agent.",
#     sub_agents=[data_loader_agent, data_preprocessor_agent],
# )