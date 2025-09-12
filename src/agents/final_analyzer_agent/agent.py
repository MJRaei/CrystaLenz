from google.adk.agents import Agent

from src.agents.final_analyzer_agent import prompts
from src.agents.final_analyzer_agent.tools import get_analysis_results

final_analizer_agent = Agent(
    model="gemini-2.5-flash",
    name="final_analizer_agent",
    description="This agent is the final analizer agent for the CrystaLens project, which encompasses both research and XRD analysis functionalities.",
    instruction=prompts.FINAL_ANALYZER_INSTR,
    tools=[get_analysis_results],
)