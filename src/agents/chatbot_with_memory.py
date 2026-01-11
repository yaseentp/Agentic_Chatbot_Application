from datetime import date, datetime
from typing import Sequence, Optional, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from datetime import date, datetime

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from memory.planner import MemoryPlanner, to_pgvector
from memory.query_analyzer import analyze_query
from agents.lazy_agent import LazyLoadingAgent


def add(a: float, b:float):
    """This is an addition function that adds 2 numbers together"""
    return a + b 

def subtract(a: float, b: float):
    """Subtraction function"""
    return a - b

def multiply(a: float, b: float):
    """Multiplication function"""
    return a * b

def divide(a: float, b: float):
    """division function that performs division"""
    return a / b

class AgentState(dict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    memory_context: Optional[str]


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    return "continue"

def should_store_memory(last_user_msg, response):
    return True

def extract_topic(message):
    return ""

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import GoogleSerperRun

class MemoryChatAgent(LazyLoadingAgent):
    def __init__(self, *, vectorstore, sql_engine, embedding_service,serper_api_key):
        super().__init__()
        self._vectorstore = vectorstore
        self._sql_engine = sql_engine
        self._embedding_service = embedding_service
        self._serper_api_key = serper_api_key
        
    async def _retrieve_long_term_memory(
        self,
        *,
        user_id: str,
        session_id: str,
        query: str,
    ) -> str:
        """
        Retrieves relevant long-term memory from PostgreSQL + pgvector.
        """

        # 1. Analyze query
        intent = analyze_query(query)

        # 2. Build SQL
        planner = MemoryPlanner(
            user_id=user_id,
            session_id=session_id,
        )

        pg_embedding = None
        if intent["query_type"] in ("semantic", "hybrid"):
            embedding = self._embedding_service.embed_query(query)
            pg_embedding = to_pgvector(embedding)

        sql, params = planner.build(intent, pg_embedding)

        # 3. Execute SQL
        async with self._sql_engine.begin() as conn:
            result = await conn.execute(sql, params)
            rows = result.fetchall()

        # 4. Format memory
        return "\n".join(r.content for r in rows)


    async def load(self) -> None:
        """
        Build and compile the graph lazily.
        This runs exactly once.
        """

        api_wrapper = GoogleSerperAPIWrapper(
        k=1,
        serper_api_key=self._serper_api_key,
    )
        web_search_tool = GoogleSerperRun(
        api_wrapper=api_wrapper,
        description="useful for when you need to ask with search",
        name="google_search",
        )
        tools = [
            add,
            subtract,
            multiply,
            divide,
            web_search_tool,
        ]

        model = ChatOpenAI(model="gpt-4o",streaming=True)
        model_with_tools = model.bind_tools(tools)


        async def llm_chat(state: AgentState, config: RunnableConfig) -> AgentState:
            user_id = config["configurable"]["user_id"]
            session_id = config["configurable"]["thread_id"]

            last_user_msg = state["messages"][-1].content

    

            memory_context = await self._retrieve_long_term_memory(
            user_id=user_id,
            session_id=session_id,
            query=last_user_msg,
            )


            memory_block = ""
            if memory_context:
                memory_block = f"""
                                Relevant past information:
                                {memory_context}
                                """

                system_prompt = SystemMessage(
                                                content=f"""
                                You are a helpful assistant.
                                {memory_block}

                                Today's date is {date.today().strftime("%B %d %Y")}
                                """
                                            )

            messages_to_send = [system_prompt] + state["messages"]

            response = model_with_tools.invoke(messages_to_send)

            # 🔹 store new memory (unchanged logic)
            if should_store_memory(last_user_msg, response.content):
                await self._vectorstore.aadd_texts(
                    texts=[last_user_msg],
                    metadatas=[{
                        "user_id": user_id,
                        "session_id": session_id,
                        "role": "user",
                        "created_at": datetime.utcnow(),
                        "topic": extract_topic(last_user_msg),
                    }]
                )

            return {
                **state,
                "messages": [response],
                "memory_context": memory_context,
            }
        graph = StateGraph(AgentState)
        graph.add_node("llm_agent", llm_chat)

        tool_node = ToolNode(tools=tools)
        graph.add_node("tools", tool_node)

        graph.set_entry_point("llm_agent")

        graph.add_conditional_edges(
            "llm_agent",
            should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )

        graph.add_edge("tools", "llm_agent")

        # 🔒 Compile ONLY here
        self._graph = graph.compile()
        self._loaded = True
