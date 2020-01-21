import asyncio
import json
from uuid import uuid4

from account.models import Account
from crontabs import update_holds
from tests.fixtures import ACC1_UUID, ACC4_UUID
from utils import url_for


class TestAccount:
    async def test_account_status(self, client, db_data):

        url = url_for(client, "status",
                      resource_kwargs={"account_uuid": ACC1_UUID})
        resp = await client.get(url)
        resp_data = await resp.json()

        assert resp.status == 200
        assert resp_data == {
            'status': 200,
            'result': True,
            'addition': {'uuid': '26c940a1-7228-4ea2-a3bc-e6460b172040',
                         'first_name': 'Иван',
                         'status': True,
                         'middle_name': 'Сергеевич',
                         'balance': 1400.0,
                         'last_name': 'Петров'},
            'description': {}}

    async def test_not_found_account_status(self, client, db_data):
        url = url_for(client, "status",
                      resource_kwargs={"account_uuid": f"{uuid4()}"})
        resp = await client.get(url)
        resp_data = await resp.json()
        assert resp.status == 404
        assert resp_data == {
            "status": 404,
            "result": False,
            "addition": {
                "error": "Not found"
            },
            "description": "Account not found"}

    async def test_add_function(self, client, db_data):
        url = url_for(client, "add",
                      resource_kwargs={"account_uuid": ACC1_UUID})
        resp = await client.patch(url, data=json.dumps({"amount": 50.00}),
                                  headers={'Content-Type': 'application/json'})

        resp_data = await resp.json()
        assert resp.status == 200
        assert resp_data == {
            'status': 200,
            'result': True,
            'addition': {'uuid': '26c940a1-7228-4ea2-a3bc-e6460b172040',
                         'first_name': 'Иван',
                         'status': True,
                         'middle_name': 'Сергеевич',
                         'balance': 1400.0 + 50.00,
                         'last_name': 'Петров'},
            'description': {}}

    async def test_add_function_with_disabled_acc(self, client, db_data):
        url = url_for(client, "add",
                      resource_kwargs={"account_uuid": ACC4_UUID})
        resp = await client.patch(url, data=json.dumps({"amount": 50.00}),
                                  headers={'content-type': 'application/json'})
        resp_data = await resp.json()
        assert resp.status == 400
        assert resp_data == {
            'status': 400,
            'result': False,
            'addition': {'balance': 999999.0,
                         'first_name': 'Петр',
                         'middle_name': 'Измаилович',
                         'uuid': '867f0924-a917-4711-939b-90b179a96392',
                         'last_name': 'Петечкин',
                         'status': False},
            'description': 'Account is disabled'}

    async def test_substract_function_with_disabled_acc(self, client, db_data):
        url = url_for(client, "substract",
                      resource_kwargs={"account_uuid": ACC4_UUID})
        resp = await client.patch(url, data=json.dumps({"amount": 50.00}),
                                  headers={'Content-Type': 'application/json'})
        resp_data = await resp.json()
        assert resp.status == 400
        assert resp_data == {
            'status': 400,
            'result': False,
            'addition': {'balance': 999999.0,
                         'first_name': 'Петр',
                         'middle_name': 'Измаилович',
                         'uuid': '867f0924-a917-4711-939b-90b179a96392',
                         'last_name': 'Петечкин',
                         'status': False},
            'description': 'Account is disabled'}

    async def test_substract_function(self, client, db_data):
        url = url_for(client, "substract",
                      resource_kwargs={"account_uuid": ACC1_UUID})
        resp = await client.patch(url, data=json.dumps({"amount": 50.00}),
                                  headers={'Content-Type': 'application/json'})
        resp_data = await resp.json()
        assert resp.status == 200
        assert resp_data == {
            'status': 200,
            'result': True,
            'addition': {'uuid': '26c940a1-7228-4ea2-a3bc-e6460b172040',
                         'first_name': 'Иван',
                         'status': True,
                         'middle_name': 'Сергеевич',
                         'balance': 1400.0 - 50.00,
                         'last_name': 'Петров'},
            'description': {}}

    async def test_substract_function_not_enough_balance(self, client,
                                                         db_data):
        url = url_for(client, "substract",
                      resource_kwargs={"account_uuid": ACC1_UUID})
        resp = await client.patch(url, data=json.dumps({"amount": 999999.00}),
                                  headers={'Content-Type': 'application/json'})
        resp_data = await resp.json()
        assert resp.status == 402
        assert resp_data == {
            'status': 402,
            'result': False,
            'addition': {'uuid': '26c940a1-7228-4ea2-a3bc-e6460b172040',
                         'first_name': 'Иван',
                         'status': True,
                         'middle_name': 'Сергеевич',
                         'balance': 1400.0,
                         'last_name': 'Петров'},
            'description': 'Insufficient funds'}

    async def test_crontabs(self, client, db_data):
        loop = asyncio.get_event_loop()
        loop.create_task(update_holds(1))
        await asyncio.sleep(2)
        accs_with_holds = await Account.query.where(
            Account.hold != 0).gino.all()
        assert len(accs_with_holds) == 0
