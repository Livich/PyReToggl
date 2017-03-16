from TeamWorkAPI import TeamWorkAPI
from argparse import Namespace
import pytest
import datetime

@pytest.fixture()
def api_setup():
    tw_api = TeamWorkAPI(Namespace(
       endpoint="***REMOVED***",
       user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
       api_key="***REMOVED***",
       password="***REMOVED***"
    ))
    return tw_api


def test_tw_access(api_setup):
    dt_from = datetime.date(2017, 3, 13)
    dt_to = datetime.date(2017, 3, 14)
    tw_entries = api_setup.get_time_entries(dt_from, dt_to, ***REMOVED***)
    assert len(tw_entries) > 0