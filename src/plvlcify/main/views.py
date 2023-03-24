from multidict import MultiDict
from lib.light_control import LightControl
from plvlcify.constants import PROJECT_DIR
import io
import pathlib
from typing import Dict
import unicodedata

import aiohttp_jinja2
import markdown2
import sys
import os
from aiohttp import web

from lib import m3u as m3u_lib
from yeelight import BulbException, LightType

import logging
logging.basicConfig(level=logging.DEBUG)


STATIC_PATH = (pathlib.Path(__file__).parent.parent / 'static')
COMMANDS = ['turn_on', 'turn_off', 'set_rgb']


@aiohttp_jinja2.template('index.html')
async def index(request: web.Request) -> Dict[str, str]:
    text = 'hello'

    return {"text": text}


async def route_m3u(request: web.Request) -> web.Response:
    m3u_list = m3u_lib.create_playList(STATIC_PATH, request)
    response = web.StreamResponse(headers={
        'Content-Type': 'audio/mpegurl'
    })
    await response.prepare(request)
    await response.write(b'#EXTM3U\n\n')
    for music in m3u_list:
        await response.write(b'#EXTINF:111,' + music.name.encode() + b'\n' + unicodedata.normalize('NFC', music.path).encode() + b'\n')
    await response.write_eof()

    return response


async def route_home(request: web.Request) -> web.Response:
    if request.match_info['key'] == os.environ.get('plvlcify_home_key'):
        kwargs = {}
        command = request.match_info['command']
        if (command.startswith('bg_')):
            command = command[3:]
            kwargs = {'light_type': LightType.Ambient}
        a = LightControl()
        call_func = getattr(a, command)
        try:
            query = MultiDict(request.rel_url.query)
            extract = query.pop('extract', None)
            result = call_func(
                *[(int(v) if v.isnumeric() else 
                   (v.split(';') if k.endswith('[]') else v)) 
                   for k, v in query.items()], **kwargs)
            if extract is not None:
                result = {'value': result.get(extract, None)}
            response = web.Response(text=str(result))
        except Exception as e:
            logging.debug(e)
            response = web.Response(status=500, reason='Something went wrong')
    else:
        response = web.Response(status=403, reason='Wrong key!')
    return response
