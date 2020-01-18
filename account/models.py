from datetime import datetime

from gino import Gino

db = Gino()


class Account(db.Model):
    __tablename__ = "accounts"

    uuid = db.Column(db.UUID(as_uuid=True), unique=True, nullable=False)
    last_name = db.Column(db.Unicode(256), nullable=False)
    first_name = db.Column(db.Unicode(256), nullable=False)
    middle_name = db.Column(db.Unicode(256), nullable=True)
    current_balance = db.Column(db.Integer(), default=0)
    current_hold = db.Column(db.Integer(), default=0)
    bank_account_status = db.Column(db.Boolean(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now)
