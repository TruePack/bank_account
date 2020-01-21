import pytest
import sqlalchemy as sa
from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware
from sqlalchemy_utils import create_database, database_exists
from tests.fixtures import ACC1_UUID, ACC2_UUID, ACC3_UUID, ACC4_UUID
from account.models import Account
from account.routes import routes as acc_routes
from database import Gino
from ping.routes import routes as ping_routes


def create_app():
    app = web.Application()
    db = Gino.init()
    host = "postgres"
    user = "postgres"
    database = "gino_test"
    sync_db_engine = sa.create_engine(f"postgresql://{host}@{user}/"
                                      f"{database}")
    if not database_exists(sync_db_engine.url):
        create_database(sync_db_engine.url)
    db.create_all(bind=sync_db_engine)
    sync_db_engine.dispose()
    db.init_app(app, config={"user": user, "database": database, "host": host})
    routes = [*acc_routes, *ping_routes]
    app.router.add_routes(routes)
    middlewares = [db, validation_middleware]
    app.middlewares.extend(middlewares)
    setup_aiohttp_apispec(app=app, in_place=True)
    return app


@pytest.fixture
def client(loop, aiohttp_client):
    app = create_app()
    return loop.run_until_complete(aiohttp_client(app))


@pytest.yield_fixture()
async def db_data():
    await Account.delete.gino.all()
    # Multiply all balances and holds to 100 for store as int at database
    acc1 = Account(uuid=ACC1_UUID,
                   first_name="Иван", last_name="Петров",
                   middle_name="Сергеевич", balance=1700_00, hold=300_00,
                   bank_account_status=True)
    acc2 = Account(uuid=ACC2_UUID,
                   first_name="Jason", last_name="Kazitsky", balance=200_00,
                   hold=200_00,
                   bank_account_status=True)
    acc3 = Account(uuid=ACC3_UUID,
                   first_name="Антон", last_name="Пархоменко",
                   middle_name="Александрович", balance=1_00, hold=300_00,
                   bank_account_status=True)
    acc4 = Account(uuid=ACC4_UUID,
                   first_name="Петр", last_name="Петечкин",
                   middle_name="Измаилович", balance=1_000_000_00, hold=1_00,
                   bank_account_status=False)
    accs = [acc1, acc2, acc3, acc4]

    for acc in accs:
        await acc.create()

    yield
    await Account.delete.gino.all()
