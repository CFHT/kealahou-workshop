# Kealahou API Workshop

The first release of the Kealahou API for integration with the AEON platform consists of the following capabilities: 

* Creation of API access tokens. 
* Querying of a user’s program metadata 
* Creation of a target entity from broker data or manual parameter input.
* Submission of fixed target and moving target data to a user’s program.

The second release, which is expected in the next month, will include the following capabilities:

* Querying of a user’s program’s configured Observing Templates. 
* Creation of Observing Groups, including observation timing information such as observation windows and monitoring parameters.
* Submission of Observing Group data to a user’s program.

Together these releases constitute the **Phase 1** capability of AEON-CFHT integration. **Phase 2** will add support for the creation and submission of Observing Templates. **Phase 3** will add support for Rapid Target of Opportunity (rToO) observations.


### Glossary

**Fixed Target** — an entity consisting of a single position, defined by RA and Dec (ICRS, J2000). Additional metadata includes proper motions, magnitudes, temperatures, and pointing offsets. 

**Moving Target** — an entity consisting of a series of coordinates, each defined by a position (RA and Dec (ICRS, J2000)) and a Modified Julian Date (MJD) timestamp. Additional metadata includes magnitudes, and pointing offsets. 

**Observing Group** — an entity consisting of combinations of target(s) and Observing Template(s). OGs are the entity that are executed on the telescope. Additional metadata includes observation scheduling information and observing strategies. 

**Observing Template** — an entity consisting of the technical instrument configuration and the requested observational constraints. Instrument configuration metadata includes filters, exposure times, dither patterns, signal-to-noise ratios, and guiding setup. Observational constraints include requested image quality (seeing), airmass, sky background, and extinction parameters. 

**Program** — the highest level of the Kealahou entity hierarchy. Users interact with CFHT through their science program, and users must have at least one CFHT science program to submit observations. Technically, a program is an entity consisting of target, Observing Template, Observing Group, and Exposure data. Observation time is allocated on a per-program basis. Each program has a single PI, and may have Co-I. Programs may only have a single instrument associated with it. Scientific objectives which require multiple instruments, will be granted multiple programs. 

## Contact

The CFHT/Kealahou development team can be contacted at <kealahou-api@cfht.hawaii.edu>.

## Kealahou Development Details

Kealahou has both a Production environment and a Staging (Test) environment. For the purposes of AEON integration with the Kealahou API, both environments are identical, however to prevent any potential impact to the Production environment, only the details for the Staging environment are provided in this document. **When the time comes for the final integration with the Production environment, contact the CFHT/Kealahou development staff.** Additionally, user and program data on the Staging environment should not be considered persistent. 

### Kealahou Staging (Test) Environment

Web UI URL: **https://hou-stage.cfht.hawaii.edu**

API URL: **https://api-stage.cfht.hawaii.edu**

### AEON+ Test Account

This account can be used to test API interactions:
- User: `aeontest`
- Password: *[contact CFHT/Kealahou development staff]*

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

### Planned End-User Workflow (Phase 1)

1. A user is granted time on CFHT through the standard CFHT TAC process, or through DDT.
2. The user creates an API access token, unless they have an existing one.
3. The user pre-configures the Observing Templates within the K2 interface for their observing program.
4. The user enters their observation into AEON, which submits target and Observing Group data through the Kealahou API.
5. This observation is executed by CFHT.

### Documentation

A Swagger page of the completed API endpoints is available in the project: [api.swagger.json](api.swagger.json).

The original [proto files](proto) can also be viewed for a more direct view of documentation for each field.

Additionally, a Swagger API documentation site is also available - URL: **https://swagger-stage.cfht.hawaii.edu/**

Please note that some inline documentation for fields in PUT methods is not showing due to a technical issue. Refer to the [proto files](proto) for full details. 

**Disclaimer** 
The API is undergoing ongoing cleanup and improvements.
This should be considered a preview version, where any and all pieces are subject to change.

### API Usage Examples

To run these examples yourself, make sure to set up an access token first, as described [above](#Access-Token).

There are some brief examples of accessing the API using cURL in [curl_examples.md](curl_examples.md).

For a more thorough example of walking through the steps of using the API, in Python, see [example.py](example.py).
