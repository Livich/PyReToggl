import requests
import json
from datetime import date, time, datetime
import random
from urllib.parse import urlparse


class ReTogglAPI:
    """Implements some general API calls for CyberHull ReToggl app"""
    params = {}
    common_headers = {}
    date_format = "%Y-%m-%d"
    time_format = "%H:%M:%S"
    datetime_format = "%sT%s" % (date_format, time_format)
    rt_projects = {}
    rt_latest_tasks = {}

    class SearchHelper:
        """Provides easy to use search in ReTogglEntry lists"""

        @staticmethod
        def search_by(where, what, items):
            results = {}
            _ = [results.update({k: item}) if what in getattr(item, where) else None for k, item in items.items()]
            return results

    class ReTogglEntry:
        """Common parent for any ReToggl entry"""

        def as_json(self):
            return self._as_json(self)

        @staticmethod
        def _as_json(obj):
            def __try_to_str(o):
                try:
                    return o.__dict__
                except:
                    if type(o) is datetime:
                        return o.strftime(ReTogglAPI.datetime_format)
                    if type(o) is time:
                        return o.strftime(ReTogglAPI.time_format)
                    if type(o) is date:
                        return o.strftime(ReTogglAPI.date_format)
                    if type(o) is ReTogglAPI.ReTogglTimeEntry:
                        return o.as_json()
                    return str(o)

            return json.dumps(
                obj,
                default=lambda o: __try_to_str(o),
                sort_keys=True,
                indent=0,
                separators=(',', ':')
            ).replace('\n', '')

    class ReTogglTimeEntry(ReTogglEntry):
        """Time entry holds information about every user's activity: time, task and so on"""
        def __init__(self,
                     end_date=datetime.today(),
                     name='',
                     project_id='',
                     start_date=datetime.today(),
                     time_zone_offset_minutes=0,
                     user_id=0,
                     id=0,
                     deleted=False):
            self.end_date = end_date
            self.name = name
            self.project_id = project_id
            self.start_date = start_date
            self.time_zone_offset_minutes = time_zone_offset_minutes
            self.user_id = user_id
            self.id = id
            self.deleted = deleted

        def as_new_json(self):
            """Get JSON data for the entity. Server needs special JSON format to create new entries"""
            o = [{
                'temporary_id': random.randint(0, 99999999),
                'time_entry': {
                    'user_id': self.user_id,
                    'name': self.name,
                    'project_id': self.project_id,
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'time_zone_offset_minutes': self.time_zone_offset_minutes,
                    'deleted': self.deleted
                }
            }]
            return self._as_json(o)

        @staticmethod
        def from_dict(data):
            """Construct ReTogglTimeEntry using dict"""
            return ReTogglAPI.ReTogglTimeEntry(
                end_date=datetime.strptime(data['end_date'], ReTogglAPI.datetime_format),
                name=data['name'],
                project_id=data['project_id'],
                start_date=datetime.strptime(data['start_date'], ReTogglAPI.datetime_format),
                time_zone_offset_minutes=data['time_zone_offset_minutes'],
                user_id=data['user_id'],
                id=data['id']
            )
            pass

    class ReTogglEntryList(ReTogglEntry):
        """Holds a list of ReTogglEntry"""
        l = []

        def append(self, item):
            self.l.append(item)

        def as_json(self):
            return self._as_json(self.l)

        def get_list(self):
            return self.l

    class ReTogglProject(ReTogglEntry):
        """Project holds general information about a number of time entries"""
        __default_project = {
            'active': True,
            'client_id': '',
            'color': '#FF0000',
            'id': random.randint(1, 9999999999),
            'name': ''
        }

        def __init__(self, project=__default_project):
            [setattr(self, attr, value) for attr, value in project.items()]

    def __init__(self, params, verbose=lambda x, y: None):
        """Create new ReTogglAPI entity. Use instance of the class to access ReToggl API.

        Keyword arguments:
            params  --  common configurations
            verbose --  message output method
        """
        self.params = params
        self.verbose = verbose
        endpoint = urlparse(self.params.endpoint)
        self.common_headers = {
            'Host': endpoint.netloc,
            'User-Agent': params.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'CH-User-Token': params.ch_user_token,
            'Referer': 'http://%s/' % endpoint.netloc,
            'Connection': 'keep-alive'
        }

    def __get_json(self, method, url, **kwargs):
        self.verbose(4, "[%s] %s" % (method, url))
        response = requests.request(method, url, **kwargs)
        j = json.loads(response.text)
        return j

    def get_projects(self):
        """Load all projects from server"""
        u_get_projects = "%sprojects?user_token=%s" % (
            self.params.endpoint,
            self.params.user_token
        )
        data = self.__get_json('get', u_get_projects, headers=self.common_headers)
        projects = {proj['id']: self.ReTogglProject(proj) for (proj) in data['data']}
        return projects

    def get_tasks(self, start_date, end_date):
        """Get time entries from server in date range"""
        s_start_date, s_end_date = start_date.strftime(self.date_format), end_date.strftime(self.date_format)
        u_get_tasks = "%stime-entries?user_token=%s&end_date=%s&start_date=%s" % (
            self.params.endpoint,
            self.params.user_token,
            s_end_date,
            s_start_date
        )
        data = self.__get_json('get', u_get_tasks, headers=self.common_headers)
        tasks = {ti['id']: self.ReTogglTimeEntry(ti) for (ti) in data['data']['time_entries']}
        self.verbose(2, "Loaded %i time entries from %s to %s" % (len(tasks), s_start_date, s_end_date))
        return tasks

    def get_latest_tasks(self):
        """Get time entries for last month"""
        # FIXME: Don't ask my why it works with 8th days of month only
        date_from = date(year=date.today().year, month=date.today().month - 1, day=8)
        date_to = date(year=date_from.year, month=date.today().month + 1, day=8)
        return self.get_tasks(date_from, date_to)

    def new_time_entry(self, task: ReTogglTimeEntry):
        """Push time entry to the server"""
        json_task = task.as_new_json()
        self.verbose(4, "Ready to push new task:\n%s" % (json_task))

        u_new_task = "%stime-entries?user_token=%s" % (
            self.params.endpoint,
            self.params.user_token
        )
        result = self.__get_json('post', u_new_task, headers=self.common_headers, data=json_task)
        return ReTogglAPI.ReTogglTimeEntry.from_dict(result['data'][0]['created_object'])

    def delete_time_entry(self, te):
        """Remove time entry from server"""
        data = ReTogglAPI.ReTogglEntry()
        data.id = te.id
        data.deleted = True
        data = '[' + data.as_json() + ']'
        self.verbose(4, "Ready to delete task #%s" % (te.id))

        u_del_task = "%stime-entries?user_token=%s" % (
            self.params.endpoint,
            self.params.user_token
        )
        result = self.__get_json('delete', u_del_task, headers=self.common_headers, data=data)
        return ReTogglAPI.ReTogglTimeEntry.from_dict(result['data'][0]['updated_object'])

# # Usage example
#
# # Create API client instance
# tt = ReTogglAPI(args)
# # Get existing project
# rt_projects = tt.get_projects()
# proj = (ReTogglAPI.SearchHelper.search_by('name', 'Review Buzz: Dev', rt_projects)[0])
# # Create new time entry in the project
# te = ReTogglAPI.ReTogglTimeEntry(
#     end_date=datetime.today()+timedelta(minutes=15),
#     name="TTT-123",
#     project_id=proj.id,
#     user_id=args.user_id
# )
# # Push it to server
# te = tt.new_time_entry(te)
# # Remove it from server
# te = tt.delete_time_entry(te)
#
# # Please note that task list is also stored locally, in your browser,
# # so you will see updates after re-login in the ReToggl. It is recommended
# # to close ReToggl in your browser during API usage
