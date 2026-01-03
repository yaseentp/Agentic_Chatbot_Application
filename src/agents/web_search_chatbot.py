from datetime import date

from typing import Annotated, Sequence, TypedDict, Union
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the 
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
import json
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import GoogleSerperRun

from core import get_model, settings


# agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

tools = []

# tools
if settings.GOOGLE_API_KEY:
    api_wrapper = GoogleSerperAPIWrapper(serper_api_key=settings.GOOGLE_API_KEY.get_secret_value())

    tools.append(GoogleSerperRun(api_wrapper=api_wrapper,description="useful for when you need to ask with search",name="google_seach"))

#tools = [web_search_tool]

instructions = f"""
    Answer as many questions as you can using your existing knowledge.  
    Only search the web for queries that you can not confidently answer.
    Today's date is {date.today().strftime("%B %d %Y")}
    If you think a user's question involves something in the future that hasn't happened yet, use the search tool.
    """

def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model

async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)

    # if state["remaining_steps"] < 2 and response.tool_calls:
    #     return {
    #         "messages": [
    #             AIMessage(
    #                 id=response.id,
    #                 content="Sorry, need more steps to process this request.",
    #             )
    #         ]
    #     }
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


def should_continue(state: AgentState): 
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls: 
        return "end"
    else:
        return "continue"


graph = StateGraph(AgentState)
graph.add_node("llm_agent", acall_model)


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
web_search_chatbot = graph.compile()