from typing import Optional
from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_apispec import setup_aiohttp_apispec
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
import base64
from cryptography import fernet

from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Optional[Config] = None
    store: Optional[Store] = None
    database: Database = Database()


class Request(AiohttpRequest):
    admin: Optional[Admin] = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})


app = Application()


async def on_startup(app: Application):
    await app.store.admins.connect(app)
    await app.store.vk_api.connect(app)


async def on_shutdown(app: Application):
    await app.store.vk_api.disconnect(app)
    app.database.clear()


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    
    # Настройка сессий
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    setup_session(app, EncryptedCookieStorage(secret_key))
    
    setup_routes(app)
    setup_middlewares(app)
    setup_aiohttp_apispec(app, title="Quiz Bot API", url="/docs/json")
    setup_store(app)
    
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    return app