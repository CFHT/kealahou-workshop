import json
import random
import sys

from .api import api_request
from .config import vverbose, verbose


def example_og(program_token, instrument, target=None, observing_template=None):
    if target is None or observing_template is None:
        print(
            f"An observing template and a target needs to be provided for OG creation for program {program_token} on instrument {instrument}")
        sys.exit(0)
    print(f"Target {target}")
    data = {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'og_priority': 'MEDIUM',
        'target_type': 'OBJECT',
        'single_observing_group': {
            'observing_block': {
                'observing_component': [{
                    'target_token': target['token'],
                    'observing_template_token': observing_template['token'],
                }],
            },
        },
    }
    return data


def get_og_list_example(program_token: str):
    """
    Params:
        program_token: str The token of the select program.

        returns: JSON of observing group results
    """
    try:
        ogs = api_request(f"programs/{program_token}/observing-groups", method='GET')
    except Exception as e:
        print(f"Getting OGs failed: {e}")
        sys.exit()

    for og in ogs['entity']:
        print(f"OG{og['label']}, OG priority: {og['og_priority']}")
        if verbose or vverbose:
            print(json.dumps(og, indent=4))
            print()
    return ogs['entity']


def set_og_example(program_token, instrument, target=None, observing_template=None):
    """
    Creates a Observing Group via API put call based on given parameters.
    Prints the response

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
        target: str
        observing_template: JSON str

    Returns:
        nothing.
    """
    new_og = example_og(program_token, instrument, target, observing_template)
    response = api_request(f"programs/{program_token}/observing-groups/{new_og['token']}", method='PUT', data={
        'entity': new_og,
    })
    og = response['entity']
    print(
        f"Created observing group OG{og['label']} [token = {og['token']}] for program {program_token} using {instrument}")


def delete_og_example(program_token, instrument):
    """
    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    ogs = get_og_list_example(program_token)
    og = ogs[-1]
    try:
        api_request(f"observing-groups/{og['token']}", method='DELETE')
        print(f"Deleted observing group OG{og['label']} [token = {og['token']}]")
    except Exception as e:
        print(f"Target deletion failed")
    print()
