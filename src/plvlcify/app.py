from pathlib import Path
from typing import (
    Optional,
    List,
    AsyncGenerator,
)

import aiohttp_jinja2
from aiohttp import web
import jinja2

from plvlcify.routes import init_routes
from plvlcify.utils.common import init_config


path = Path(__file__).parent


def init_jinja2(app: web.Application) -> None:
    '''
    Initialize jinja2 template for application.
    '''
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(path / 'templates'))
    )

@web.middleware
async def error_middleware(request: web.Request, handler):
    try:
        response = await handler(request)

        return response
    except web.HTTPException as ex:
        raise
    # this is needed to handle non-HTTPException
    except Exception as e:
        request.app.logger.debug(e)
        return web.Response(text='Oops, something went wrong', status=500)

def init_app(config: Optional[List[str]] = None) -> web.Application:
    app = web.Application(middlewares=[error_middleware])

    init_jinja2(app)
    init_config(app, config=config)
    init_routes(app)

    return app
