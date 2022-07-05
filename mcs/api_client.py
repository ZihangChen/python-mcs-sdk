import requests
import json
from mcs.common import utils, exceptions
from mcs.common import constants as c


class ApiClient(object):

    def _request(self, method, request_path, params, files=False):
        if method == c.GET:
            request_path = request_path + utils.parse_params_to_str(params)
        url = c.MCS_API + c.REST_API_VERSION + request_path

        body = params if method == c.POST else ""
        header = {}
        print("url:", url)
        print("body:", body)

        # send request
        response = None
        if method == c.GET:
            response = requests.get(url, headers=header)
        elif method == c.POST:
            if files:
                response = requests.post(url, data=body, headers=header, files=files)
            else:
                response = requests.post(url, data=body, headers=header)
        elif method == c.DELETE:
            response = requests.delete(url, headers=header)

        # exception handle
        if not str(response.status_code).startswith('2'):
            raise exceptions.McsAPIException(response)

        return response.json()

    def _request_without_params(self, method, request_path):
        return self._request(method, request_path, {})

    def _request_with_params(self, method, request_path, params, files):
        return self._request(method, request_path, params, files)
