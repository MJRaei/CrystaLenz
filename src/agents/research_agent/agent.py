"""Defines the paper structuring agent."""

from google.adk.agents import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.agent_tool import AgentTool

from src.agents.research_agent.sub_agents.paper_miner.agent import paper_miner_agent
from src.agents.research_agent.sub_agents.retriever.agent import retriever_pipeline


research_specialist_agent = SequentialAgent(
    name="research_specialist_agent",
    description="This pipeline is the research pipeline for the research agent.",
    sub_agents=[
        paper_miner_agent,
        retriever_pipeline,
    ],
)

# root_agent = research_specialist_agent