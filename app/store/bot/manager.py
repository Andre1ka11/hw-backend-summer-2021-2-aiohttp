import typing
import asyncio

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app
        self.last_message_id = None  # Запоминаем последнее обработанное сообщение

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == "message_new":
                message_id = update.object.message.id
                
                # Если это то же сообщение, что и в прошлый раз - пропускаем
                if message_id == self.last_message_id:
                    continue
                
                self.last_message_id = message_id
                user_id = update.object.message.from_id
                await self.send_greeting(user_id)

    async def send_greeting(self, user_id: int):
        message = Message(
            user_id=user_id,
            text="Привет! Я бот для викторин. Скоро здесь будут вопросы!"
        )
        await self.app.store.vk_api.send_message(message)