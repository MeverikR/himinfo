import json

from aiohttp import web
from helpers.config import Config
from helpers.models.data import Data
from helpers.db import get_row
config = Config.get_config()


async def checkHealth(self):
    db = self.app.get('db')
    agbis = await get_row(Data.get_select(), db)
    if not agbis:
        date = 0
    else:
        date = agbis.pop()['date_pay']

    return web.json_response({'latest update date': str(date)})

