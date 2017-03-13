# ReToggl unofficial API client

[![Build Status](https://travis-ci.com/Livich/PyReToggl.svg?token=6T8dpeTmz8PpycNpNg8C&branch=master)](https://travis-ci.com/Livich/PyReToggl)

## ReTogglAPI

API client implemented as class `ReTogglAPI`. Initialize it with dict to set such configurations:
* `endpoint` - API endpoint (HTTP address)
* `user_agent` - User-Agent header string
* `ch_user_token` - CyberHull user token
* `user_token` - ReToggl user token

There are such methods available:
* `get_projects(): dict` loads all projects from server
* `get_tasks(start_date: date, end_date: date): dict` loads tasks from server
* `get_latest_tasks(): dict` loads latest tasks from server. This is a wrapper to `get_tasks` which prepares `start_date` and `end_date` in more safer (and very specific to ReToggl API) manner
* `new_time_entry(te: ReTogglAPI.ReTogglTimeEntry): ReTogglAPI.ReTogglTimeEntry` push time entry to server
* `delete_time_entry(te: ReTogglAPI.ReTogglTimeEntry): ReTogglAPI.ReTogglTimeEntry` delete time entry from server

>Hint: do not use API client and your browser at the same time. The API client uses just the same methods as your browser. API specification is unofficial and just sniffed using browser tools so there may be collisions between API clients.

There is special class to hold ReToggl time entry - `ReTogglAPI.ReTogglTimeEntry`. Its constructor accepts such arguments:
* `end_date: datetime` - time entry finish date and time
* `name: str` - time entry name
* `project_id: str` - project which holds the entry. Project id is stored on the server so use `ReTogglAPI.get_projects` to access project list end extract ids
* `start_date: datetime` - time entry start date and time
* `time_zone_offset_minutes: int` - time zone offset
* `user_id: str` - ReToggl user id
* `id: str` - set this field to random number to create new task. After using `ReTogglAPI.new_time_entry` on such entry the field will be updated to actual value
* `deleted: bool` - deletion flag

### Usage example
```python
from ReogglAPI import ReTogglAPI
from argparse import Namespace

# Create API client instance
tt = ReTogglAPI(Namespace(
    user_id="1234",
    endpoint="***REMOVED***",
    user_agent="PyReToggl",
    ch_user_token="YOUR CH TOKEN",
    user_token="YOUR RT TOKEN"
))

# Get project
rt_projects = rt_api.get_projects()
proj = (ReTogglAPI.SearchHelper.search_by('name', 'Review Buzz: Dev', rt_projects)[0])
# Create new time entry in the project. Other attributes will be set automatically
te = ReTogglAPI.ReTogglTimeEntry(
    end_date=datetime.today()+timedelta(minutes=15),
    name="TTT-123",
    project_id=proj.id,
    user_id=args.user_id
)
# Push it to server
te = tt.new_time_entry(te)
# Remove it from server
te = tt.delete_time_entry(te)

# Please note that task list is also stored locally, in your browser,
# so you will see updates after re-login in the ReToggl. It is recommended
# to close ReToggl in your browser during API usage
```
      
## CSV2RT

`csv2rt` is a command line utility which implements import from TeamWork CSV file to ReToggl. CSV example:
```csv
Id,Date,Date/Time,Project,Company,Who,Hours,Minutes,Decimal Hours,Description,Task List,Task,Parent Task,Is Sub-task,Is it Billable?,Invoice Number,Tags
"4668473","20/02/2017","20/02/2017 10:09","CyberHull company","Outstaffing","Dima Prekrasnyy","2","22","2.367","","20-26 Feb","Collaboration - Development - RB","","0","1","","",
```

Look to code of `csv2rt` to get extended API client usage example.

##TW2RT

`tw2rt` is a command line utility to copy time entries from TeamWork (using official TW API) to ReToggl (using given unofficial API implementation).

Team Work API client is implemented in `/TeamWorkAPI.py`.
        