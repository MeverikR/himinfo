from logging import config as logger_config
from aiohttp import web
from helpers.config import Config
from handlers.check_health import checkHealth
from handlers.main import Main
from helpers.db import init, close



config = Config.get_config()

logger_config.dictConfig(config.get('logging'))

if __name__ == '__main__':

    app = web.Application()
    #конфиг в глобально

    # маршруты
    app.router.add_route('GET', '/', Main)
    app.router.add_route('GET', '/check_health/', checkHealth)
    # базка
    app.on_startup.append(init)
    app.on_cleanup.append(close)
    # ЗАПУСК!
    web.run_app(app, host=config.get('host'), port=config.get('port'))

