import json
import random
import sys

from . import config
from .api import EntityCrudApi
from .constants import INSTRUMENT, entity_desc

observing_group_api = lambda program_token: EntityCrudApi(program_token, 'observing-groups')
observing_group_desc = lambda observing_group: entity_desc(observing_group, 'OG')


def example_observing_group(program_token, target, observing_template):
    if target is None or observing_template is None:
        print(f"An observing template and a target must be provided for OG creation")
        sys.exit(0)
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
    api = observing_group_api(program_token)
    try:
        observing_groups = api.list()
    except Exception as e:
        print(f"Getting OGs failed: {e}")
        sys.exit()

    for og in observing_groups:
        print(f"{observing_group_desc(og)}, OG priority: {og['og_priority']}")
        if config.verbose:
            print(json.dumps(og, indent=4))
            print()
    return observing_groups


def create_og_example(program_token, instrument: INSTRUMENT, target, observing_template):
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
    new_og = example_observing_group(program_token, target, observing_template)
    api = observing_group_api(program_token)
    og = api.create_or_update(new_og)
    print(
        f"Created observing group {observing_group_desc(og)} for program {program_token} using {instrument}")


def delete_og_example(program_token):
    """
    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    ogs = get_og_list_example(program_token)
    og = ogs[-1]
    api = observing_group_api(program_token)
    try:
        api.delete(og['token'])
        print(f"Deleted observing group {observing_group_desc(og)}")
    except Exception as e:
        print(f"Observing group deletion failed: {e}")
    print()
