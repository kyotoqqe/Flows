from sqladmin import ModelView

from src.auth.domain.entities import User

class UserAdmin(ModelView, model=User):
    can_create = False
    can_delete = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"
    column_list = ["id", "email", "active"]

    