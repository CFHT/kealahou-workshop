"""
Examples of using the Kealahou API for PI program management.
All API interactions in these examples should be considered as non-final design, and subject to change.

An access token is necessary to run these examples. See the README for details.

Note that, for real world usage, a library such as requests (https://requests.readthedocs.io/)
is better suited for submitting HTTP requests than the stock Python urllib.
"""

import json
import random
import argparse
from typing import Literal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

KEY_FILE = '.access_token'
BASE_URL = 'https://api-stage.cfht.hawaii.edu'

INSTRUMENT = Literal['SPIROU', 'ESPADONS', 'MEGACAM']
access_token = None
versbose = False
example = 'all'

required_mag_by_instrument: dict[INSTRUMENT, str] = {
    'SPIROU': 'H',
    'ESPADONS': 'V',
    'MEGACAM': 'AB',
}


def api_request(endpoint, data=None, method='GET'):
    """
    Submit a request to the Kealahou API, and condense any errors into a consistent error message format.
    """

    if data is None:
        data = {}
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    url = f'{BASE_URL}/{endpoint}'
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

    if response.get('success'):
        return response
    elif response.get('error') and response['error']['messages']:
        raise Exception(f"API request failed: {', '.join(response['error']['messages'])}")
    elif http_error:
        raise Exception(f"API request failed ({http_error})")
    else:
        raise Exception('API request failed, but no error message was given')


class EntityCrudApi:
    """
    Wrapper around the Kealahou API CRUD methods for a given program and entity type.
    """

    def __init__(self, program_token: str, entity_type: str):
        self.path_prefix = f'/programs/{program_token}/{entity_type}'

    def list(self) -> list[dict]:
        api_response = api_request(f'{self.path_prefix}')
        return api_response['entity']

    def show(self, token: str) -> dict:
        api_response = api_request(f'{self.path_prefix}/{token}')
        return api_response['entity']

    def create_or_update(self, entity: dict, request_aux_data: dict = {}) -> dict:
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

def example_fixed_target(program_token: str, instrument=INSTRUMENT):
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'My new fancy fixed target!',
        'fixed_target': {
            'coordinate': {
                'ra': random.uniform(0, 359.9999),
                'dec': random.uniform(-90, 90),
            },
            'proper_motion': {},
            'estimated_radial_velocity_kmps': {'value': 234.0} if instrument == 'SPIROU' else None,
        },
        'magnitude': {
        },
        'temperature_effective': 10000,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }


def example_moving_target(program_token: str, instrument=INSTRUMENT):
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'My new moving target!',
        'moving_target': {
            'ephemeris_point': [{
                'mjd': 61041.0 + i,
                'coordinate': {
                    'ra': random.uniform(0, 359.9999),
                    'dec': random.uniform(-90, 90),
                },
            } for i in range(0, 5)],
        },
        'magnitude': {
        },
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }

