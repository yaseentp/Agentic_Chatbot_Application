import logging

from db.setup import setup_database
from db.index import create_indexes

logger = logging.getLogger(__name__)

async def bootstrap_database():
    """
    One-time database bootstrap:
    - extensions
    - tables
    - indexes
    """
    logger.info("Starting database bootstrap...")

    await setup_database()
    await create_indexes()

    logger.info("Database bootstrap completed")
