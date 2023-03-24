import pathlib

from aiohttp import web

import plvlcify.main.views as v

PROJECT_PATH = pathlib.Path(__file__).parent


def init_routes(app: web.Application) -> None:
    add_route = app.router.add_route

    add_route('*', '/', v.index, name='index')
    prefix = 'route_'
    for rt in dir(v):
        if str(rt).startswith(prefix):
            add_route('*', '/' + rt[len(prefix):] + '/{key:.*}/{command:.*}', getattr(v, rt), name=rt)

    # added static dir
    app.router.add_static(
        '/static/',
        path=(PROJECT_PATH / 'static'),
        name='static',
    )
