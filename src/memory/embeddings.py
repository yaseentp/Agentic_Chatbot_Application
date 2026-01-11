from langchain_openai import OpenAIEmbeddings

embedding_service = OpenAIEmbeddings(
    model="text-embedding-3-small"  # 1536 dims
)