def target_api_examples(program_token: str, instrument: INSTRUMENT):
    """
    Complete API examples for Kealahou targets.
    """
    print(f'Running through target API examples for {program_token}...')
    print()
    target_api = EntityCrudApi[dict](program_token, 'targets')

    # List targets
    targets = target_api.list()
    print(f'All targets for {program_token}:')
    for target in targets:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

    new_target = example_fixed_target(program_token, instrument)

    # Invalid new target data, value is wrong type
    new_target['fixed_target']['coordinate']['ra'] = 'twenty point seven degrees'

    # Attempt to create invalid target
    try:
        print('Trying to create target...')
        target_api.create_or_update(new_target)
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Correct bad format, but new value is out of range
    new_target['fixed_target']['coordinate']['ra'] = 2220.7

    # Attempt again with out-of-range value
    try:
        print('Trying to create target...')
        target_api.create_or_update(new_target)
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Correct value
    new_target['fixed_target']['coordinate']['ra'] = 20.7

    # Attempt again, only missing instrument-specific fields
    try:
        print('Trying to create target with instrument validation...')
        # Specify instrument to perform extra validation checks
        target_api.create_or_update(new_target, {'instrument': instrument})
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Add instrument-specific data
    new_target['magnitude'] = {
        required_mag_by_instrument[instrument]: {
            'value': 10.0,
        },
    }

    # Successfully create new target with instrument-specific checks
    target = target_api.create_or_update(new_target, {'instrument': instrument})
    print(f"Created target T{target['label']} - {target['name']} [token = {target['token']}] "
          f"(version={target['version']})")
    print()

    # Update target
    update_target = target
    update_target['standard_star'] = True
    target = target_api.create_or_update(update_target, {'instrument': instrument})
    print(f"Updated T{target['label']} - {target['name']} [token = {target['token']}] (version={target['version']})")
    print()

    # Attempt to update target again with stale version
    # NOTE: This doesn't seem to be working correctly on staging as of 2026-03-09... under investigation
    try:
        target_api.create_or_update(update_target, {'instrument': instrument})
    except Exception as e:
        print(f'Target update failed - {e}')
        print()

    # Fetch single target
    target = target_api.show(new_target['token'])
    print(f"Fetched T{target['label']} - {target['name']} [token = {target['token']}] (version={target['version']})")
    print()

    # Delete the new (unobserved) target
    target_api.delete(target['token'])
    print(f"Deleted target T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

    try:
        target_api.show(target['token'])
    except Exception as e:
        print(f'Target show failed - {e}')
        print()

    moving_target = example_moving_target(program_token, instrument)
    moving_target['magnitude'] = {
        required_mag_by_instrument[instrument]: {
            'value': 10.0,
        },
    }

    # Create moving target
    moving_target = target_api.create_or_update(moving_target, {'instrument': instrument})
    print(f"Created target T{moving_target['label']} - {moving_target['name']} [token = {moving_target['token']}] "
          f"(version={moving_target['version']})")
    print()

    # Delete the new (unobserved) moving target
    target_api.delete(moving_target['token'])
    print(f"Deleted target T{moving_target['label']} - {moving_target['name']} [token = {moving_target['token']}]")
    print()

def k2_example_walkthrough(program_token: str, instrument: INSTRUMENT):
    """
    Walkthrough of work-in-progress API examples for full K2 program management.
    """
    print(f'K2 examples for program {program_token} ({instrument})')
    print()

    # List observing templates
    response = api_request(f'/programs/{program_token}/observing-templates')
    print(f'All observing templates for {program_token}:')
    for ot in response['observing_template']:
        print(f"OT{ot['label']} - {ot['name']} [token = {ot['token']}]")
    print()
    first_ot = response['observing_template'][0]  # Save for later example

    # Create new target
    target_api = EntityCrudApi[dict](program_token, 'targets')
    target = target_api.create_or_update(example_fixed_target(program_token, instrument))

    # Create new basic OG from new target
    new_og = {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'og_priority': 'MEDIUM',
        'target_type': 'OBJECT',
        'single_observing_group': {
            'observing_block': {
                'observing_component': [{
                    'target_token': target['token'],
                    'observing_template_token': first_ot['token'],
                }],
            },
        },
    }
    response = api_request(f"programs/{program_token}/observing-groups/{new_og['token']}", method='PUT', data={
        'observing_group': new_og,
    })
    og = response['observing_group']
    print(f"Created observing group OG{og['label']} [token = {og['token']}]")
    print()

    # Attempt to delete the target that is used in an observing group
    try:
        target_api.delete(target['token'])
    except Exception as e:
        print(f'Target delete failed - {e}')
        print()

    # Delete the new (unobserved) OG
    api_request(f"observing-groups/{og['token']}", method='DELETE')
    print(f"Deleted observing group OG{og['label']} [token = {og['token']}]")
    print()

    # Delete the new (unobserved) target
    target_api.delete(target['token'])

    # List exposures
    response = api_request(f'/programs/{program_token}/exposures')
    print(f'All exposures for {program_token}:')
    for exp in response['exposure']:
        print(f"{exp['obsid']} "
              f"(OG{exp['observing_group_context']['observing_group_label']}, "
              f"{exp['target_data']['name']})")
    print()
    print()

### DD adds: Small and focused:

def get_target_list_example(program_token, instrument=INSTRUMENT):
    """
    Example to get the target list
    """
    try:
        response = api_request(f'/programs/{program_token}/targets')
    except Exception as e:
        print('API request to get list targets failed')
        
    print(f'All targets for {program_token}:')
    for target in response['entity']:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

def get_target_list_api_example(program_token, instrument=INSTRUMENT):
    """
    Example to get the target list
    """
    try:
        print(f'Running through target API examples for {program_token}...')
        print()
        target_api = EntityCrudApi(program_token, 'targets')
        targets = target_api.list()
        response = api_request(f'/programs/{program_token}/targets')
    except Exception as e:
        print('API request to get list targets failed')
        
    print(f'All targets for {program_token}:')
    for target in response['entity']:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

def get_ot_list_example(program_token, instrument=INSTRUMENT):
    """
    Example to get the list of OTs.
    """
    try:
        response = api_request(f'/programs/{program_token}/observing-templates')
    except Exception as e:
        print(f"Problems getting OTs for program {program_token} on {instrument}")
    print(f'All observing templates for {program_token}:')
    for ot in response['observing_template']:
        print(f"OT{ot['label']} - {ot['name']} [token = {ot['token']}]")
    print()

def get_og_list_example(program_token, instrument=INSTRUMENT):
    """
    Example to get the list of OTs.
    """
    try:
        response = api_request(f'/programs/{program_token}/observing-groups')
    except Exception as e:
        print()
    print(f'All observing groups for {program_token}:')
    for og in response['observing_group']:
        print(f"OG{og['label']} {og['time_accounting']['time_accounting_status']} Requested: {og['subTotals']['etime']['requested']} Observed: {og['subTotals']['etime']['observed']}")
    print()

def get_exposure_list_example(program_token, instrument=INSTRUMENT):
    """
    Example to get the list of exposures
    """
    response = api_request(f'/programs/{program_token}/exposures')
    print(f'All exposures for {program_token}:')
    for exp in response['exposure']:
        print(f"{exp['obsid']} OG{exp['observing_group_context']['observing_group_label']}")
        #print(f"{exp['obsid']} (OG{exp['observing_group_context']['observing_group_label']}, {exp['target']['name']})")
    print()

def process_options():
    """
        Assigns optional arguments when running the script.

        Parameters: None.
        Returns: Nothing.
    """
    global access_token, verbose, api_url, examples

    parser = argparse.ArgumentParser(description="This script shows examples of using the Kealahou API for PI program management.")

    # Check for token file.
    parser.add_argument('--token_file', '-t',
                    required=False,
                    type=str,
                    default=KEY_FILE,
                    help=f"The path to the file that contains a user access token (default {KEY_FILE})")
    
    # Ability to change api urls
    parser.add_argument('--api_url', '-a',
                    required=False,
                    type=str.lower,
                    default=BASE_URL,
                    help=f"The path to the file that contains a user access token (default {BASE_URL}).")
    
    # Run a list of the examples.
    parser.add_argument('--example', '-e',                    
                    required=False,                    
                    choices=[1,2,3,4],
                    default=4,
                    type=int,
                    help='Options for specific examples: Choose integer: 1 - Pointing Offeset 2 - List Programs 3 - Show Targets 4 - Show all examples')
    
    # verbose output.
    parser.add_argument('--verbose', '-v',
                    action='store_true',
                    help='Enable verbose ou0put. This will print out formatted JSON.')

    args = parser.parse_args()
    
    # Load access token
    try:
        with open(args.token_file, 'r') as file_read:
            access_token = file_read.read().strip()
    except OSError:
        print(f"Failed to load API access token file: {args.token_file}. Check path and file permissions.")
        exit(1)

    verbose = args.verbose
    api_url = args.api_url
    example = args.example

def read_tests(program_token,instrument=INSTRUMENT):
    print(f"Get the list of targets for program {program_token} using {instrument}")
    try:
        return get_target_list_example(program_token,instrument=INSTRUMENT)
    except Exception as e:
        print(f"Problem getting target list for {program_token} on {instrument}")
    # print(f"Get the list of OTs.")
    try:
        get_ot_list_example(program_token,instrument=INSTRUMENT)
    except Exception as e:
        print(f"Problem getting OTs for {program_token}")
    print(f"Get the list of exposures")
    try:
        get_exposure_list_example(program_token,instrument=INSTRUMENT)
    except Exception as e:
        print(f"Problem getting exposures for {program_token} using {instrument}")
    print(f"Get observing groups")
    try:
        get_og_list_example(program_token,instrument=INSTRUMENT)
    except Exception as e:
        print(f"Problem getting OGs for {program_token} using {instrument}")

def main():
    process_options()
    # List programs
    response = api_request('programs')
    # for program in response['entity']:
    #     program_data = program['program_data']
    #     program_token = program_data['token']
    #     instrument = program_data['time_allocation'][0]['instrument']
    #     #target_api_examples(program_token, instrument)
    #     #k2_example_walkthrough(program_token, instrument)

    # Attempt to delete an observed target
    # try:
    #     api_request(f"targets/25BE25-1758314224958", method='DELETE')
    # except Exception as e:
    #     print(f'Target deletion failed - {e}')
    #     print()

    # # Attempt to delete an observed observing group
    # try:
    #     api_request(f"observing-groups/25BE25-1758314360503", method='DELETE')
    # except Exception as e:
    #     print(f'Observing group deletion failed - {e}')
    #     print()

    print(json.dumps(response, indent=4, sort_keys=True))
    # programs = response['entity']
    # for program in programs:
        # print(f"Title: {program['program_data']['title']}")
        # print(f"Program ID: {program['program_data']['token']}")
        # print(f"Instrument: {program['program_data']['time_allocation'][0]['instrument']}")
        # print(f"Time allocated: {program['program_data']['time_allocation'][0]['time_allocated_millis']/(1000*3600)} hours")
        # print()
        # print('Performing read tests')
        # read_tests(program['program_data']['token'],program['program_data']['time_allocation'][0]['instrument'])
        # # print(f"Performing write tests")
        # # writetests(program['program_data']['token'],program['program_data']['time_allocation'][0]['instrument'])
        # print(f"============================")

if __name__ == '__main__':
    main()

