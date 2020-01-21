import functools
import json
from typing import Generator, Optional, Tuple, Union

from aiohttp import web
from marshmallow import ValidationError
from yarl import URL

pretty_json = functools.partial(json.dumps, indent=4)


def response(*, status: int, result: bool, addition: Optional[dict]=None,
             description: Union[None, str, dict] = None) -> web.Response:
    data = serialize_data_to_generic_response(status=status, result=result,
                                              addition=addition,
                                              description=description)
    return web.json_response(status=status, data=data, dumps=pretty_json)


def not_found(model: str) -> web.Response:
    return response(status=web.HTTPNotFound.status_code, result=False,
                    addition={"error": "Not found"},
                    description=f"{model} not found")


def serialize_data_to_generic_response(
        *, status: int, result: bool,
        addition: Optional[dict]=None,
        description: Union[None, str, dict] = None) -> dict:
    data = {
        "status": status,
        "result": result,
        "addition": {},
        "description": {},
    }
    if description:
        data["description"] = description
    if addition:
        data["addition"] = addition
    return data


def url_for(request: web.Request, resource_name: str,
            resource_kwargs: Optional[dict] = None) -> URL:
    if resource_kwargs is None:
        resource_kwargs = {}
    return request.app.router[resource_name].url_for(**resource_kwargs)


async def validation_error_handler(error: ValidationError, *args) -> None:
    field, error = return_field_and_error(error=error)
    body = serialize_data_to_generic_response(
        status=web.HTTPBadRequest.status_code, result=False,
        addition={"error": "Validation error"},
        description={"field": field, "error": error})
    raise web.HTTPBadRequest(body=pretty_json(body))


def return_field_and_error(error: ValidationError) -> Tuple[str, str]:
    dict_error = error.normalized_messages()
    key, value = get_last_key_value(nested_dict=dict_error).__next__()
    return key, value


def get_last_key_value(nested_dict: dict, key: Optional[str] = None
                       ) -> Generator[Tuple[str, str], None, None]:
    if isinstance(nested_dict, dict):
        value = list(nested_dict.values())[0]
        key = list(nested_dict.keys())[0]
        yield from get_last_key_value(nested_dict=value, key=key)
    else:
        yield key, nested_dict[0]
