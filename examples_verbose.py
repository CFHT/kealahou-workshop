"""
Examples of using the Kealahou API for PI program management.
All API interactions in these examples should be considered as non-final design, and subject to change.

An access token is necessary to run these examples. See the README for details.
"""

import argparse
import sys

from python_examples import config
from python_examples.exposures import get_exposure_list_example
from python_examples.observing_groups import get_og_list_example, create_og_example, delete_og_example
from python_examples.observing_templates import get_observing_template_list_example, get_observing_template_by_index
from python_examples.programs import get_first_program_example, get_program_list_example
from python_examples.targets import get_megacam_default_pointing_offset_example, get_target_list_example, \
    create_target_example, delete_target_example, get_target_by_index

KEY_FILE = '.access_token'
BASE_URL = 'https://api-stage.cfht.hawaii.edu'

example_list = [
    'List programs',
    'List default pointing offsets for MegaCam',
    'Show targets',
    'Add a target',
    'Delete a target',
    'Show observing groups',
    'Add an observing group',
    'Delete an observing group',
    'Show observing templates',
    'Show exposures taken',
]


def main():
    parser = argparse.ArgumentParser(
        description="This script shows examples of using the Kealahou API for PI program management.",
        formatter_class=argparse.RawTextHelpFormatter)

    example_description = '\n'.join((f'\t{(i + 1):>2} - {desc}' for i, desc in enumerate(example_list)))

    # Check for token file.
    parser.add_argument('--token_file', '-t',
                        required=False,
                        type=str,
                        default=KEY_FILE,
                        help=f"The path to the file that contains a user access token (default ./{KEY_FILE})")

    # Ability to change API urls
    parser.add_argument('--api_url', '-a',
                        required=False,
                        type=str.lower,
                        default=BASE_URL,
                        help=f"The URL for the Kealahou API (default {BASE_URL}).")

    # Run a list of the examples.
    parser.add_argument('--example', '-e',
                        required=False,
                        choices=list(range(1, len(example_list) + 1)),
                        default=None,
                        type=int,
                        help='Run specific example. Select a number:\n' +example_description)

    # verbose output.
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='Enable verbose output. This will print out JSON attributes for each example.')

    parser.add_argument('--vverbose', '-vv',
                        action='store_true',
                        help='Enable enhanced verbose output. This will print out the entire JSON response.')

    args = parser.parse_args()

    # Load access token
    try:
        with open(args.token_file, 'r') as file_read:
            config.access_token = file_read.read().strip()
    except OSError:
        print(f"Failed to load API access token file: {args.token_file}. Check path and file permissions.")
        sys.exit(1)

    config.verbose = args.verbose or args.vverbose
    config.vverbose = args.vverbose
    config.api_url = args.api_url

    if args.example is not None:
        example = args.example
    else:
        print("To run a specific example, select a number (0 to exit):")
        print(example_description)
        try:
            example = int(input("Select an option: "))
        except ValueError:
            print("Invalid option selected")
            sys.exit()
        if example == 0:
            sys.exit()
        elif example < 1 or example > len(example_description):
            print("Invalid option selected")
            sys.exit()

    print("#" * 80)
    print(f"Selected example: {example_list[example - 1]}")
    print("#" * 80)

    if example > 2:
        # Used examples higher than 1: Get Program List.
        program_id, instrument = get_first_program_example(0)

        # Exit if there is no programs to conduct further examples.
        if not program_id:
            print(f"No Programs found. Cannot execute example: {example_list[example - 1]}")
            sys.exit(0)

    # Execute API call based on option chosen.
    match example:
        case 1:
            get_program_list_example()
        case 2:
            get_megacam_default_pointing_offset_example()
        case 3:
            get_target_list_example(program_id)
        case 4:
            create_target_example(program_id, instrument, moving_target=True)
        case 5:
            delete_target_example(program_id)
        case 6:
            get_og_list_example(program_id)
        case 7:
            target_example = get_target_by_index(program_id, 2)
            ot_example = get_observing_template_by_index(program_id, 0)
            create_og_example(program_id, instrument, target_example, ot_example)
        case 8:
            delete_og_example(program_id)
        case 9:
            get_observing_template_list_example(program_id)
        case 10:
            get_exposure_list_example(program_id)
        case _:
            print(f"Unknown option: {example}.")


if __name__ == '__main__':
    main()
