from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.reference_check import prompts
from src.agents.xrd_agent.sub_agents.reference_check.tools.mp_identifier import mp_identifier
from src.agents.xrd_agent.sub_agents.reference_check.tools.compare_with_mp import compare_with_mp


mp_identifier_agent = Agent(
    model="gemini-2.5-flash",
    name="mp_identifier_agent",
    description="This agent identifies the materials project identifier from the XRD data based on the formula.",
    instruction=prompts.MP_IDENTIFIER_INSTR,
    tools=[mp_identifier],
    output_schema=schemas.MPIdentifierOutput,
    output_key="mp_identifier_output",
)

reference_check_agent = Agent(
    model="gemini-2.5-flash",
    name="reference_check_agent",
    description="This agent compares the XRD data with a reference database.",
    instruction=prompts.REFERENCE_CHECK_INSTR,
    tools=[
        AgentTool(agent=mp_identifier_agent),
        compare_with_mp,
        ],
    output_schema=schemas.ReferenceCheckOutput,
    output_key="reference_check_output",
)


# ----------- Testing ------------
# from google.adk.agents import SequentialAgent
# from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent
# from src.agents.xrd_agent.sub_agents.data_preprocessor.agent import data_preprocessor_agent
# from src.agents.xrd_agent.sub_agents.peak_finder.agent import peak_finder_agent
# from src.agents.xrd_agent.sub_agents.scherrer_and_wh.agent import scherrer_and_wh_agent

# root_agent = SequentialAgent(
#     name="root_agent",
#     description="The root agent for the XRD agent.",
#     sub_agents=[data_loader_agent, 
#                 data_preprocessor_agent,
#                 peak_finder_agent,
#                 scherrer_and_wh_agent, 
#                 reference_check_agent
#             ],
# )