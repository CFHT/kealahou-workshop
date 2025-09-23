# kealahou-workshop

## Kealahou API Examples

[TBD]

## Kealahou Development Details

### Kealahou Staging (Test) Session

URL: **[https://hou-stage.cfht.hawaii.edu](https://hou-stage.cfht.hawaii.edu)**

### API Documentation

URL: **[https://swagger.cfht.hawaii.edu](https://swagger.cfht.hawaii.edu)**

### Test Account:

- User: `aeontest`
- Password: *[see CFHT staff]*
- Access Token: *[see CFHT staff]*

This account can be used to test 'get' and 'put' API interactions. See examples above.

### Program IDs: 

- 25BE25 (MegaCam, imaging instrument) 
- 25BE30 (SPIRou, spectrograph)

There is existing target and observing template (OT) data in both programs. 25BE25 also has observing group (OG) and exposure data. 
Note that the API endpoint for the program list is not currently available in the API documentation. See CFHT staff for details. 

## Questions for the AEON/LCO Team

"Do we automatically trigger the creation of OGs (the encapsulated observation construct), or have a UI on the AEON side for this? How do other observatories handle this for AEON?"

"Do we need to store any AEON-specific target or observation metadata that is not already included in Kealahou?"

"Are there any concerns about how our token-based authentication scheme would match up with their UI, and also about how multi-program users are handled at other observatories – does AEON have a scheme for such cases?"

"Regarding error-handling - does AEON have a preferred method of doing so, or specific implementations, protocols, and/or syntax they require?"