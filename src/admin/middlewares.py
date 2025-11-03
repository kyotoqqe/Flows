from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.config import cookie_settings

class RefreshTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if hasattr(request.state, "refresh_token"):
            print("Has")
            print(request.state.refresh_token)
            response.set_cookie(
                key=cookie_settings.cookie_key,
                value=request.state.refresh_token,
                max_age=cookie_settings.max_age,
                path=cookie_settings.cookie_path,
                domain=cookie_settings.cookie_domain,
                secure=cookie_settings.cookie_secure,
                samesite=cookie_settings.cookie_samesite,
                httponly=False
            )
       
        return response