from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from src.schemas import schemas
from src.agents.xrd_agent.sub_agents.hyperparameter_optimizer import prompts
from src.agents.xrd_agent.sub_agents.hyperparameter_optimizer.tools import get_analysis_results

hyperparameter_optimizer_agent = Agent(
    model="gemini-2.5-flash",
    name="hyperparameter_optimizer_agent",
    description="This agent optimizes the hyperparameters for the XRD analysis pipeline.",
    instruction=prompts.HYPERPARAMETER_OPTIMIZER_INSTR,
    tools=[get_analysis_results],
    output_schema=schemas.HyperparameterOptimizerOutput,
    output_key="hyperparameter_optimizer_output",
)