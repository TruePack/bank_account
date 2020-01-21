from aiohttp import web
from account import views

routes = [
    web.get("/api/status/{account_uuid}", views.status, name="status"),
    web.patch("/api/add/{account_uuid}", views.add, name="add"),
    web.patch("/api/substract/{account_uuid}", views.subtract,
              name="substract"),
]
