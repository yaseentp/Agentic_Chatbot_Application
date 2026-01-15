import asyncio
from sqlalchemy import text

from langchain_postgres.v2.indexes import IVFFlatIndex
from langchain_postgres.v2.vectorstores import AsyncPGVectorStore

from db.engine import create_pg_engine, create_sql_engine

TABLE_NAME = "conversation_memory"
INDEX_NAME = "conversation_memorylangchainvectorindex"

async def create_indexes():
    sql_engine = create_sql_engine()

    # 1. Check if LangChain vector index already exists
    async with sql_engine.connect() as conn:
        exists = await conn.scalar(
            text("""
                SELECT 1
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = :index
                  AND n.nspname = 'public'
            """),
            {"index": INDEX_NAME},
        )

    if exists:
        print("ℹ️ LangChain vector index already exists, skipping creation")
        return

    # 2. Create index ONCE
    vectorstore = await AsyncPGVectorStore.create(
        engine=create_pg_engine(),
        table_name=TABLE_NAME,
        embedding_service=None,
    )

    await vectorstore.aapply_vector_index(
        IVFFlatIndex(lists=100)
    )

    async with sql_engine.begin() as conn:
        await conn.execute(text("ANALYZE conversation_memory"))


    print("✅ Vector index created")

if __name__ == "__main__":
    asyncio.run(create_indexes())
