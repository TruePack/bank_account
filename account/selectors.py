from typing import Optional

from account.models import Account


async def get_account(uuid: str, lock: bool) -> Optional[Account]:
    if not lock:
        acc = await Account.get(uuid)
    else:
        acc = await Account.query.where(
            Account.uuid == uuid).with_for_update().gino.first()
    return acc
