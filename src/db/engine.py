from sqlalchemy.ext.asyncio import create_async_engine
from langchain_postgres import PGEngine
from langchain_postgres import Column
from core import settings

# DATABASE_URL = (
#     "postgresql+asyncpg://langchain:langchain@localhost:6024/langchain"
# )

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD.get_secret_value()}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)


# create async SQL Alchmey engine 
engine = create_async_engine(
    DATABASE_URL,
    echo=True,     
    pool_size=5,
    max_overflow=10,
)

# Wrap the engine with Langraph pgEngine, use for query, updation 
pg_engine = PGEngine.from_engine(engine=engine)


sql_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)
