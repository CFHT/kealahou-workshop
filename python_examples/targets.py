import json
import random
import sys

from .api import api_request, EntityCrudApi
from .config import vverbose, verbose
from .constants import INSTRUMENT, required_mag_by_instrument


def example_fixed_target(program_token: str, instrument: INSTRUMENT):
    """
    Generate data for a fixed target under a specified program.
    :param program_token: The token of the program the target will belong to.
    :param instrument: The instrument the target will be observed with.
    :return: Formatted JSON to be used in an API call to create a single fixed target.
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
    :param program_token: The token of the program the target will belong to.
    :param instrument: The instrument the target will be observed with.
    :return: Formatted JSON to be used in an API call to create a single moving target.
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
    Creates a target based on the program token and instrument.  Also type of targe
    fixed or moving taget.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
        moving_target: Boolean. True creates moving. False is fixed.
    Returns:
        Nothing
    """

    if moving_target:
        new_target = example_moving_target(program_token, instrument)
    else:
        new_target = example_fixed_target(program_token, instrument)
    try:
        target_api = EntityCrudApi(program_token, 'targets')
        target_api.create_or_update(new_target)
        print(f"Target created for Program ID: {program_token} using {instrument}.")
    except Exception as e:
        print(f"Problem adding new target to {program_token} on {instrument} - {e}.")

    if verbose or vverbose:
        print(target_api)


def delete_target(program_token, target_name, target_token):
    """

    Deletes the latest based on the token and name.

    Params:
        program_token: str The token of the select program.
        target_name: Given name of the target.
        target_token: Given token of the target.
    Returns:
        Nothing
    """
    try:
        target_api = EntityCrudApi(program_token, 'targets')
    except Exception as e:
        print(f"Problem getting target_api from {program_token} - {e}")

    try:
        target_api.delete(target_token)
        print(f"Target {target_name} deleted")
    except Exception as e:
        print(f"Problem deleting {target_name} - {e}")


def delete_target_example(program_token, instrument):
    """

    Deletes the latest target based on the program id.
    The target id and name is passed for deletion.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    try:
        target_api = EntityCrudApi(program_token, 'targets')
    except Exception as e:
        print(f"Problem getting target_api from {program_token} on {instrument} - {e}")

    deleted_target = target_api.list()[-1]
    print(f"Deleting {deleted_target['name']},{deleted_target['token']}")

    delete_target(program_token, deleted_target['name'], deleted_target['token'])

    if verbose or vverbose:
        for i, target in enumerate(target_api.list()):
            print(f"Target {i}")
            print(target)
            print()


def get_target_list_example(program_token, instrument):
    """
    Prints a target list from a single program.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).

    Returns: JSON Target response entity.
    """

    print(f"Attempting to display Target List for Program ID: {program_token} with {instrument}")

    try:
        response = api_request('programs')
        programs = response['entity']
        target_response = api_request(f'/programs/{program_token}/targets')
    except Exception as e:
        print(f"API request to get list targets failed: {e}")
        sys.exit()

    print(f'All targets for {program_token}:')
    for target in target_response['entity']:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
        if verbose:
            print(f"API target keys/values")
            print(f"{json.dumps(target_response['entity'], indent=4, sort_keys=True)}")
    print("#" * 80)

    if vverbose:
        print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")

    return target_response['entity']


def get_target_example(program_token, instrument, idx=0):
    return get_target_list_example(program_token, instrument)[idx]


def get_megacam_default_pointing_offset_example():
    """
    Simple API example to list pointing offsets for MEGACAM

    Prints JSON attributes
    """
    instrument = 'MEGACAM'
    response = api_request('pointing_offset', data={
        'instrument': instrument
    })

    offsets = response['entity']

    if offsets:
        print(f"Pointing Offsets for {instrument} below:")
        for offset in offsets:
            print(offset)
    else:
        print(f"No default pointing offsets found.")
