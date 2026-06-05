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
    Lists the observing groups for the specified program.

    Parameters:
        program_token: The token of the program to list observing groups from.
    """

    print(f"Listing observing groups for program {program_token}")

    api = observing_group_api(program_token)
    try:
        observing_groups = api.list()
    except Exception as e:
        print(f"API request to get list of observing groups failed: {e}")
        return

    print(f'All observing groups for {program_token}:')
    for og in observing_groups:
        print(f"{observing_group_desc(og)}, OG priority: {og['og_priority']}")
        if config.verbose:
            print(json.dumps(og, indent=4))
            print()


def create_og_example(program_token, instrument: INSTRUMENT, target, observing_template):
    """
    Create an observing group target under the specified program, to be observed with the specified instrument.
    The observing group will consist of a single observation of the specified target and observing template.

    Parameters:
        program_token: The token of the program to create a target under.
        instrument: The instrument the target will be observed with.
        target: The target to be observed.
        observing_template: The observing template to be used for observation.
    """
    new_og = example_observing_group(program_token, target, observing_template)

    api = observing_group_api(program_token)

    print(f"Creating {observing_group_desc(new_og)}")

    try:
        result = api.create_or_update(new_og)
    except Exception as e:
        print(f"Problem creating new observing group for {program_token} using {instrument}: {e}.")
        return

    print(f"Created observing group {observing_group_desc(result)} for program {program_token} using {instrument}")
    if config.verbose:
        print(result)


def delete_og_example(program_token):
    """
    Deletes the latest observing group under the specified program.

    Parameters:
        program_token: The token of the program to delete an observing group from.
    """
    api = observing_group_api(program_token)

    try:
        existing_ogs = api.list()
    except Exception as e:
        print(f"Listing observing groups in {program_token} failed: {e}")
        return

    print(f"{len(existing_ogs)} observing groups currently on {program_token}")

    try:
        og_to_delete = existing_ogs[-1]
    except IndexError:
        print(f"No observing groups to delete in {program_token}")
        return

    print(f"Deleting {observing_group_desc(og_to_delete)}")

    try:
        api.delete(og_to_delete['token'])
        print(f"{observing_group_desc(og_to_delete)} deleted")
    except Exception as e:
        print(f"Problem deleting {observing_group_desc(og_to_delete)}: {e}")
        return

    remaining_ogs = api.list()
    print(f"{len(remaining_ogs)} observing groups remain on {program_token}")
    if config.verbose:
        print(f"Remaining observing groups: {remaining_ogs}")
        for observing_group in enumerate(remaining_ogs):
            print(observing_group)
            print()
