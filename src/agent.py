from google.adk.agents import Agent
from google.adk.agents import SequentialAgent, ParallelAgent

from src import prompts

from src.agents.research_agent.agent import research_specialist_agent
from src.agents.xrd_agent.agent import xrd_specialist_agent
from src.agents.final_analyzer_agent.agent import final_analizer_agent

parallel_research_analysis_agent = ParallelAgent(
    name="parallel_research_analysis_agent",
    description="This agent is the parallel agent for the CrystaLens project, which encompasses both research and XRD analysis functionalities.",
    sub_agents=[
        research_specialist_agent,
        xrd_specialist_agent,
    ],
)

sequential_pipeline_agent = SequentialAgent(
    name="sequential_pipeline_agent",
    description="This agent is the sequential pipeline agent for the CrystaLens project, which encompasses both research and XRD analysis functionalities.",
    sub_agents=[
        parallel_research_analysis_agent,
        final_analizer_agent,
    ],
)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="crystalens_root_agent",
    description="This agent is the root agent for the CrystaLens project, which encompasses both research and XRD analysis functionalities.",
    instruction=prompts.ROOT_AGENT_INSTR,
    sub_agents=[
        sequential_pipeline_agent,
    ],
)