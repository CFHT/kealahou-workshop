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
versbose = False
example = 0

example_list = { 
            1: 'List Pointing Offesets', 
            2: 'List Programs',
            3: 'Show Targets',
            4: 'Show All Examples'
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

def get_program_list_example():
    """
    Simple API example to list programs

    Prints JSON attributes
    """
    # List programs
    response = api_request('programs')
    programs = response['entity']
    for program in programs:
        print(f"Title: {program['program_data']['title']}")
        print(f"Program ID: {program['program_data']['token']}")
        print(f"Instrument: {program['program_data']['time_allocation'][0]['instrument']}")
        print(f"Time allocated: {program['program_data']['time_allocation'][0]['time_allocated_millis']/(1000*3600)} hours")        
        print("#" * 80)

    # Print JSON if verbose
    if (verbose):
        print(json.dumps(response, indent=4, sort_keys=True))
        
def get_pointing_offset_example():
    """
    Simple API example to list offsets for each instrument

    Prints JSON attributes
    """
    global INSTRUMENT
    
    # Check for offsets in each instrument and print out.
    for instrument_name in get_args(INSTRUMENT):
        response = api_request('pointing_offset', data={                
                'instrument': instrument_name
                })
        offsets = response['entity']
        
        for offset in offsets:
            if ('ra_offset' in offset['offset'] and 'dec_offset' in offset['offset']):
                print(f"Offset: Ra offset: {offset['offset']['ra_offset']} Dec offset: {offset['offset']['dec_offset']}")
                print("#" * 80)

            
    if (verbose):
        print(json.dumps(response, indent=4, sort_keys=True))


def process_options():
    """
        Assigns optional arguments when running the script.

        Parameters: None.
        Returns: Nothing.
    """
    global access_token, verbose, api_url, example

    parser = argparse.ArgumentParser(description="This script shows examples of using the Kealahou API for PI program management.",
                                     formatter_class=argparse.RawTextHelpFormatter)

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
                    help='Options for specific examples. Choose integer:\n'+
                          '\t1 - List Pointing Offesets \n'+
                          '\t2 - List Programs \n'+
                          '\t3 - Show Targets \n'+
                          '\t4 - Show all examples\n'
                          )
    
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

def main():
    process_options()
    
    print(f"Show example: {example_list[example]}")
    match example:
        case 1:
            get_program_list_example()
        case 2:
            get_pointing_offset_example()
        case 4:
            get_program_list_example()
            get_pointing_offset_example()
        case _:
            print(f"Unkown Option: {example}.")
    
if __name__ == '__main__':
    main()

