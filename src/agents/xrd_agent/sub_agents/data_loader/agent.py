from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.data_loader import prompts
from src.agents.xrd_agent.sub_agents.data_loader.tools import inspect_xrd_file, load_xrd_data

data_ingester_agent = Agent(
    model="gemini-2.5-flash",
    name="data_ingester_agent",
    description="This agent reads the 2θ and intensity columns and decides on the unit of the 2θ column",
    instruction=prompts.DATA_INGESTION_INSTR,
    tools=[inspect_xrd_file],
    output_schema=schemas.DataInjesterOutput,
    output_key="data_ingestion_output",
)

data_loader_agent = Agent(
    model="gemini-2.5-flash",
    name="data_loader_agent",
    description="This agent loads the data from the file and returns the data in the form of a dictionary",
    instruction=prompts.DATA_LOADER_INSTR,
    tools=[
        AgentTool(agent=data_ingester_agent),
        load_xrd_data,
        ],
    output_schema=schemas.DataLoaderOutput,
    output_key="data_loader_output",
)

# root_agent = data_loader_agent