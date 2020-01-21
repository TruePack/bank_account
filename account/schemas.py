from marshmallow import Schema, fields, post_load

from account.models import Account
from account.validators import validate_amount


class RawBalanceSchema(Schema):
    raw_balance = fields.Bool(
        missing=False,
        description="Return raw balance without holds if True")


class ResponseSchema(Schema):
    uuid = fields.UUID(required=True)
    last_name = fields.Str()
    first_name = fields.Str()
    middle_name = fields.Str(allow_none=True)
    balance = fields.Method("get_balance")
    status = fields.Bool(attribute="bank_account_status")

    @staticmethod
    def get_balance(account: Account) -> str:
        balance = account.current_balance
        if isinstance(balance, int):
            return balance/100
        return balance


class RequestSchema(Schema):
    amount = fields.Float(validate=validate_amount, required=True,
                          description="Amount to change balance. "
                                      "Format must be like 19.99")

    @post_load()
    def convert_amount_to_int(self, data, *args, **kwargs):
        data["amount"] = int(data["amount"] * 100)
        return data


class MatchInfoSchema(Schema):
    account_uuid = fields.UUID(required=True)
