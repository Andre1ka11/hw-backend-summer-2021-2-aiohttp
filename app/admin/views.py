from hashlib import sha256

from aiohttp.web import HTTPForbidden, HTTPBadRequest
from aiohttp_apispec import request_schema, response_schema
from aiohttp_session import get_session

from app.admin.schemes import AdminLoginSchema, AdminSchema
from app.web.app import View
from app.web.utils import json_response, error_json_response


class AdminLoginView(View):
    @request_schema(AdminLoginSchema)
    @response_schema(AdminSchema, 200)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]
        
        admin = await self.store.admins.get_by_email(email)
        
        if not admin:
            return error_json_response(
                http_status=403,
                status="forbidden",
                message="Forbidden",
                data={},
            )
        
        password_hash = sha256(password.encode()).hexdigest()
        if admin.password != password_hash:
            return error_json_response(
                http_status=403,
                status="forbidden",
                message="Forbidden",
                data={},
            )

        session = await get_session(self.request)
        session["admin_id"] = admin.id
        
        return json_response(data=AdminSchema().dump(admin))


class AdminCurrentView(View):
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))