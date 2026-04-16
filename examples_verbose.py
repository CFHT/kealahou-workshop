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
from typing import Literal, get_args
from urllib.error import HTTPError
from urllib.request import Request, urlopen

KEY_FILE = '.access_token'
BASE_URL = 'https://api-stage.cfht.hawaii.edu'

INSTRUMENT = Literal['SPIROU', 'ESPADONS', 'MEGACAM']
access_token = None
verbose = False
vverbose = False
example = 0

example_list = { 
            1: 'List Programs',
            2: 'List MegaCam default Pointing Offsets',
            3: 'Show Targets',
            4: 'Add a target',
            5: 'Create an OG'
            #4: 'Show All Examples'
        }

required_mag_by_instrument: dict[INSTRUMENT, str] = {
    'SPIROU': 'H',
    'ESPADONS': 'V',
    'MEGACAM': 'AB',
}

def api_request(endpoint, data=None, method='GET'):
    """
    Submit a request to the Kealahou API, and condense any errors into a consistent error message format.

    Params:
    endpoint - String Added to the API url
    data - JSON for additional variables.
    method - Default GET, but also available for POST and DELETE.

    Returns:
        response as JSON format.
    """

    if data is None:
        data = {}
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    url = f'{BASE_URL}/{endpoint}'

    if (verbose) or (vverbose):        
        print(f"Request\n full URL: {url}")
        print(f"Data: {data}")
        print(f"Headers: {headers}")
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
        self.path_prefix = f'programs/{program_token}/{entity_type}'

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

def example_fixed_target(program_token: str, instrument: INSTRUMENT):
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'DD target 1',
        'fixed_target': {
            'coordinate': {
                'ra': random.uniform(0, 359.9999), #Values are in decimal degrees.
                'dec': random.uniform(-90, 90),
            },
            'proper_motion': {'ra_mas': -15.468, 'dec_mas': 12.5},
            'estimated_radial_velocity_kmps': {'value': 234.0} if instrument == 'SPIROU' else None,
        },
        'magnitude': {'AB' if instrument == 'MEGACAM' else 
                      'H' if instrument == 'SPIROU' else 
                      'V' if instrument == 'ESPADONS' else 0: {'value': 25.0}
        },
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }

def example_moving_target(program_token: str, instrument: INSTRUMENT):
    return {
        'token': f'{program_token}-{random.randint(1000000000, 9999999999)}',
        'name': 'DD moving target 1.',
        'moving_target': {
            'ephemeris_point': [{
                'mjd': 61041.0 + i,
                'coordinate': {
                    'ra': random.uniform(0, 359.9999),
                    'dec': random.uniform(-90, 90),
                },
            } for i in range(0, 5)],
        },
        'magnitude': {'AB' if instrument == 'MEGACAM' else 
                      'H' if instrument == 'SPIROU' else 
                      'V' if instrument == 'ESPADONS' else 0: {'value': 25.0}
        },
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }
    
def delete_target_example():
    target_api = EntityCrudApi(program_token, 'targets')
    target_api.create_or_update(new_target)
    
def set_target_example(program_token: str, instrument: INSTRUMENT, moving_target=False):
    target_api = EntityCrudApi(program_token, 'targets')
    if moving_target:
        new_target = example_moving_target(program_token, instrument)
    else:
        new_target = example_fixed_target(program_token, instrument)
    try:
        target_api.create_or_update(new_target)
        print(f"Target created.")
    except Exception as e:
        print(f"Problem adding new target to {program_token} on {instrument} - {e}.")

    if verbose or vverbose:
        print(target_api)

def get_target_list_example():
    """
    Example to get the target list
    """

    print("Displaying Target List")
    print("#" * 80)
    
    response = api_request('programs')
    programs = response['entity']
    for program in programs:
        program_token = program['program_data']['token']
        print(f"Program token {program_token}")
        try:
            tresponse = api_request(f'/programs/{program_token}/targets')
        except Exception as e:
            print('API request to get list targets failed')
            
        print(f'All targets for {program_token}:')
        for target in tresponse['entity']:
            print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
            if verbose:
                print("-" * 80)
                print(f"API target keys/values")
                print(f"{tresponse['entity']}")
        print("#" * 80)

    if (vverbose):
        print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")    

