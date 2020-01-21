from typing import Optional, Tuple, Union

from aiohttp import web
from aiohttp.web import HTTPOk, Response
from aiohttp_apispec import (docs, json_schema, match_info_schema,
                             querystring_schema, response_schema)

from account import selectors
from account.models import Account
from account.schemas import (MatchInfoSchema, RawBalanceSchema, RequestSchema,
                             ResponseSchema)
from utils import not_found, response


@docs(tags=["Account"],
      summary="Return info about account.")
@match_info_schema(MatchInfoSchema)
@querystring_schema(RawBalanceSchema)
@response_schema(ResponseSchema)
async def status(request):
    account_uuid = request["match_info"]["account_uuid"]
    acc, bad_response = await get_account(account_uuid)
    if bad_response is not None:
        return bad_response
    raw_balance = request["querystring"]["raw_balance"]
    if raw_balance:
        acc.raw_balance = True
    return response(status=HTTPOk.status_code, result=True,
                    addition=ResponseSchema().dump(acc))


@docs(tags=["Account"],
      summary="Refill account balance.")
@match_info_schema(MatchInfoSchema)
@json_schema(RequestSchema)
@response_schema(ResponseSchema)
async def add(request):
    account_uuid = request.match_info.get("account_uuid")
    acc, bad_response = await get_account(account_uuid, lock=True)
    if bad_response is not None:
        return bad_response
    refill_amount = request["json"]["amount"]
    await acc.update(balance=acc.balance + refill_amount).apply()
    return response(status=HTTPOk.status_code, result=True,
                    addition=ResponseSchema().dump(acc))


@docs(tags=["Account"],
      summary="Subtract account balance.")
@match_info_schema(MatchInfoSchema)
@json_schema(RequestSchema)
@response_schema(ResponseSchema)
async def subtract(request):
    account_uuid = request.match_info.get("account_uuid")
    acc, bad_response = await get_account(account_uuid, lock=True)
    if bad_response is not None:
        return bad_response
    subtract_amount = request["json"]["amount"]
    if not acc.subtract_is_allowed(subtract_amount):
        return response(status=web.HTTPPaymentRequired.status_code,
                        result=False, addition=ResponseSchema().dump(acc),
                        description="Insufficient funds")
    await acc.update(hold=acc.hold + subtract_amount).apply()
    return response(status=HTTPOk.status_code, result=True,
                    addition=ResponseSchema().dump(acc))


async def get_account(uuid: str, lock: Optional[bool] = False
                      ) -> Tuple[Union[Account, Response], bool]:
    acc = await selectors.get_account(uuid=uuid, lock=lock)
    if acc is None:
        return None, not_found(Account().__class__.__name__)
    if not acc.is_active:
        return None, response(status=400, result=False,
                              addition=ResponseSchema().dump(acc),
                              description="Account is disabled")
    return acc, None
