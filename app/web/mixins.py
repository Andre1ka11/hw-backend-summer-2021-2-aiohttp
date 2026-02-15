from aiohttp.web import HTTPUnauthorized, HTTPForbidden


class AuthRequiredMixin:
    @property
    def request(self):
        return super().request

    async def _iter(self):
        if not getattr(self.request, "admin", None):
            raise HTTPUnauthorized()
        return await super()._iter()