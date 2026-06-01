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
import sys

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
            5: 'Delete a target',
            6: 'Show Observing Groups',
            7: 'Add Observing Groups',
            8: 'Delete Observing Groups',
            9: 'Show observing templates',
            10: 'Show exposures taken'
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
                    choices=[1,2,3,4,5,6,7,8,9,10],
                    default=None,
                    type=int,
                    help='Options for specific examples. Choose integer:\n'+
                          '\t1 - List Programs \n'+
                          '\t2 - List default MegaCam Pointing Offsets \n'+
                          '\t3 - Show Targets \n'+
                          '\t4 - Add a new targets\n'+
                          '\t5 - Delete a target\n'+
                          '\t6 - Show Observing Groups\n'+
                          '\t7 - Add Observing Groups\n'+
                          '\t8 - Delete Observing Groups\n'+
                          '\t9 - Show observing templates\n'+
                          '\t10 - Show exposures taken\n'
                          )
    
    # verbose output.
    parser.add_argument('--verbose', '-v',
                    action='store_true',
                    help='Enable verbose output. This will print out JSON attributes for each particular example.')

    parser.add_argument('--vverbose', '-vv',
                    action='store_true',
                    help='Enable enhanced verbose output. This will print out JSON attributes of the entire response.')    

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
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

def example_fixed_target(program_token: str, instrument: INSTRUMENT):
    """
    Obtain a single Fixed Target based on the Program Token
    
    Parameters:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).

    Returns: Formatted json to be used in an API call for a single fixed target.
    """
    
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
        'magnitude': {'AB' if instrument == 'MEGACAM' else 
                      'H' if instrument == 'SPIROU' else 
                      'V' if instrument == 'ESPADONS' else 0: {'value': 25.0}
        },
        'temperature_effective': 1234.5,
        'standard_star': False,
        'pointing_offset_token': f'00AZ00-PO+{instrument}+1',
    }
    
def example_og(program_token,instrument,target=None,observing_template=None):
    if target is None or observing_template is None:
        print(f"An observing template and a target needs to be provided for OG creation for program {program_token} on instrument {instrument}")
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

def delete_target(program_token, target_name, target_token):
    """

    Deletes the latest based on the token token and name.
    
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
    
            
def delete_target_example(program_token,instrument):
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
    
    delete_target(program_token,deleted_target['name'],deleted_target['token'] )
    
    if verbose or vverbose:
        for i,target in enumerate(target_api.list()):
            print(f"Target {i}")
            print(target)
            print()
    
def set_target_example(program_token: str, instrument: INSTRUMENT, moving_target=False):
    """

    Creates a target based on the program token and instrument.  Also type of targe
    fixed or moving taget.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
        moving_target: Boolean. True creates moving. False is fixexd.
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

def get_target_list_example(program_token,instrument):
    """
    Prints a target list from a single program.

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).

    Returns: json Target response entity.
    """

    print(f"Attempting to display Target List for Program ID: {program_token} with {instrument}")    

    try:
        response = api_request('programs')        
        programs = response['entity']        
        target_response = api_request(f'/programs/{program_token}/targets')
    except Exception as e:
        print(f"API request to get list targets failed: {e}")
        exit()
                
    print(f'All targets for {program_token}:')
    for target in target_response['entity']:
        print(f"T{target['label']} - {target['name']} [token = {target['token']}]")
        if verbose:            
            print(f"API target keys/values")
            print(f"{json.dumps(target_response['entity'],indent=4, sort_keys=True)}")
    print("#" * 80)

    if (vverbose):
        print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")    

    return target_response['entity']

def get_target_example(program_token,instrument,idx=0):
    return get_target_list_example(program_token, instrument)[idx]

