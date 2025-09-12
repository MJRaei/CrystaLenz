from google.adk.agents import Agent

from src.agents.research_agent.sub_agents.paper_miner import prompts
from src.agents.research_agent.sub_agents.paper_miner.tools.search_papers import search_papers
from src.agents.research_agent.sub_agents.paper_miner.tools.download_pdfs import download_pdfs
from src.agents.research_agent.sub_agents.paper_miner.tools.extract_texts_from_pdfs import extract_texts_from_pdfs

paper_miner_agent = Agent(
    model="gemini-2.5-flash",
    name="paper_miner_agent",
    description="An agent that is a specialist in paper mining.",
    instruction=prompts.PAPER_MINER_PROMPT,
    tools=[search_papers,
           download_pdfs,
           extract_texts_from_pdfs,
           ],
)

root_agent = paper_miner_agent