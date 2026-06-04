import json
import sys

from .api import api_request
from .config import verbose, vverbose


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
            print(
                f"Time allocated: {program['program_data']['time_allocation'][0]['time_allocated_millis'] / (1000 * 3600)} hours")
            print("-" * 80)

            if verbose:
                print(f"API program keys/values:")
                print(
                    f"Program {program['program_data']['token']}: {json.dumps(program['program_data'], indent=4, sort_keys=True)}")

        # Print JSON if verbose
        if vverbose:
            print(f"Response: {json.dumps(response, indent=4, sort_keys=True)}")

    return programs


def get_first_program_example(idx=0):
    """
    Grabs program information based on the index number
    and returns it as separate variables.

    Returns:
        program_id - The program identification
        instrument - The name of the instrument (see constant).
    """
    programs = get_program_list_example(output=False)

    if len(programs) <= idx:
        print(f'Not enough programs in list. Found {len(programs)}, need at least {idx + 1}.')
        sys.exit()

    program = programs[idx]['program_data']
    program_id = program['token']
    instrument = program['time_allocation'][0]['instrument']

    return program_id, instrument
