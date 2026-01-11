from dataclasses import dataclass
from langgraph.graph.state import CompiledStateGraph
from langgraph.pregel import Pregel
from agents.lazy_agent import LazyLoadingAgent
from agents.web_search_chatbot import web_search_chatbot
from agents.chatbot_with_memory import MemoryChatAgent

from schema import AgentInfo





DEFAULT_AGENT = "web_search_chatbot"


#the central registry and access point for all agents in your system.

AgentGraph = CompiledStateGraph | Pregel  # What get_agent() returns (always loaded)
AgentGraphLike = CompiledStateGraph | Pregel | LazyLoadingAgent  # What can be stored in registry


@dataclass
class Agent:
    description: str
    graph_like: AgentGraphLike

# agent registry
agents: dict[str, Agent] = {
    "web_search_chatbot" : Agent(description="Chatbot with web search capabilities", graph_like=web_search_chatbot),
}


async def load_agent(agent_id: str) -> None:
    """Load lazy agents if needed."""
    graph_like = agents[agent_id].graph_like
    if isinstance(graph_like, LazyLoadingAgent):
        await graph_like.load()


def get_agent(agent_id: str) -> AgentGraph:
    """Get an agent graph, loading lazy agents if needed."""
    agent_graph = agents[agent_id].graph_like

    # If it's a lazy loading agent, ensure it's loaded and return its graph
    if isinstance(agent_graph, LazyLoadingAgent):
        if not agent_graph._loaded:
            raise RuntimeError(f"Agent {agent_id} not loaded. Call load() first.")
        return agent_graph.get_graph()

    # Otherwise return the graph directly
    return agent_graph


def get_all_agent_info() -> list[AgentInfo]:
    return [
        AgentInfo(key=agent_id, description=agent.description) for agent_id, agent in agents.items()
    ]


def register_memory_chat_agent(
    *,
    vectorstore,
    sql_engine,
    embedding_service,
    serper_api_key: str,
) -> None:
    """
    Register the MemoryChatAgent after dependencies are available.
    """
    agents["memory_chatbot"] = Agent(
        description="Chatbot with long-term memory and web search",
        graph_like=MemoryChatAgent(
            vectorstore=vectorstore,
            sql_engine=sql_engine,
            embedding_service=embedding_service,
            serper_api_key=serper_api_key,
        ),
    )