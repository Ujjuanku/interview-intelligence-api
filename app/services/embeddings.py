import logging
from typing import List
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Note: The AsyncOpenAI client will read OPENAI_API_KEY from environment 
# or it can be explicitly passed.
client = AsyncOpenAI(api_key=settings.openai_api_key)

async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI.
    """
    if not texts:
        return []
        
    try:
        response = await client.embeddings.create(
            model=settings.embedding_model,
            input=texts
        )
        # Ensure embeddings are returned in the same order as input texts
        embeddings = [None] * len(texts)
        for entry in response.data:
            embeddings[entry.index] = entry.embedding
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise
