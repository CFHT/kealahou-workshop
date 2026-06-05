import json
from typing import Any

from . import config
from .api import EntityReadApi
from .constants import entity_desc

get_observing_template_api = lambda program_token: EntityReadApi(program_token, 'observing-templates')
observing_template_desc = lambda observing_template: entity_desc(observing_template, 'OT')


def get_observing_template_list_example(program_token: str) -> Any:
    """
    Lists the observing templates for the specified program.

    Parameters:
        program_token: The token of the program to list observing templates from.
    """
    api = get_observing_template_api(program_token)

    try:
        observing_templates = api.list()
    except Exception as e:
        print(f"API request to get list of observing templates failed: {e}")
        return

    print(f'All observing templates for {program_token}:')
    for observing_template in observing_templates:
        print(observing_template_desc(observing_template))
        if config.verbose:
            print(json.dumps(observing_template, indent=4))
    print()


def get_observing_template_by_index(program_token: str, idx=0):
    api = get_observing_template_api(program_token)
    try:
        observing_templates = api.list()
    except Exception as e:
        print(f"API request to get list of observing templates failed: {e}")
        return None
    try:
        return observing_templates[idx]
    except IndexError:
        print(f"No observing template at index {idx}")
        return None
