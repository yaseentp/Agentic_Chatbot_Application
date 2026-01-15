from sqlalchemy import text
from langchain_postgres import Column
import asyncio

from db.engine import create_pg_engine, create_sql_engine

TABLE_NAME = "conversation_memory"
VECTOR_SIZE = 1536

async def setup_database():
    sql_engine = create_sql_engine()

    # 1. Enable extensions (safe)
    async with sql_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    # 2. Check if table exists (CRITICAL)
    async with sql_engine.connect() as conn:
        exists = await conn.scalar(
            text("SELECT to_regclass(:table_name)"),
            {"table_name": f"public.{TABLE_NAME}"},
        )

    if exists:
        print("ℹ️ Vectorstore table already exists, skipping creation")
        return

    # 3. Create table ONCE
    pg_engine = create_pg_engine()
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
