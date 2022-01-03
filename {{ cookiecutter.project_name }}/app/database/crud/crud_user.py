from app.database.crud.crud_base import CRUDBase
from app.database.model.user import User


class CRUDUser(CRUDBase[User]):
    pass


crud_user = CRUDUser(User)
