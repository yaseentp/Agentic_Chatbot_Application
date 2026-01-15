from sqlalchemy.ext.asyncio import create_async_engine
from langchain_postgres import PGEngine
from langchain_postgres import Column
from core import settings

# DATABASE_URL = (
#     "postgresql+asyncpg://langchain:langchain@localhost:6024/langchain"
# )



def get_postgres_connection_string() -> str:
    """Build and return the PostgreSQL connection string from settings."""
    if settings.POSTGRES_PASSWORD is None:
        raise ValueError("POSTGRES_PASSWORD is not set")
    DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD.get_secret_value()}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

    return DATABASE_URL


# # create async SQL Alchmey engine 
# engine = create_async_engine(
#     DATABASE_URL=get_postgres_connection_string(),
#     echo=True,     
#     pool_size=5,
#     max_overflow=10,
# )

# # Wrap the engine with Langraph pgEngine, use for query, updation 
# pg_engine = PGEngine.from_engine(engine=engine)


# sql_engine = create_async_engine(
#     DATABASE_URL=get_postgres_connection_string(),
#     echo=False,
#     pool_size=5,
#     max_overflow=10,
# )




def create_pg_engine(
    echo: bool = True,
):
    engine = create_async_engine(
        get_postgres_connection_string(),
        echo=echo,
        pool_size=5,
        max_overflow=10,
    )

    # Wrap with LangGraph PGEngine
    return PGEngine.from_engine(engine=engine)


def create_sql_engine(
    echo: bool = False,
):
    return create_async_engine(
        get_postgres_connection_string(),
        echo=echo,
        pool_size=5,
        max_overflow=10,
    )