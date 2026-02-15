import typing
from hashlib import sha256

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        await self.create_admin(
            email=app.config.admin.email,
            password=app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin
        return None

    async def get_by_id(self, admin_id: int) -> Admin | None:
        for admin in self.app.database.admins:
            if admin.id == admin_id:
                return admin
        return None

    async def create_admin(self, email: str, password: str) -> Admin:
        existing = await self.get_by_email(email)
        if existing:
            return existing

        password_hash = sha256(password.encode()).hexdigest()
        admin = Admin(
            id=self.app.database.next_admin_id,
            email=email,
            password=password_hash
        )
        self.app.database.admins.append(admin)
        return admin