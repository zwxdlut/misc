# flake8: noqa:

import time
import lakefs_client
from lakefs_client.api import objects_api, branches_api
from lakefs_client.model.object_stats_list import ObjectStatsList
from lakefs_client.model.error import Error
from pprint import pprint
# Defining the host is optional and defaults to http://localhost/api/v1
# See configuration.py for a list of all supported configuration parameters.

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basic_auth
configuration = lakefs_client.Configuration(
    host="http://192.168.70.202:30495/api/v1",
    username=None,
    password=None,
)

# Configure API key authorization: cookie_auth
# configuration.api_key['cookie_auth'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['cookie_auth'] = 'Bearer'

# Configure Bearer authorization (JWT): jwt_token
# configuration = lakefs_client.Configuration(
#     access_token='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJsb2dpbiIsImV4cCI6MTY3NzA1MjM4NCwianRpIjoiZjNiMTg0MGMtMzNkMC00ZTcwLWI4MTEtYmU2NTU3Yjg4NTE4IiwiaWF0IjoxNjc2NDQ3NTg0LCJzdWIiOiJhZG1pbiJ9.X5rrLumVOEnqo1lK0Ek6fnPzR8ttVAGhSDoZK6No7ao'
# )

# Configure API key authorization: oidc_auth
# configuration.api_key['oidc_auth'] = 'YOUR_API_KEY'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['oidc_auth'] = 'Bearer'

# Enter a context with an instance of the API client
####################### 列出分支 #####################
with lakefs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = branches_api.BranchesApi(api_client)
    print(api_instance)

    repository = "mxdataset"  # str |
    # str | return items prefixed with this value (optional)
    prefix = ""
    after = ""  # str | return items after this value (optional)
    # int | how many items to return (optional) if omitted the server will use the default value of 100
    amount = 100

    # example passing only required values which don't have defaults set
    try:
        # list branches
        api_response = api_instance.list_branches(repository)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling BranchesApi->list_branches: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list branches
        api_response = api_instance.list_branches(
            repository, prefix=prefix, after=after, amount=amount)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling BranchesApi->list_branches: %s\n" % e)


# Enter a context with an instance of the API client
###################### list_objects #######################
with lakefs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = objects_api.ObjectsApi(api_client)
    repository = "mxdataset"  # str |
    # str | a reference (could be either a branch or a commit ID)
    ref = "main"
    # bool |  (optional) if omitted the server will use the default value of True
    user_metadata = True
    presign = True  # bool |  (optional)
    after = ""  # str | return items after this value (optional)
    # int | how many items to return (optional) if omitted the server will use the default value of 100
    amount = 100
    # str | delimiter used to group common prefixes by (optional)
    delimiter = ""
    # str | return items prefixed with this value (optional)
    prefix = ""

    # example passing only required values which don't have defaults set
    try:
        # list objects under a given prefix
        api_response = api_instance.list_objects(repository, ref)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling ObjectsApi->list_objects: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # list objects under a given prefix
        api_response = api_instance.list_objects(
            # repository, ref, user_metadata=user_metadata, presign=presign, after=after, amount=amount, delimiter=delimiter, prefix=prefix)
            repository, ref, user_metadata=user_metadata, after=after, amount=amount, delimiter=delimiter, prefix=prefix)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling ObjectsApi->list_objects: %s\n" % e)


# Enter a context with an instance of the API client
############################ upload_object #######################################
with lakefs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = objects_api.ObjectsApi(api_client)
    repository = "mxdataset"  # str |
    branch = "main"  # str |
    path = "tox.ini"  # str | relative to the branch
    storage_class = ""  # str |  (optional)
    # str | Currently supports only \"*\" to allow uploading an object only if one doesn't exist yet (optional)
    # if_none_match = "*" #################### 
    # file_type | Only a single file per upload which must be named \\\"content\\\". (optional)
    content = open('./tox.ini', 'rb')

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        api_response = api_instance.upload_object(
            repository, branch, path, storage_class=storage_class, 
            # if_none_match=if_none_match,
              content=content)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling ObjectsApi->upload_object: %s\n" % e)


# Enter a context with an instance of the API client
########################## get_object ######################################
with lakefs_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = objects_api.ObjectsApi(api_client)
    repository = "mxdataset"  # str |
    # str | a reference (could be either a branch or a commit ID)
    ref = "main"
    path = "121.txt"  # str | relative to the ref
    range = "bytes=0-1023"  # str | Byte range to retrieve (optional)
    presign = True  # bool |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # get object content
        api_response = api_instance.get_object(repository, ref, path)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling ObjectsApi->get_object: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # get object content
        api_response = api_instance.get_object(
            # repository, ref, path, range=range, presign=presign)
            repository, ref, path, range=range)
        pprint(api_response)
    except lakefs_client.ApiException as e:
        print("Exception when calling ObjectsApi->get_object: %s\n" % e)


# EOF
