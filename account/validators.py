from marshmallow import ValidationError

INVALID_AMOUNT = "Invalid amount"


def validate_amount(amount: float) -> None:
    if str(amount) != str(int(amount*100) / 100):
        raise ValidationError(INVALID_AMOUNT)
