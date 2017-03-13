from ReogglAPI import ReTogglAPI

def test_rt_access():
    tt = ReTogglAPI({
       "user_id": "***REMOVED***",
       "endpoint": "***REMOVED***",
       "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
       "ch_user_token": "***REMOVED***",
       "user_token": "***REMOVED***"
    })
    rt_projects = tt.get_projects()
    assert len(rt_projects) > 0