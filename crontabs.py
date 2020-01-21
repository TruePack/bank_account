import asyncio
import logging
from typing import NoReturn

from account.models import Account


async def update_holds(timeout: int) -> NoReturn:
    while True:
        await asyncio.sleep(timeout)
        info, _ = await Account.update.values(
            hold=0, balance=Account.balance - Account.hold
        ).where(
            Account.hold > 0
        ).gino.status()
        logging.info(f"Holds and balances updated, db resp: '{info}'")