def get_program_list_example(output=True):
    """
    Simple API example to list programs

    Prints or return JSON attributes

    Params: output - Boolean True prints out program info.
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
            
            if (verbose):
                print(f"API program keys/values:")
                print(f"Program {program['program_data']['token']}: {json.dumps(program['program_data'],indent=4,sort_keys=True)}")
    
        # Print JSON if verbose
        if (vverbose):
            print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")
    
    return programs
        
def get_megacam_default_pointing_offset_example():
    """
    Simple API example to list pointing offsets for MEGACAM

    Prints JSON attributes
    """
    intrument = 'MEGACAM'
    response = api_request('pointing_offset', data={                
            'instrument': intrument
            })
    
    offsets = response['entity']

    if (offsets):
        print(f"Pointing Offsets for {intrument} below:")
        for offset in offsets:
            print(offset)
    else:
        print(f"No default pointing offsets found.")

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
        
    for og in ogs['observing_group']:
        print(f"OG{og['label']}, OG priority: {og['og_priority']}")
        if verbose or vverbose:
            print(json.dumps(og, indent=4))
            print()
    return ogs['observing_group']
    
def get_first_program_example(idx=0):
    """
    Grabs program information based on the index number
    and returns it as separate variables.

    Returns:     
        program_id - The program identification 
        instrument - The name of the instrument (see constant).
    """


    programs = get_program_list_example(output=False)
    program_id,instrument = None, None
        
    if (len(programs) > 0):
        program = programs[idx]['program_data']
        program_id = program['token']
        instrument = program['time_allocation'][0]['instrument']
    
    return program_id,instrument

def set_og_example(program_token,instrument,target=None,observing_template=None):
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
    new_og = example_og(program_token,instrument,target,observing_template)
    response = api_request(f"programs/{program_token}/observing-groups/{new_og['token']}", method='PUT', data={
        'observing_group': new_og,
    })
    og = response['observing_group']
    print(f"Created observing group OG{og['label']} [token = {og['token']}] for program {program_token} using {instrument}")    

def get_ot_list_example(program_token):
    """
    API call prints Observing Templates based 
    Params:
        program_token: str The token of the select program.        
    Returns:
        Nothing
    """
    response = api_request(f'programs/{program_token}/observing-templates')
    print(f'All observing templates for {program_token}:')
    for ot in response['observing_template']:
        print(f"OT{ot['label']} - {ot['name']} [token = {ot['token']}]")
        if verbose:
            print(json.dumps(ot,indent=4,sort_keys=True))
    print()
    
    ot_out = response['observing_template'][0]
    
    return ot_out

def get_exposure_list_example(program_token: str, instrument: INSTRUMENT):
    """
    Example API call to get the list of exposures

    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    response = api_request(f'/programs/{program_token}/exposures')
    print(f'All exposures for {program_token}:')
    for exp in response['exposure']:
        #print(f"{exp['obsid']} (OG{exp['observing_group_context']['observing_group_label']}, {exp['target']['name']})")
        s = (
            f"Exposure ID: {exp['obsid']} OG{exp['observing_group_context']['observing_group_label']}, "
            f"Target: {exp['target_data']['name']}, "
            f"Filter: {exp['exposure_status']['megacam_status']['actual_filter']}, "
            f"IQ: {exp['exposure_status']['megacam_status']} "
            #f"IQ: {exp['exposure_status']['megacam_status']['elixir_processing_result']['sky_background']} "
        )
        print(s)
        if verbose:
            print(json.dumps(exp,indent=4))
    print()

def delete_og_example(program_token,instrument):
    """
    Params:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    ogs = get_og_list_example(program_token)
    og=ogs[-1]
    try:
        api_request(f"observing-groups/{og['token']}", method='DELETE')
        print(f"Deleted observing group OG{og['label']} [token = {og['token']}]")
    except Exception as e:
        print(f"Target deletion failed")
    print()

def main():
    process_options()  
    print("#" * 80)
    print(f"Chosen example: {example_list[example]}")
    print("#" * 80)

    # Used examples higher than 1: Get Program List.
    program_id,instrument = get_first_program_example(0)    

    # Exit if there is no programs to conduct furether examples.
    if (example > 2 and program_id == None):
        print(f"No Programs found. Cannot execute example: {example_list[example]}")
        exit(0)
    
    # Execute API call based on option chosen.
    match example:
        case 1:
            get_program_list_example()
        case 2:
            get_megacam_default_pointing_offset_example()
        case 3:
            get_target_list_example(program_id,instrument)
        case 4:
            set_target_example(program_id,instrument,moving_target=True)
        case 5:
            delete_target_example(program_id,instrument)
        case 6:
            get_og_list_example(program_id)
        case 7:
            set_og_example(program_id,instrument,get_target_example(program_id,instrument,2),get_ot_list_example(program_id))
        case 8:
            delete_og_example(program_id,instrument)
        case 9:
            get_ot_list_example(program_id);
        case 10:
            get_exposure_list_example(program_id,instrument)
        case _:
            print(f"Unkown Option: {example}.")
    
if __name__ == '__main__':
    main()