import json
import typing

from aiohttp.web_exceptions import (
    HTTPUnprocessableEntity,
    HTTPUnauthorized,
    HTTPForbidden,
)
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
        return response
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPUnauthorized as e:
        return error_json_response(
            http_status=401,
            status=HTTP_ERROR_CODES[401],
            message=str(e),
        )
    except HTTPForbidden as e:
        return error_json_response(
            http_status=403,
            status=HTTP_ERROR_CODES[403],
            message=str(e),
        )


@middleware
async def auth_middleware(request: "Request", handler):
    if request.path == "/admin.login" and request.method == "POST":
        return await handler(request)
    
    session = request.get("session", {})
    admin_id = session.get("admin_id")
    
    if not admin_id:
        raise HTTPUnauthorized()
    
    admin = await request.app.store.admins.get_by_id(admin_id)
    
    if not admin:
        raise HTTPForbidden()
    
    request.admin = admin
    
    return await handler(request)


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)