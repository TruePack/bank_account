import logging

from aiohttp.web import HTTPInternalServerError, HTTPOk

from database import Gino
from utils import response


async def ping(request):
    db = Gino.init()
    try:
        db_status = await db.status(db.text('SELECT 1'))
        logging.info(f"Database health check, response={db_status}")
        return response(status=HTTPOk.status_code, result=True,
                        description="Im alive!")
    except Exception as error:
        logging.fatal(error, exc_info=True)
        return response(status=HTTPInternalServerError.status_code,
                        result=False,
                        description="Health check failed. Repair me!")
