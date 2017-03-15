import urllib

import requests
import json
import datetime
from urllib.parse import urlparse
import base64


class TeamWorkAPI:

    class TeamWorkTimeEntry:
        date_format = "%Y-%m-%d"
        time_format = "%H:%M:%S"
        datetime_format = "%sT%sZ" % (date_format, time_format)

        def __init__(self,
                     name='',
                     project_id=0,
                     hours=0,
                     minutes=0,
                     date_start='',
                     person_id=0,
                     id=0):
            self.name = name
            self.project_id = project_id
            self.dt_start = datetime.datetime.strptime(date_start, self.datetime_format)
            self.dt_finish = self.dt_start + datetime.timedelta(hours=int(hours), minutes=int(minutes))
            self.person_id = person_id
            self.id=id

        @staticmethod
        def from_dict(data):
            return TeamWorkAPI.TeamWorkTimeEntry(
                name=data['todo-item-name'],
                project_id=data['project-id'],
                hours=data['hours'],
                minutes=data['minutes'],
                date_start=data['dateUserPerspective'],
                person_id=data['person-id'],
                id=data['todo-item-id']
            )

    params = {}
    endpoint = ""
    common_headers = {}
    date_format = "%Y%m%d"
    time_format = "%H:%M"

    def __init__(self, params, verbose=lambda x, y: None):
        """Create new TeamWorkAPI entity. Use instance of the class to access TeamWork API.

        Keyword arguments:
            params  --  common configurations
            verbose --  message output method
        """
        self.params = params
        self.verbose = verbose
        self.endpoint = urlparse(params.endpoint)
        self.common_headers = {
            'Host': self.endpoint.netloc,
            'User-Agent': params.user_agent,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive',
            'Authorization': 'BASIC '+base64.b64encode(
                ("%s:%s" % (params.api_key, params.password)).encode('ascii')
            ).decode('ascii')
        }

    def __get_json(self, what, headers, data):
        url = self.params.endpoint+what
        self.verbose(4, "[get] %s" % url)
        data = requests.get(url, headers=headers, data=data)
        j = json.loads(data.text)
        entries = [TeamWorkAPI.TeamWorkTimeEntry.from_dict(e) for e in j['time-entries']]
        return entries

    def get_time_entries(self, dt_from: datetime, dt_to: datetime, uid):
        data = {
                'fromdate': dt_from.strftime(self.date_format),
                'fromtime': dt_from.strftime(self.time_format),
                'todate': dt_to.strftime(self.date_format),
                'totime': dt_to.strftime(self.time_format),
                'showDeleted': False
        }
        if uid:
            data['userId'] = uid
        params = urllib.parse.urlencode(data, doseq=True)
        entries = self.__get_json("time_entries.json?%s" % params, self.common_headers, None)

        return entries


