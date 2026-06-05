import json
import sys

from example import INSTRUMENT
from . import config
from .api import api_request


def get_program_list_example():
    """
    Simple example listing all programs belonging to the user
    """
    response = api_request('programs')
    programs = response['entity']

    print("Displaying program list")
    print("#" * 80)

    # List programs
    for program in programs:
        program_data = program['program_data']
        primary_allocation = program_data['time_allocation'][0]
        print("#" * 80)
        print(f"Title: {program_data['title']}")
        print(f"Program ID: {program_data['token']}")
        print(f"Instrument: {primary_allocation['instrument']}")
        print(f"Time allocated: {primary_allocation['time_allocated_millis'] / (1000 * 3600)} hours")
        print("-" * 80)

        if config.verbose:
            print(f"Program data:")
            print(f"Program {program_data['token']}: {json.dumps(program_data, indent=4)}")


def get_first_program_example(idx=0) -> tuple[str, INSTRUMENT]:
    """
    Grabs program information based on the index number
    and returns the program's token and instrument.

    Returns:
        program_token - The program token
        instrument - The name of the instrument
    """
    response = api_request('programs')
    programs = response['entity']

    if len(programs) <= idx:
        print(f'Not enough programs in list. Found {len(programs)}, need at least {idx + 1}.')
        sys.exit()

    program = programs[idx]['program_data']
    program_token = program['token']
    instrument = program['time_allocation'][0]['instrument']

    return program_token, instrument
