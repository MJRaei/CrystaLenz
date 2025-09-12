from google.adk.agents import Agent
from google.adk.agents import SequentialAgent

from src.agents.research_agent.sub_agents.retriever import prompts
from src.agents.research_agent.sub_agents.retriever.tools.retrieve_data import retrieve_data
from src.agents.research_agent.sub_agents.retriever.tools.create_vector_store import create_vector_store, check_vector_store

vs_creator_agent = Agent(
    model="gemini-2.5-flash",
    name="vs_creator_agent",
    description="An agent that is a specialist in creating vector stores.",
    instruction=prompts.VS_CREATOR_PROMPT,
    tools=[check_vector_store, create_vector_store],
)

retriever_agent = Agent(
    model="gemini-2.5-flash",
    name="retriever_agent",
    description="An agent that is a specialist in retrieving papers.",
    instruction=prompts.RETRIEVER_PROMPT,
    tools=[retrieve_data],
    output_key="retriever_results",
)

retriever_pipeline = SequentialAgent(
    name="retriever_pipeline",
    description="Pipeline: always create/verify the vector store before retrieval.",
    sub_agents=[
        vs_creator_agent,
        retriever_agent,
    ],
)


# root_agent = retriever_pipeline