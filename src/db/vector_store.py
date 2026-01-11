from langchain_postgres.v2.vectorstores import AsyncPGVectorStore
from db.engine import pg_engine
from memory.embeddings import embedding_service

TABLE_NAME = "conversation_memory"

_vectorstore = None

async def get_vectorstore() -> AsyncPGVectorStore:
    """
    Lazy-initialized vectorstore.
    Created once per process.
    """
    global _vectorstore

    if _vectorstore is None:
        _vectorstore = await AsyncPGVectorStore.create(
            engine=pg_engine,
            table_name=TABLE_NAME,
            embedding_service=embedding_service,
            metadata_columns=[
                "user_id",
                "session_id",
                "role",
                "created_at",
                "topic",
            ],
        )

    return _vectorstore