def get_program_list_example(output=True):
    """
    Simple API example to list programs

    Prints or return JSON attributes
    """
    response = api_request('programs')
    programs = response['entity']
    
    if output:
        print("Displaying Program List")
        print("#" * 80)

        # List programs

        for program in programs:
            print("#" * 80)
            print(f"Title: {program['program_data']['title']}")
            print(f"Program ID: {program['program_data']['token']}")
            print(f"Instrument: {program['program_data']['time_allocation'][0]['instrument']}")
            print(f"Time allocated: {program['program_data']['time_allocation'][0]['time_allocated_millis']/(1000*3600)} hours")        
            print("-" * 80)
            print(f"API program keys/values:")
            if (verbose):
                print(f"Program {program['program_data']['token']}: {json.dumps(program['program_data'],indent=4,sort_keys=True)}")
    
        # Print JSON if verbose
        if (vverbose):
            print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")
    
    return programs
        
def get_megacam_default_pointing_offset_example():
    """
    Simple API example to list offsets for each instrument

    Prints JSON attributes
    """
    global INSTRUMENT

    for instrument_name in get_args(INSTRUMENT):
        response = api_request('pointing_offset', data={                
                'instrument': instrument_name
                })
        
        if (instrument_name) == 'MEGACAM':
            offsets = response['entity']
            for offset in offsets:
                print(offset)

        else:
            print(f"No default pointing offsets for {instrument_name}")
        
        # for offset in offsets:
        #     if ('ra_offset' in offset['offset'] and 'dec_offset' in offset['offset']):
        #         print(f"Offset: RA offset: {offset['offset']['ra_offset']} DEC offset: {offset['offset']['dec_offset']}")
        #         #print("#" * 80)
        #         if (vverbose or verbose):
        #             print("-" * 80)
        #             print(f"API MegaCam offset keys/values")
        #             print(offset)
        #             #print(json.dumps(response, indent=4, sort_keys=True))

def process_options():
    """
        Assigns optional arguments when running the script.

        Parameters: None.
        Returns: Nothing.
    """
    global access_token, verbose, vverbose, api_url, example

    parser = argparse.ArgumentParser(description="This script shows examples of using the Kealahou API for PI program management.",
                                     formatter_class=argparse.RawTextHelpFormatter)
                        
    
    # Check for token file.
    parser.add_argument('--token_file', '-t',
                    required=False,
                    type=str,
                    default=KEY_FILE,
                    help=f"The path to the file that contains a user access token (default ./{KEY_FILE})")
    
    # Ability to change api urls
    parser.add_argument('--api_url', '-a',
                    required=False,
                    type=str.lower,
                    default=BASE_URL,
                    help=f"The path to the file that contains a user access token (default {BASE_URL}).")
    
    # Run a list of the examples.
    parser.add_argument('--example', '-e',                    
                    required=False,                    
                    choices=[1,2,3,4,5],
                    default=1,
                    type=int,
                    help='Options for specific examples. Choose integer:\n'+
                          '\t1 - List Programs \n'+
                          '\t2 - List default MegaCam Pointing Offsets \n'+
                          '\t3 - Show Targets \n'+
                          '\t4 - Add a new targets\n'+
                          '\t5 - Create a new OG'
                          )
    
    # verbose output.
    parser.add_argument('--verbose', '-v',
                    action='store_true',
                    help='Enable verbose output. This will print out JSON attributes for each particular example.')

    parser.add_argument('--vverbose', '-vv',
                    action='store_true',
                    help='Enable enhanced verbose output. This will print out JSON attributes of the entire response.')    

    args = parser.parse_args()
    
    # Load access token
    try:
        with open(args.token_file, 'r') as file_read:
            access_token = file_read.read().strip()
    except OSError:
        print(f"Failed to load API access token file: {args.token_file}. Check path and file permissions.")
        exit(1)

    verbose = args.verbose
    vverbose = args.vverbose
    api_url = args.api_url
    example = args.example

def main():
    process_options()  
    print("#" * 80)  
    print(f"Chosen example: {example_list[example]}")
    print("#" * 80)
    match example:
        case 1:
            get_program_list_example()
        case 2:
            get_megacam_default_pointing_offset_example()
        case 3:
            get_target_list_example()
        case 4:
            programs = get_program_list_example(output=False)
            program = programs[3]['program_data']
            progid = program['token']
            instrument = program['time_allocation'][0]['instrument']
            #set_target_example(progid,instrument)
            set_target_example(progid,instrument,moving_target=True)
        case 5:
            pass
        # case 5:
        #     get_program_list_example()
        #     get_pointing_offset_example()
        #     get_target_list_example()
        case _:
            print(f"Unkown Option: {example}.")
    
if __name__ == '__main__':
    main()
