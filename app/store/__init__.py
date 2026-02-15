from .store import *
import typing

from app.store.admin.accessor import AdminAccessor
from app.store.quiz.accessor import QuizAccessor
from app.store.vk_api.accessor import VkApiAccessor
from app.store.bot.manager import BotManager

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app
        self.admins = AdminAccessor(app)
        self.quiz = QuizAccessor(app)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.store = Store(app)