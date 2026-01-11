from datetime import datetime, timedelta
from typing import Any, Dict, Tuple, Optional
from sqlalchemy import text

def normalize_time_reference(time_ref: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize time_reference into concrete datetime values.
    """
    if not time_ref or time_ref.get("type") in (None, "null"):
        return None

    ttype = time_ref["type"]
    value = time_ref.get("value")

    now = datetime.utcnow()

    if ttype == "relative":
        if value == "last week":
            return {"type": "after", "start": now - timedelta(days=7)}
        if value == "last day":
            return {"type": "after", "start": now - timedelta(days=1)}

    if ttype == "range":
        start, end = value
        return {
            "type": "range",
            "start": datetime.fromisoformat(start),
            "end": datetime.fromisoformat(end),
        }

    if ttype == "newest":
        return {"type": "order", "direction": "DESC"}

    if ttype == "oldest":
        return {"type": "order", "direction": "ASC"}

    return None

class MemoryPlanner:
    def __init__(self, user_id: str, session_id: Optional[str] = None):
        self.user_id = user_id
        self.session_id = session_id

    def build(
        self,
        intent: Dict[str, Any],
        pg_embedding: Optional[str] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Returns:
            (sqlalchemy.text, params dict)
        """

        query_type = intent["query_type"]
        session_scope = intent.get("session_scope", "user_all")
        topic = intent.get("topic")
        seq_ref = intent.get("sequence_reference", {}).get("value")
        time_ref = normalize_time_reference(intent.get("time_reference"))

        sql_parts = [
            "SELECT content, role, created_at",
            "FROM conversation_memory",
            "WHERE user_id = :user_id",
        ]

        params: Dict[str, Any] = {
            "user_id": self.user_id
        }

        # --- session scope ---
        if session_scope == "current_session":
            sql_parts.append("AND session_id = :session_id")
            params["session_id"] = self.session_id

        # # --- topic filter ---
        # if topic:
        #     sql_parts.append("AND topic = :topic")
        #     params["topic"] = topic


        if query_type == "sequence_based":
            sql_parts.append("AND role = 'user'")

            order = "DESC"
            if time_ref and time_ref.get("direction"):
                order = time_ref["direction"]

            sql_parts.append(f"ORDER BY created_at {order}")
            sql_parts.append("LIMIT :k")

            params["k"] = seq_ref or 1

            return text("\n".join(sql_parts)), params

       
        if query_type == "time_based":
            if time_ref and time_ref["type"] == "range":
                sql_parts.append("AND created_at BETWEEN :start AND :end")
                params["start"] = time_ref["start"]
                params["end"] = time_ref["end"]

            sql_parts.append("ORDER BY created_at ASC")
            return text("\n".join(sql_parts)), params

        if query_type in ("semantic", "hybrid"):
            if time_ref:
                if time_ref["type"] == "after":
                    sql_parts.append("AND created_at >= :start_time")
                    params["start_time"] = time_ref["start"]

            sql_parts.append(
                "ORDER BY embedding <=> CAST(:embedding AS vector)"
            )
            sql_parts.append("LIMIT :k")

            params["embedding"] = pg_embedding
            params["k"] = 10 if intent.get("needs_long_context") else 5

            return text("\n".join(sql_parts)), params

        raise ValueError(f"Unsupported query_type: {query_type}")

def to_pgvector(vec: list[float]) -> str:
    return "[" + ",".join(map(str, vec)) + "]"


