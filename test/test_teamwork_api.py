from TeamWorkAPI import TeamWorkAPI
from argparse import Namespace
import datetime


def test_tw_access(tw_config):
    tw_api = TeamWorkAPI(Namespace(**tw_config))
    dt_from = datetime.date(2017, 3, 13)
    dt_to = datetime.date(2017, 3, 14)
    tw_entries = tw_api.get_time_entries(dt_from, dt_to, ***REMOVED***)
    assert len(tw_entries) > 0