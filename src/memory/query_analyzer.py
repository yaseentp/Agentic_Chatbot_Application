from typing import Optional, List, Union, Literal
from datetime import date
from dotenv import load_dotenv 

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()

class TimeReference(BaseModel):
    type: Literal["absolute", "relative", "range", "oldest", "newest", "null"]
    value: Optional[Union[str, List[str]]] = Field(
        None, description="Date or list of dates"
    )

class SequenceReference(BaseModel):
    value: Optional[int] = None

class QueryUnderstanding(BaseModel):
    query_type: Literal["semantic", "time_based", "sequence_based", "metadata_based", "hybrid"]
    topic: Optional[str] = None
    time_reference: TimeReference
    sequence_reference: SequenceReference
    session_scope: Literal["current_session", "all_sessions", "user_all", "null"]
    needs_long_context: bool
    output_hint: Literal["summary", "full", "snippets", "reference"]
    confidence: float


SYSTEM_PROMPT = """You are an expert Memory Query Interpreter.

Your job is:
- to analyze a user’s question about past chats,
- determine what type of memory lookup is needed,
- and produce a *structured JSON* that strictly matches the given schema.

The JSON you output will be used to query a vector store, so accuracy and consistency are important.

Today's date is '{date}'

Follow these rules:
1. For sequence based query_type, time_reference type should be 'oldest' or 'newest'. 'newest' when user query about recent ones.
2. For sequence based query_type, sequence_reference operator should be "null".
3. Whenever the query contains a relative time expression (e.g., “last week”, “last month”, “yesterday”, “two days ago”, “last quarter”, “recently”), you MUST convert it into an absolute date or date range using the current date.
4. Always fill all fields.
5. If a field does not apply, set it to null.
6. Never include extra fields beyond the schema.
7. "needs_long_context" is True when the query references:
   - topics across sessions
   - long-range dates
   - semantic searches
   - or unclear / fuzzy memory requests.

Definitions:
- "topic": Key subject of the query (e.g., Kubernetes, travel, wine). If none, use null.
- "query_type":
    * semantic → meaning-based search
    * time_based → specific date, range, last week, etc.
    * sequence_based → “first message”, “second question”
    * metadata_based → search by attributes (sentiment, user/AI role, etc.)
    * hybrid → combination of time + topic, or sequence + topic
- session_scope:
    * current_session → only today’s chat
    * all_sessions → AI messages + user messages across all sessions
    * user_all → only user messages across all sessions
    * null → if the scope cannot be inferred
- output_hint:
    * full → want entire messages
    * snippets → excerpts
    * summary → summarized
    * reference → short pointers or IDs

Output ONLY the JSON object. No explanation.
"""


USER_PROMPT = """
Convert the following user question into the structured JSON format:

"{query}"

Return ONLY valid JSON according to the schema.

"""

model = ChatOpenAI(model = "gpt-4o")
model_with_structured_output = model.with_structured_output(QueryUnderstanding)

prompt_template = ChatPromptTemplate.from_messages([
    ('system',SYSTEM_PROMPT),
    ('user',USER_PROMPT),
])

def analyze_query(query):
    messages = prompt_template.invoke({'date':date.today(),'query':query})
    response = model_with_structured_output.invoke(messages,config={"callbacks": []})
    return response.model_dump()

