"""
Note that, for real world usage, a library such as requests (https://requests.readthedocs.io/)
is better suited for submitting HTTP requests than the stock Python urllib.
"""

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from . import config


def api_request(endpoint, data=None, method='GET'):
    """
    Submit a request to the Kealahou API, and condense any errors into a consistent error message format.
    :param endpoint: Path for the desired method to append to the base URL
    :param data: Data to send in the request
    :param method: HTTP method to use for the specified endpoint
    :return: Response
    :raise: Exception with a simple message describing what went wrong
    """

    if data is None:
        data = {}

    headers = {
        'Authorization': f'Bearer {config.access_token}',
        'Content-Type': 'application/json',
    }

    url = f'{config.api_url}/{endpoint}'

    if config.vverbose:
        print(f"Request")
        print(f"URL: {url}")
        print(f"Data: {data}")
        print("#" * 80)

    request = Request(url, json.dumps(data).encode('utf-8'), headers, method=method)
    http_error = None
    try:
        raw_response = urlopen(request)
    except HTTPError as e:
        http_error = str(e)
        try:
            response = json.loads(e.read().decode('utf-8'))
        except json.JSONDecodeError:
            response = dict()
    else:
        response = json.loads(raw_response.read().decode('utf-8'))

    if config.vverbose:
        print(f"Response: {json.dumps(response, indent=4, default=lambda val: "")}")

    if response.get('success'):
        return response
    elif response.get('error') and response['error']['messages']:
        raise Exception(f"API request failed: {', '.join(response['error']['messages'])}")
    elif http_error:
        raise Exception(f"API request failed ({http_error})")
    else:
        raise Exception('API request failed, but no error message was given')


class EntityReadApi:
    """
    Wrapper around the Kealahou API read methods for a given program and entity type.
    """

    def __init__(self, program_token: str, entity_type: str):
        self.path_prefix = f'programs/{program_token}/{entity_type}'

    def list(self) -> list[dict]:
        api_response = api_request(f'{self.path_prefix}', method='GET')
        return api_response['entity']

    def show(self, token: str) -> dict:
        api_response = api_request(f'{self.path_prefix}/{token}', method='GET')
        return api_response['entity']


class EntityCrudApi(EntityReadApi):
    """
    Wrapper around the Kealahou API CRUD methods for a given program and entity type.
    """

    def __init__(self, program_token: str, entity_type: str):
        super().__init__(program_token, entity_type)

    def create_or_update(self, entity: dict, request_aux_data: dict = None) -> dict:
        if request_aux_data is None:
            request_aux_data = {}
        version = entity.get('version', None)
        lock_version = {
            'value': version,
        } if version else None
        api_response = api_request(f"{self.path_prefix}/{entity['token']}", method='PUT', data={
            'entity': entity,
            'lock_version': lock_version,  # Use version-locking to prevent accidental overwrites
            **request_aux_data,
        })
        return api_response['entity']

    def delete(self, entity_token: str):
        api_request(f'{self.path_prefix}/{entity_token}', method='DELETE')
