# Kealahou Workshop

## Kealahou API Examples
There are some brief examples of accessing the API using cURL in [curl_examples.md](curl_examples.md).

For a more thorough example of walking through the steps of using the API, in Python, see [example.py](example.py).

To run the examples yourself, make sure to set up an access token first,
as described [below](#Access-Token).

## Kealahou Development Details

### Kealahou Staging (Test) Session

URL: **[https://hou-stage.cfht.hawaii.edu](https://hou-stage.cfht.hawaii.edu)**

API URL: **https://api-stage.cfht.hawaii.edu**

### API Documentation

URL: **[https://swagger.cfht.hawaii.edu](https://swagger.cfht.hawaii.edu)**

Note, the API is undergoing ongoing cleanup and improvements.
This should be considered a preview version, where any and all pieces are subject to change.

- `/programs/lite` endpoint not listed in the docs, lists a user's programs. (Plan to move it to `/programs`.)


### Test Account:

- User: `aeontest`
- Password: *[see CFHT staff]*
- Access Token: *see [below](#Access-Token)*

This account can be used to test API interactions. See examples above.

### Access Token

An access token can be used to allow programmatic access to the API without potentially surfacing your password.
These can be generated on the [Manage Tokens](https://hou-stage.cfht.hawaii.edu/account/token-manager) page.
Note that the token will only be visible to you when you first generate it, so make sure to save it somewhere secure.

### Program IDs

- 25BE25 (MegaCam, imaging instrument)
- 25BE30 (SPIRou, spectrograph)

There is existing target and observing template (OT) data in both programs. 25BE25 also has observing group (OG) and exposure data.
Note that the API endpoint for the program list is not currently available in the API documentation. See [above](#API-Documentation).

## Questions for the AEON/LCO Team

"Do we automatically trigger the creation of OGs (the encapsulated observation construct), or have a UI on the AEON side for this? How do other observatories handle this for AEON?"

"Do we need to store any AEON-specific target or observation metadata that is not already included in Kealahou?"

"Are there any concerns about how our token-based authentication scheme would match up with their UI, and also about how multi-program users are handled at other observatories – does AEON have a scheme for such cases?"

"Regarding error-handling - does AEON have a preferred method of doing so, or specific implementations, protocols, and/or syntax they require?"