import peewee
from peewee_async import (
    Manager,
    PooledPostgresqlDatabase,
)

from app.settings import settings

database = PooledPostgresqlDatabase(
    "postgres",
    host="postgres",
    port=5432,
    user="postgres",
    password=settings.POSTGRES_PASSWORD,
    autoconnect=True
)


class CustomManager(Manager):
    async def peek(self, query, n: int = 1):
        await self.connect()
        rows = (await self.execute(query))[:n]

        if rows:
            return rows[0] if n == 1 else rows

    async def first(self, source_, n: int = 1):
        if isinstance(source_, peewee.Query):
            query = source_
        else:
            query = source_.select()

        if query._limit != n:
            query._limit = n
            query._cursor_wrapper = None

        return await self.peek(query, n=n)

    async def get_or_none(self, source_, *args, **kwargs):
        try:
            return await self.get(source_, *args, **kwargs)
        except peewee.DoesNotExist:
            return None

    async def update(self, obj, only=None):
        await super(CustomManager, self).update(obj, only=only)
        return obj


objects = CustomManager(database)
