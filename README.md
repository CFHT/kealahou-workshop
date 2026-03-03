# Kealahou API Workshop

## Kealahou Development Details

### Kealahou Staging (Test) Environment

Web UI URL: **https://hou-stage.cfht.hawaii.edu**

API URL: **https://api-stage.cfht.hawaii.edu**

### AEON+ Test Account

This account can be used to test API interactions:
- User: `aeontest`
- Password: *[see CFHT staff]*

### Program IDs

The test account has full access to the following science programs:

- 25BE25
  - MegaCam (imaging instrument)
  - Existing target data
  - Existing observing template (OT) data
  - Existing observing group (OG) data
  - Existing exposure data
- 25BE30
  - SPIRou (spectrograph)
  - Existing observing template (OT) data

## Kealahou API

### Access Token

An access token can be used to allow programmatic access to the API without potentially surfacing your password.
These can be generated on the [Manage Tokens](https://hou-stage.cfht.hawaii.edu/account/token-manager) page.
Note that the token will only be visible to you when you first generate it, so make sure to save it somewhere secure.

The examples in this project will assume this token has been saved into a file in this directory named `.access_token`.

### User Workflow

1. A user is granted time on CFHT through the standard CFHT TAC process, or through DDT.
2. The user creates an API access token, unless they have an existing one.
3. The user pre-configures the Observing Templates within the K2 interface for their observing program.
4. The user enters their observation into AEON, which submits target and Observing Group data through the Kealahou API.
5. This observation is executed by CFHT.

### Current Documentation

A Swagger page of the completed API endpoints is available in the project: [api.swagger.json](api.swagger.json).

The original [proto files](proto) can also be viewed for a more direct view of documentation for each field.

### Full API Documentation (Under Construction)

URL: **https://swagger-stage.cfht.hawaii.edu/**

Note, the API is undergoing ongoing cleanup and improvements.
This should be considered a preview version, where any and all pieces are subject to change.

### API Usage Examples

To run these examples yourself, make sure to set up an access token first, as described [above](#Access-Token).

There are some brief examples of accessing the API using cURL in [curl_examples.md](curl_examples.md).

For a more thorough example of walking through the steps of using the API, in Python, see [example.py](example.py).
