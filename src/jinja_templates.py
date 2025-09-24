__all__ = ("templates", )

from fastapi.templating import Jinja2Templates

from src.config import core_settings

templates = Jinja2Templates(
    directory=core_settings.base_dir / "templates"
)