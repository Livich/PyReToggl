from ReogglAPI import ReTogglAPI
from argparse import Namespace
import requests
import json
import pytest

class TRetogglApi(ReTogglAPI):
      api_call_method = ''
      api_call_url = ''

      def _ReTogglAPI__get_json(self, method, url, **kwargs):
        self.api_call_method = method
        self.api_call_url = url
        response = requests.request(method, url, **kwargs)
        j = json.loads(response.text)
        return j

@pytest.fixture()
def api_setup():
    rt_api = TRetogglApi(Namespace(
       user_id="***REMOVED***",
       endpoint="***REMOVED***",
       user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
       ch_user_token="***REMOVED***",
       user_token="***REMOVED***"
    ))
    return rt_api


def test_rt_access(api_setup):
    rt_projects = api_setup.get_projects()
    assert len(rt_projects) > 0
    assert api_setup.api_call_method == 'get'
    assert api_setup.api_call_url == '***REMOVED***projects?user_token=***REMOVED***'