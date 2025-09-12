from google.adk.agents import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools.agent_tool import AgentTool

from src.agents.xrd_agent.sub_agents.data_loader.agent import data_loader_agent
from src.agents.xrd_agent.sub_agents.data_preprocessor.agent import data_preprocessor_agent
from src.agents.xrd_agent.sub_agents.peak_finder.agent import peak_finder_agent
from src.agents.xrd_agent.sub_agents.scherrer_and_wh.agent import scherrer_and_wh_agent
from src.agents.xrd_agent.sub_agents.reference_check.agent import reference_check_agent
from src.agents.xrd_agent.sub_agents.reporter.agent import reporter_agent
from src.agents.xrd_agent.sub_agents.hyperparameter_optimizer.agent import hyperparameter_optimizer_agent

xrd_analysis_pipeline = SequentialAgent(
    name="xrd_analysis_pipeline",
    description="This agent is the root agent for the XRD analysis pipeline.",
    sub_agents=[
        data_preprocessor_agent,
        peak_finder_agent,
        scherrer_and_wh_agent,
        reference_check_agent,
        reporter_agent,
    ],
)


xrd_hyperparameter_optimizer_pipeline = LoopAgent(
    name="xrd_hyperparameter_optimizer_pipeline",
    description="This agent is the root agent for the XRD hyperparameter optimizer pipeline.",
    sub_agents=[
        hyperparameter_optimizer_agent,
        xrd_analysis_pipeline,
    ],
    max_iterations=1,
)


xrd_specialist_agent = SequentialAgent(
    name="xrd_specialist_agent",
    description="This agent is the specialist agent for the XRD analysis pipeline.",
    sub_agents=[
        data_loader_agent,
        xrd_hyperparameter_optimizer_pipeline,
    ],
)

root_agent = xrd_specialist_agent