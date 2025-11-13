'''
Examples of using the Kealahou API for PI program management.
All API interactions in these examples should be considered as non-final design, and subject to change.

An access token is necessary to run these examples. See the README for details.

Note that, for real world usage, a library such as requests (https://requests.readthedocs.io/)
is better suited for submitting HTTP requests than the stock Python urllib.
'''

import json
import random
from typing import Literal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

KEY_FILE = '.access_token'
BASE_URL = 'https://api-stage.cfht.hawaii.edu'

INSTRUMENT = Literal['SPIROU', 'ESPADONS', 'MEGACAM']

required_mag_by_instrument: dict[INSTRUMENT, str] = {
    'SPIROU': 'H',
    'ESPADONS': 'V',
    'MEGACAM': 'AB',
}

# Load access token
try:
    with open(KEY_FILE, 'r') as file_read:
        access_token = file_read.read().strip()
except OSError:
    print('Failed to load API access token')
    raise


'''
Submit a request to the Kealahou API, and condense any errors into a consistent error message format.
'''
def api_request(endpoint, data=None, method='GET'):
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
        response = json.loads(e.read().decode('utf-8'))
    else:
        response = json.loads(raw_response.read().decode('utf-8'))

    if response.get('success'):
        return response
    elif response.get('error') and response['error']['messages']:
        if http_error:
            raise Exception(f"API request failed ({http_error}): {', '.join(response['error']['messages'])}")
        else:
            raise Exception(f"API request failed: {', '.join(response['error']['messages'])}")
    elif http_error:
        raise Exception(f"API request failed ({http_error})")
    else:
        raise Exception('API request failed, but no error message was given')


def k2_example_walkthrough(program_token: str, instrument: INSTRUMENT):
    print(f'Program {program_token} ({instrument})')
    print()

    # List observing templates
    response = api_request(f'/programs/{program_token}/observing-templates')
    print(f'All observing templates for {program_token}:')
    for ot in response['observing_template']:
        print(f"OT{ot['label']} - {ot['name']} [token = {ot['token']}]")
    print()
    first_ot = response['observing_template'][0]  # Save for later example

    # List targets
    response = api_request(f'programs/{program_token}/targets')
    print(f'All targets for {program_token}:')
    for target in response['target']:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

    # Invalid new target data
    new_target = {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'My new fancy target!',
        'fixed_target': {
            'coordinate': {
                'ra': 'twenty point seven degrees',  # Wrong type!
                'dec': random.uniform(-90, 90),
            },
            'proper_motion': {},
        },
        'target_magnitudes': {
        },
        'reference_equinox_julian_years': 2000.0,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }

    # Attempt to create invalid target
    try:
        print('Trying to create target...')
        api_request(f"programs/{program_token}/targets/{new_target['token']}", method='PUT', data={
            'target': new_target,
        })
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Correct bad format, but new value is out of range
    new_target['fixed_target']['coordinate']['ra'] = 2220.7

    # Attempt again with out-of-range value
    try:
        print('Trying to create target...')
        api_request(f"programs/{program_token}/targets/{new_target['token']}", method='PUT', data={
            'target': new_target,
        })
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Correct value
    new_target['fixed_target']['coordinate']['ra'] = 20.7

    # Attempt again, only missing instrument-specific fields
    try:
        print('Trying to create target with instrument validation...')
        api_request(f"programs/{program_token}/targets/{new_target['token']}", method='PUT', data={
            'target': new_target,
            'instrument': instrument,  # Specify instrument to perform extra validation checks
        })
    except Exception as e:
        print(f'Target creation failed - {e}')
        print()

    # Add instrument-specific data
    new_target['target_magnitudes'] = {
        required_mag_by_instrument[instrument]: {
            'value': 10.0,
        },
    }

    # Successfully create new target
    response = api_request(f"programs/{program_token}/targets/{new_target['token']}", method='PUT', data={
        'target': new_target,
        'instrument': instrument,  # Specify instrument to perform extra validation checks
    })
    target = response['target']
    print(f"Created target T{target['label']} - {target['name']} [token = {target['token']}] "
          f"(version={target['version']})")
    print()

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

    # Update target
    update_target = target
    update_target['standard_star'] = True
    response = api_request(f"programs/{program_token}/targets/{update_target['token']}", method='PUT', data={
        'target': update_target,
        'lock_version': {
            'value': update_target['version'],  # Use version-locking to prevent accidental overwrites
        },
        'instrument': instrument,  # Specify instrument to perform extra validation checks
    })
    target = response['target']
    print(f"Updated T{target['label']} - {target['name']} [token = {target['token']}]  (version={target['version']})")
    print()

    # Fetch single target
    response = api_request(f"programs/{program_token}/targets/{new_target['token']}")
    target = response['target']
    print(f"Fetched T{target['label']} - {target['name']} [token = {target['token']}] (version={target['version']})")
    print()

    # Delete the new (unobserved) OG
    api_request(f"observing-groups/{og['token']}", method='DELETE')
    print(f"Deleted observing group OG{og['label']} [token = {og['token']}]")
    print()

    # Delete the new (unobserved) target
    api_request(f"targets/{target['token']}", method='DELETE')
    print(f"Deleted target T{target['label']} - {target['name']} [token = {target['token']}]")
    print()

    # Attempt to delete observed target
    try:
        api_request(f"targets/25BE25-1758314224958", method='DELETE')
    except Exception as e:
        print(f'Target deletion failed - {e}')
        print()

    # Attempt to delete observed observing group
    try:
        api_request(f"observing-groups/25BE25-1758314360503", method='DELETE')
    except Exception as e:
        print(f'Observing group deletion failed - {e}')
        print()

    # List exposures
    response = api_request(f'/programs/{program_token}/exposures')
    print(f'All exposures for {program_token}:')
    for exp in response['exposure']:
        print(f"{exp['obsid']} (OG{exp['observing_group_context']['observing_group_label']}, {exp['target']['name']})")
    print()

# List programs
response = api_request('programs/lite')
for program in response['entity']:
    program_data = program['program_data']
    program_token = program_data['token']
    instrument = program_data['time_allocation'][0]['instrument']
    k2_example_walkthrough(program_token, instrument)
