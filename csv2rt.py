import argparse
from datetime import date, time, datetime, timedelta
from ReogglAPI import ReTogglAPI
import csv
import sys
import re

parser = argparse.ArgumentParser(description='CSV --> ReToggl importer.')
parser.add_argument('input', metavar='I', type=str, help='input CSV file')
parser.add_argument('-u', '--user-agent', type=str,
                    default='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
                    help='user-agent header for HTTP requests')
parser.add_argument('-e', '--endpoint', type=str,
                    default='***REMOVED***',
                    help='ReToggl API endpoint')
parser.add_argument('-t', '--user-token', type=str,
                    default='***REMOVED***',
                    help='ReToggl API token')
parser.add_argument('-i', '--user-id', type=str,
                    default='***REMOVED***',
                    help='ReToggl user id')
parser.add_argument('--ch-user-token', type=str,
                    default='***REMOVED***',
                    help='CyberHull user token')
parser.add_argument('-v', '--verbose', type=int,
                    default=0,
                    help='verbosity level. 0 is lowest, 4 - debug')
parser.add_argument('-S', '--simulate', type=int,
                    default=1,
                    help='simulation mode. Set to 0 to push tasks')

args = parser.parse_args()

args.simulate = True if args.simulate == 1 else False

def verbose(lvl, message):
    """Logger function

    Keyword arguments:
        lvl     --  message priority level
        message --  message text
    """
    hdr = {
        -1: "SYS",
        0: "STATUS",
        1: "INFO",
        2: "MSG",
        3: "EXTRA",
        4: "DBG"
    }
    if args.verbose >= lvl:
        print("%s: %s" % (hdr[lvl], message))


csv_date_format = "%d/%m/%Y"
csv_time_format = "%H:%M"
csv_date_time_format = "%s %s" % (csv_date_format, csv_time_format)

rt_projects = []

if args.simulate:
    verbose(-1, "Simulation mode ON. Set -S to False to push tasks")


class RBNameHelper:
    class NameConversionError(Exception):
        pass

    NAME_TO_PROJECT_ID = 1
    NAME_TO_TASK_NAME = 0

    __prekrasnyy_format = r"(?P<ticket>(\w*-\d*))"

    @staticmethod
    def conv_task_name(name, conversion_method):
        """Converts task name to project ID or to ReToggl task name

        Keyword arguments:
            name                --  the task name
            conversion_method   --  set to NAME_TO_PROJECT_ID when conversion to project id is needed
                                    or to NAME_TO_TASK_NAME when name prettifying needed
        """
        if conversion_method == RBNameHelper.NAME_TO_PROJECT_ID:
            return RBNameHelper.__name_to_project_id(name)
        if conversion_method == RBNameHelper.NAME_TO_TASK_NAME:
            return RBNameHelper.__name_to_task_name(name)

    @staticmethod
    def __name_to_project_id(name):
        # If ticket name matches pattern, use well-known project
        if 'mnt-' in name.lower():
            return '000000276'  # Maintenance
        if 'cyb-' in name.lower():
            return '000000084'  # Development
        if 'et-' in name.lower():
            return '000000277'  # Elm Tree Project
        if 'hive-' in name.lower():
            return '000000297'  # HIVE project
        if 'collaboration' in name.lower() and 'development' in name.lower():
           return '000000084' # Development
        if 'collaboration' in name.lower() and 'maintenance' in name.lower():
           return '000000276' # Maintenance

        raise RBNameHelper.NameConversionError("Cannot convert [%s] to project ID" % name)


        #items = RBNameHelper.__split(name)
        # Full search in ReviewBuzz projects
        #proj = ReTogglAPI.SearchHelper.search_by('name', 'Buzz', rt_projects)
        #proj = ReTogglAPI.SearchHelper.search_by('name', items["project"], proj)
        #if len(proj) <= 0:
        #    raise RBNameHelper.NameConversionError("Cannot convert [%s] to project ID" % str(items["project"]))
        #return proj[0].id

    @staticmethod
    def __name_to_task_name(name):
        # FIXME: dirty hack to apply ticket names
        if 'collaboration' in name.lower():
            return 'Calling, Collaboration'

        items = RBNameHelper.__split(name)
        return items["ticket"]

    @staticmethod
    def __split(name: str):
        matched = re.match(RBNameHelper.__prekrasnyy_format, name).groupdict()
        if len(matched) == 0:
            raise RBNameHelper.NameConversionError("Cannot apply regexp to [%s]" % name)
        return matched


class ReTogglEntryList(ReTogglAPI.ReTogglEntry):
    """Holds a list of ReTogglEntry"""
    l = []

    def append(self, item):
        self.l.append(item)

    def as_json(self):
        return self._as_json(self.l)

    def get_list(self):
        return self.l


pushed = ReTogglEntryList()
total_time = timedelta()
try:
    rt_api = ReTogglAPI(args, verbose)
    rt_projects = rt_api.get_projects()
    verbose(1, "Reading %s file" % args.input)
    task_data = []
    with open(args.input, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            task_data.append(row)
    verbose(1, "%i tasks loaded" % len(task_data))
    for task in task_data:
        verbose(2, "Pushing task [%s] at [%s] to the server%s" % (task["Task"], task["Date/Time"], " (simulation)" if args.simulate else ""))
        start_datetime = datetime.strptime(task["Date/Time"], csv_date_time_format)
        try:
            hours = float(task["Decimal Hours"])
            total_time += timedelta(hours=hours)
            end_datetime = start_datetime + timedelta(hours=hours)
            time_entry = ReTogglAPI.ReTogglTimeEntry(
                start_date=start_datetime,
                end_date=end_datetime,
                #name=RBNameHelper.conv_task_name(task["Task"], RBNameHelper.NAME_TO_TASK_NAME).strip(),
                name=task["Task"].strip(),
                project_id=RBNameHelper.conv_task_name(task["Task"], RBNameHelper.NAME_TO_PROJECT_ID),
                user_id=args.user_id,
                id=task["Id"]
            )
            if args.simulate:
                pushed.append(time_entry)
            else:
                pushed.append(rt_api.new_time_entry(time_entry))
                verbose(1, "Task [%s] at [%s] pushed" % (task["Task"], task["Date/Time"]))
        except RBNameHelper.NameConversionError as err:
            verbose(
                -1,
                "Can't convert name to project id and task name for task [%s] (id: %s) at [%s]: %s" %
                    (task["Task"], task["Id"], task["Date/Time"], str(err))
            )
            continue
        except Exception as err:
            verbose(
                -1,
                "Something wrong with server while pushing task [%s] at [%s]: %s. Check server state manually" %
                (task["Task"], task["Date/Time"], str(err))
            )
            continue

except Exception as err:
    verbose(-1, "Something went wrong: {0}".format(err))
    sys.exit(1)
verbose(2, "Total time: %s"%str(total_time))
verbose(1, pushed.as_json())
