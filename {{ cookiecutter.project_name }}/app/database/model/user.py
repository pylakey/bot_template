import peewee

from .base_model import BaseModel


class User(BaseModel):
    id = peewee.BigIntegerField(primary_key=True)
    first_name = peewee.CharField(max_length=64)
    last_name = peewee.CharField(null=True, max_length=64)
    username = peewee.CharField(null=True, max_length=32, index=True)
    is_admin = peewee.BooleanField(default=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or '-'

    @property
    def link(self) -> str:
        return f"<a href='tg://user?id={self.id}'>{self.full_name}</a>"
