from ReogglAPI import ReTogglAPI
from argparse import Namespace
import requests
import json


class TRetogglApi(ReTogglAPI):
    api_call_method = ''
    api_call_url = ''

    def _ReTogglAPI__get_json(self, method, url, **kwargs):
        self.api_call_method = method
        self.api_call_url = url
        response = requests.request(method, url, **kwargs)
        j = json.loads(response.text)
        return j


def test_rt_access(rt_config):
    rt_api = TRetogglApi(Namespace(**rt_config))
    rt_projects = rt_api.get_projects()
    assert len(rt_projects) > 0
    assert rt_api.api_call_method == 'get'
    assert '***REMOVED***projects?user_token=' in rt_api.api_call_url
