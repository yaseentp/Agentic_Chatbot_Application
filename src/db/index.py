import asyncio
from langchain_postgres.v2.indexes import IVFFlatIndex
from langchain_postgres.v2.vectorstores import AsyncPGVectorStore

#from db.engine import pg_engine
from db.engine import create_pg_engine
async def create_indexes():
    vectorstore = await AsyncPGVectorStore.create(
        engine=create_pg_engine(),
        table_name="conversation_memory",
        embedding_service=None,  # not needed for index creation
    )

    await vectorstore.aapply_vector_index(IVFFlatIndex())
    print("✅ Vector index created")

if __name__ == "__main__":
    asyncio.run(create_indexes())
