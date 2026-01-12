from sqlalchemy import text
from langchain_postgres import Column
import asyncio

from db.engine import sql_engine, pg_engine

TABLE_NAME = "conversation_memory"
VECTOR_SIZE = 1536

async def setup_database():
    # 1. Enable extensions
    async with sql_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    # 2. Create vectorstore table
    await pg_engine.ainit_vectorstore_table(
        table_name=TABLE_NAME,
        vector_size=VECTOR_SIZE,
        metadata_columns=[
            Column("user_id", "TEXT"),
            Column("session_id", "TEXT"),
            Column("role", "TEXT"),
            Column("created_at", "TIMESTAMPTZ"),
            Column("topic", "TEXT"),
        ],
    )

    print("✅ Database setup complete")

if __name__ == "__main__":
    asyncio.run(setup_database())