import pyrogram.types

from app.database.crud.crud_base import CRUDBase
from app.database.model.user import User


class CRUDUser(CRUDBase[User]):
    async def create_or_update_from_pyrogram_user(self, user: pyrogram.types.User) -> User:
        return await self.create_or_update(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code
        )

    async def set_user_admin(self, user: User) -> User:
        self.logger.warning(f"User {user.id} @{user.username} promoted to be an admin")
        return await self.update(user, is_admin=True)


crud_user = CRUDUser(User)
