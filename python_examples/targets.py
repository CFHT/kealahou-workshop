import json
import random

from . import config
from .api import api_request, EntityCrudApi
from .constants import INSTRUMENT, required_mag_by_instrument, entity_desc

target_api = lambda program_token: EntityCrudApi(program_token, 'targets')
target_desc = lambda target: entity_desc(target, 'T')


def example_fixed_target(program_token: str, instrument: INSTRUMENT):
    """
    Generate data for a fixed target under a specified program.
    Params:
        program_token: str The token of the program the target will belong to.
        instrument: The instrument the target will be observed with.
    Returns:
        Formatted JSON to be used in an API call to create a single fixed target.
    """
    mag_key = required_mag_by_instrument.get(instrument, None)
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'DD target 1',
        'fixed_target': {
            'coordinate': {
                'ra': random.uniform(0, 359.9999),  # Values are in decimal degrees.
                'dec': random.uniform(-90, 90),
            },
            'proper_motion': {'ra_mas': -15.468, 'dec_mas': 12.5},
            'estimated_radial_velocity_kmps': {'value': 234.0} if instrument == 'SPIROU' else None,
        },
        'magnitude': {mag_key: {'value': 25.0}} if mag_key else {},
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }


def example_moving_target(program_token: str, instrument: INSTRUMENT):
    """
    Generate data for a moving target under a specified program.
    Params:
        program_token: The token of the program the target will belong to.
        instrument: The instrument the target will be observed with.
    Returns:
        Formatted JSON to be used in an API call to create a single moving target.
    """
    mag_key = required_mag_by_instrument.get(instrument, None)
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'DD moving target 2.',
        'moving_target': {
            'ephemeris_point': [{
                'mjd': 61041.0 + i,
                'coordinate': {
                    'ra': random.uniform(0, 359.9999),
                    'dec': random.uniform(-90, 90),
                },
            } for i in range(0, 5)],
        },
        'magnitude': {mag_key: {'value': 25.0}} if mag_key else {},
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }


def create_target_example(program_token: str, instrument: INSTRUMENT, moving_target=False):
    """
    Creates a target based on the program token, validating using the instrument.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
        moving_target: Creates a moving target if true, otherwise creates a fixed target.
    Returns:
        Nothing
    """

    if moving_target:
        new_target = example_moving_target(program_token, instrument)
    else:
        new_target = example_fixed_target(program_token, instrument)

    api = target_api(program_token)

    print(f"Creating {target_desc(new_target)}")

    try:
        result = api.create_or_update(new_target)
    except Exception as e:
        print(f"Problem creating new target for {program_token} using {instrument}: {e}.")
        return

    print(f"Target created for program {program_token} using {instrument}.")
    if config.verbose:
        print(result)


def delete_target_example(program_token: str):
    """
    Deletes the latest target based on the program id.
    Params:
        program_token: str The token of the select program.
    """
    api = target_api(program_token)

    try:
        existing_targets = api.list()
    except Exception as e:
        print(f"Listing targets in {program_token} failed: {e}")
        return

    print(f"{len(existing_targets)} targets currently on {program_token}")

    try:
        target_to_delete = existing_targets[-1]
    except IndexError:
        print(f"No targets to delete in {program_token}")
        return

    print(f"Deleting {target_desc(target_to_delete)}")

    try:
        api.delete(target_to_delete['token'])
        print(f"Target {target_desc(target_to_delete)} deleted")
    except Exception as e:
        print(f"Problem deleting {target_desc(target_to_delete)}: {e}")
        return

    remaining_targets = api.list()
    print(f"{len(remaining_targets)} targets remain on {program_token}")
    if config.verbose:
        print(f"Remaining targets: {remaining_targets}")
        for target in enumerate(remaining_targets):
            print(target)
            print()


def get_target_list_example(program_token: str):
    """
    Prints a target list from a single program.
    """

    print(f"Listing targets for program {program_token}")

    api = target_api(program_token)
    try:
        targets = api.list()
    except Exception as e:
        print(f"API request to get list of targets failed: {e}")
        return

    print(f'All targets for {program_token}:')
    for target in targets:
        print(target_desc(target))
        if config.verbose:
            print(json.dumps(target, indent=4))
    print("#" * 80)


def get_target_by_index(program_token: str, idx=0):
    api = target_api(program_token)
    try:
        targets = api.list()
    except Exception as e:
        print(f"API request to get list of targets failed: {e}")
        return None
    try:
        return targets[idx]
    except IndexError:
        print(f"No target at index {idx}")
        return None


def get_megacam_default_pointing_offset_example():
    """
    List the system-defined pointing offsets for MEGACAM

    Prints JSON attributes
    """
    instrument = 'MEGACAM'
    response = api_request('pointing_offset', data={
        'instrument': instrument
    })

    offsets = response['entity']

    if offsets:
        print(f"Pointing Offsets for {instrument}:")
        for offset in offsets:
            print(offset)
    else:
        print(f"No default pointing offsets found.")
