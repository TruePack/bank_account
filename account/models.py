from datetime import datetime
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from database import Gino

db = Gino.init()


class Account(db.Model):
    __tablename__ = "accounts"

    uuid = db.Column(UUID(), unique=True, nullable=False,
                     primary_key=True, default=uuid4)
    last_name = db.Column(db.Unicode(256), nullable=False)
    first_name = db.Column(db.Unicode(256), nullable=False)
    middle_name = db.Column(db.Unicode(256), nullable=True)
    balance = db.Column(db.Integer(), default=0)
    hold = db.Column(db.Integer(), default=0)
    bank_account_status = db.Column(db.Boolean(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.raw_balance = False

    @property
    def current_balance(self) -> int:
        if self.raw_balance:
            return self.balance
        return self.balance - self.hold

    @property
    def is_active(self) -> bool:
        return self.bank_account_status

    def subtract_is_allowed(self, subtract_amount: int) -> bool:
        return self.balance > self.hold + subtract_amount
