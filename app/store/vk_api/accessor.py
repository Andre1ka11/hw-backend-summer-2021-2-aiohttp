import typing
from urllib.parse import urlencode, urljoin

from aiohttp import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"
API_HOST = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        self.session = ClientSession()
        await self._get_long_poll_service()
        self.poller = Poller(self.app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        params = {
            "group_id": self.app.config.bot.group_id,
            "access_token": self.app.config.bot.token,
        }
        
        async with self.session.get(
            self._build_query(API_HOST, "groups.getLongPollServer", params)
        ) as resp:
            data = await resp.json()
            
            if "error" in data:
                error_msg = data["error"].get("error_msg", "Unknown error")
                raise Exception(f"VK API error: {error_msg}")
            
            response = data["response"]
            self.key = response["key"]
            self.server = response["server"]
            self.ts = response["ts"]

    async def poll(self):
        if not self.server or not self.key or not self.ts:
            await self._get_long_poll_service()
        
        params = {
            "key": self.key,
            "ts": self.ts,
            "wait": 25,
        }
        
        async with self.session.get(
            self._build_query(self.server, "", params)
        ) as resp:
            data = await resp.json()
            
            if "failed" in data:
                if data["failed"] == 1:
                    self.ts = data["ts"]
                elif data["failed"] == 2:
                    await self._get_long_poll_service()
                elif data["failed"] == 3:
                    await self._get_long_poll_service()
                return []
            
            self.ts = data["ts"]
            updates = []
            
            for update_data in data.get("updates", []):
                if update_data["type"] == "message_new":
                    message_data = update_data["object"]["message"]
                    update = Update(
                        type=update_data["type"],
                        object=UpdateObject(
                            message=UpdateMessage(
                                from_id=message_data["from_id"],
                                text=message_data["text"],
                                id=message_data["id"],
                            )
                        ),
                    )
                    updates.append(update)
            
            return updates

    async def send_message(self, message: Message) -> None:
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "access_token": self.app.config.bot.token,
            "random_id": 0,
        }
        
        async with self.session.get(
            self._build_query(API_HOST, "messages.send", params)
        ) as resp:
            await resp.json()