import asyncio
import logging
import sys
from typing import NoReturn
import sqlalchemy as sa
import yaml
from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from gino.ext.aiohttp import Gino
from utils import validation_error_handler
from account.routes import routes as acc_routes
from crontabs import update_holds
from database import Gino
from ping.routes import routes as ping_routes


def main() -> NoReturn:
    app_conf = config.get("app", {})
    app = init_app()
    init_logger()
    init_crontabs(app_conf)
    host = app_conf.get("host", "0.0.0.0")
    port = app_conf.get("port", 80)
    web.run_app(app, host=host, port=port)


def init_app() -> web.Application:
    app = web.Application()
    app["config"] = {}
    # Setup routes
    routes = [*acc_routes, *ping_routes]
    app.router.add_routes(routes)
    # Setup DB connection
    db = init_db(app)
    # Setup middlewares
    middlewares = [db, validation_middleware]
    app.middlewares.extend(middlewares)
    # Setup api_spec
    setup_aiohttp_apispec(
        error_callback=validation_error_handler,
        app=app,
        title="API documentation",
        version="v1",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs")
    return app


def init_db(app: web.Application) -> Gino:
    db = Gino.init()
    db_conf = config.get("database")
    app["config"]["gino"] = db_conf
    db.init_app(app)
    host = db_conf.get("host", "postgres")
    user = db_conf.get("user", "postgres")
    database = db_conf.get("database", "gino")
    sync_db_engine = sa.create_engine(f"postgresql://{host}@{user}/"
                                      f"{database}")
    db.create_all(bind=sync_db_engine)
    sync_db_engine.dispose()
    return db


def init_crontabs(app_conf: dict) -> None:
    loop = asyncio.get_event_loop()
    loop.create_task(update_holds(app_conf.get("hold_update_time", 600)))


def init_logger() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def init_config() -> dict:
    with open("config.yml", "r") as yaml_cfg:
        cfg = yaml.load(yaml_cfg)
    return cfg or {}


config = init_config()

if __name__ == "__main__":
    main()

