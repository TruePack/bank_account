from aiohttp import web

from ping import views

routes = [
    web.get('/api/ping', views.ping, name='ping'),
]
