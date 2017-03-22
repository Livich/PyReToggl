import argparse
from datetime import date, time, datetime, timedelta
from ReogglAPI import ReTogglAPI
from RBNameHelper import RBNameHelper
import csv
import sys

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
        -2: "",
        -1: "SYS: ",
        0: "STATUS: ",
        1: "INFO: ",
        2: "MSG: ",
        3: "EXTRA: ",
        4: "DBG: "
    }
    if args.verbose >= lvl:
        print("%s%s" % (hdr[lvl], message))


csv_date_format = "%d/%m/%Y"
csv_time_format = "%H:%M"
csv_date_time_format = "%s %s" % (csv_date_format, csv_time_format)

rt_projects = []

if args.simulate:
    verbose(-1, "Simulation mode ON. Set -S 0 to push tasks")

pushed = ReTogglAPI.ReTogglEntryList()
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
        verbose(
            2,
            "Pushing task [%s] at [%s] to the server%s" % (
                task["Task"],
                task["Date/Time"],
                " (simulation)" if args.simulate else ""
            )
        )
        start_datetime = datetime.strptime(task["Date/Time"], csv_date_time_format)
        try:
            hours = float(task["Decimal Hours"])
            total_time += timedelta(hours=hours)
            end_datetime = start_datetime + timedelta(hours=hours)
            time_entry = ReTogglAPI.ReTogglTimeEntry(
                start_date=start_datetime,
                end_date=end_datetime,
                name=task["Task"].strip(),
                project_id=RBNameHelper.conv_task_name_auto(task["Task"], RBNameHelper.NAME_TO_PROJECT_ID),
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
                "Can't convert name to project id and task name for task [%s] (id: %s) at [%s]: %s" % (
                    task["Task"],
                    task["Id"],
                    task["Date/Time"],
                    str(err)
                )
            )
            continue
        except Exception as err:
            verbose(
                -1,
                "Something wrong with server while pushing task [%s] at [%s]: %s. Check server state manually" % (
                    task["Task"],
                    task["Date/Time"],
                    str(err)
                )
            )
            continue

except Exception as err:
    verbose(-1, "Something went wrong: {0}".format(err))
    sys.exit(1)
verbose(2, "Total time: %s"%str(total_time))
verbose(-2, pushed.as_json())
