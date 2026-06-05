import json

from . import config
from .api import api_request


def get_exposure_list_example(program_token: str):
    """
    Example API call to get the list of exposures

    Parameters:
        program_token: str The token of the select program.
        instrument: A constant string (i.e., MEGACAM).
    Returns:
        Nothing
    """
    response = api_request(f'/programs/{program_token}/exposures')
    print(f'All exposures for {program_token}:')
    for exp in response['exposure']:
        s = (
            f"Exposure ID: {exp['obsid']} OG{exp['observing_group_context']['observing_group_label']}, "
            f"Target: {exp['target_data']['name']}, "
            f"Filter: {exp['exposure_status']['megacam_status']['actual_filter']}, "
            f"IQ: {exp['exposure_status']['megacam_status']} "
            # f"IQ: {exp['exposure_status']['megacam_status']['elixir_processing_result']['sky_background']} "
        )
        print(s)
        if config.verbose:
            print(json.dumps(exp, indent=4))
    print()


