import asyncio
from app.core.database import engine, Base
from app.models import user, session

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(main())
print("Tables created successfully!")
