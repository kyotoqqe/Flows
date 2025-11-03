from sqladmin import Admin
from starlette.middleware import Middleware


from src.main import app
from src.core.database.connection import engine

from src.admin.auth import authentication_backend
from src.admin.middlewares import RefreshTokenMiddleware
from src.auth.config import cookie_settings



class MyAdmin(Admin):
    async def login(self, request):
        response =  await super().login(request)
        if hasattr(request.state, "refresh_token"):
            response.set_cookie(
                key=cookie_settings.cookie_key,
                value=request.state.refresh_token,
                max_age=cookie_settings.max_age,
                path="/",
                domain=cookie_settings.cookie_domain,
                secure=cookie_settings.cookie_secure,
                samesite=cookie_settings.cookie_samesite,
                httponly=False
            )
        return response

admin = MyAdmin(app, engine, authentication_backend=authentication_backend)