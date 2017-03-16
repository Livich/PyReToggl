# ReToggl unofficial API client

[![Build Status](https://travis-ci.com/Livich/PyReToggl.svg?token=6T8dpeTmz8PpycNpNg8C&branch=master)](https://travis-ci.com/Livich/PyReToggl)

## ReTogglAPI

API client implemented as class `ReTogglAPI`. Initialize it with `argparse.Namespace` to set such configurations:
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

In case when you need to hold a list of `ReTogglAPI.ReTogglTimeEntry` you may use `ReTogglAPI.ReTogglEntryList`.

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
rt_projects = tt.get_projects()
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

## TW2RT

`tw2rt` is a command line utility to copy time entries from TeamWork (using official TW API) to ReToggl (using given unofficial API implementation). Call `tw2rt -h` to see usage information.

>Hint: most configurations for tw2rt are placed in `./config.ini`. You may have your own `~/tw2rt.ini` outside the repository.

### Arguments

All command line arguments are optional.

* `-h, --help` display short help
* `-f, --date-from` date and time to start fetching time entries from TeamWork. Format: `DD/MM/YYYTHH:MM` (e.g. 13/01/2017T08:03). By default it is set to current date, 00:00
* `-t, --date-to` same as `-f`, means date and time to end with
* `-p, --profile` profile configuration file. T2RT will try to use `~/tw2rt.ini` and then `./config.ini` files when alternative value is not provided
* `-v, --verbose` verbosity level in range from -2 to 4. It is set to `0` by default
* `-S, --simulate` simulation flag. By default it set to `1` so TW2RT will not actually push time entries to ReToggl

### Configuration file format

```ini
[general]
user_agent=USER-AGENT HEADER VALUE

[retoggl]
endpoint=RETOGGL API ENDPOINT
user_token=RETOGGL USER TOKEN
user_id=RETOGGL USER ID
ch_user_token=CYBERHULL USER TOKEN

[teamwork]
endpoint=TEAMWORK API ENDPOINT
api_key=TEAMWORK API KEY
api_pass=TEAMWORK API PASSWORD
user_id=TEAMWORK USER ID
```

Team Work API client is implemented in `/TeamWorkAPI.py`

## `push_today`

`push_today` is a bash script to copy time entries from TeamWork to ReToggl using `tw2rt`. Script copies today's time entries auto-magically :) Call `push_today.sh` to see usage information.

# ReviewBuzz related information

I made reverse-engineering of ReToggl API for my own needs, to copy information about certain project (ReviewBuzz, actually) from TeamWork.
So there are a lot of ReviewBuzz related code in the repository.

## Usage with ReviewBuzz

* Clone the repository
* `sudo apt-get install python3 python3-pip -y`
* `python3 -m pip install requests`
* Put configuration file to `~/tw2rt.ini` (you may copy it from `config.ini`). Don't forget to change its contents!
* Use `push_today.sh` everyday, or by example:
```
python3 ./tw2rt.py -f 01/03/2017T00:01 -t 01/03/2017T23:59 -v 0 -S 0
```

Currently TW2RT will prevent duplicating ReToggl items just by stopping execution.

## `RBNameHelper`

ReviewBuzz Name Helper is a utility class which helps with ticket-name-to-project-id and ticket-name-to-task-name conversion.
Conversion routine is based on ticket naming standard which was modified by Dmitryy Prekrasnyy (so there is `__prekrasnyy_format` attribute).

`RBNameHelper` is used in both TW2RT and CSV2RT.
