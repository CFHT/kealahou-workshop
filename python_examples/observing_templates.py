import json
from typing import Any

from .api import api_request
from .config import verbose


def get_ot_list_example(program_token: str) -> Any:
    """
    API call prints Observing Templates based
    Params:
        program_token: str The token of the select program.
    Returns:
        Nothing
    """
    response = api_request(f'programs/{program_token}/observing-templates')
    print(f'All observing templates for {program_token}:')
    for ot in response['entity']:
        print(f"OT{ot['label']} - {ot['name']} [token = {ot['token']}]")
        if verbose:
            print(json.dumps(ot, indent=4, sort_keys=True))
    print()

    ot_out = response['entity'][0]

    return ot_out
