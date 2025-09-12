from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.reporter import prompts
from src.agents.xrd_agent.sub_agents.reporter.tools.analyzer import get_results, save_analysis, save_results
from src.agents.xrd_agent.sub_agents.reporter.tools.plotter import plot_results

analyzer_agent = Agent(
    model="gemini-2.5-flash",
    name="analyzer_agent",
    description="This agent analyzes the XRD data.",
    instruction=prompts.ANALYZER_INSTR,
    tools=[get_results, save_analysis],
    output_schema=schemas.AnalyzerOutput,
    output_key="analyzer_output",
)

reporter_agent = Agent(
    model="gemini-2.5-flash",
    name="reporter_agent",
    description="This agent reports the XRD data.",
    instruction=prompts.REPORTER_INSTR,
    tools=[
        AgentTool(agent=analyzer_agent),
        save_results,
        plot_results,
        ],
    output_schema=schemas.ReporterOutput,
    output_key="reporter_output",
)

# ------------- Testing -------------
# from google.adk.agents import SequentialAgent
# from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent
# from src.agents.xrd_agent.sub_agents.data_preprocessor.agent import data_preprocessor_agent
# from src.agents.xrd_agent.sub_agents.peak_finder.agent import peak_finder_agent
# from src.agents.xrd_agent.sub_agents.scherrer_and_wh.agent import scherrer_and_wh_agent
# from src.agents.xrd_agent.sub_agents.reference_check.agent import reference_check_agent

# root_agent = SequentialAgent(
#     name="root_agent",
#     description="This agent is the root agent for the XRD pipeline.",
#     sub_agents=[
#         data_loader_agent,
#         data_preprocessor_agent,
#         peak_finder_agent, 
#         scherrer_and_wh_agent, 
#         reference_check_agent, 
#         reporter_agent
#     ],
# )