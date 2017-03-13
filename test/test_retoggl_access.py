from ReogglAPI import ReTogglAPI
from argparse import Namespace
import pytest

@pytest.fixture()
def api_setup():
    rt_api =  ReTogglAPI(Namespace(
       user_id = "***REMOVED***",
       endpoint = "***REMOVED***",
       user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
       ch_user_token = "***REMOVED***",
       user_token = "***REMOVED***"
    ))
    return rt_api

def test_rt_access(api_setup):
    rt_projects = api_setup.get_projects()
    assert len(rt_projects) > 0