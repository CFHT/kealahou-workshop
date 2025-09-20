For the below examples we will use the following tools:
* `curl` - To perform HTTP requests
* `jq` - To format/parse JSON responses

### HTTP headers
For the below examples, since we will be using `curl` to do HTTP requests with JSON data,
we will set up a header file to avoid retyping the same boilerplate for each query:

Create a file named `.kealahou_headers` with the following contents:
```name
Content-Type: application/json
Authorization: Bearer 12345678-90ab-cdef-1234-567890abcdef"
```
(Replace with your actual access token.)

## Program Management API
This is the API used by PIs to manage their programs.
The K2 web interface uses this under the hood to get and set data.

### Targets

List all targets for a program:
```
curl --header @.kealahou_headers -X GET https://api-stage.cfht.hawaii.edu/programs/23AQ78/targets | jq
```

List all fixed targets for a program:
```
curl --header @.kealahou_headers -X GET --data "{target_type: FIXED}" https://api-stage.cfht.hawaii.edu/programs/23AQ78/targets | jq
```

List a single target for a program:
```
curl --header @.kealahou_headers -X GET https://api-stage.cfht.hawaii.edu/programs/23AQ78/targets/23AQ78-56301200080000295183 | jq
```
