import argparse
import datetime
from ReogglAPI import ReTogglAPI
from TeamWorkAPI import TeamWorkAPI
from RBNameHelper import RBNameHelper
import sys
import os
import configparser

date_format = "%d/%m/%Y"
time_format = "%H:%M"
date_time_format = "%sT%s" % (date_format, time_format)
date_time_format_friendly = 'DD/MM/YYYYTHH:MM'
global_config_file = os.path.expanduser('~')+"/tw2rt.ini"


def valid_date_time(s):
    try:
        if not s:
            return datetime.datetime.today()
        return datetime.datetime.strptime(str.strip(s), date_time_format)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='TeamWork --> ReToggl importer.')

parser.add_argument('-f',
                    '--date-from',
                    type=valid_date_time,
                    default='',
                    help='Date and time to start from (%s)' % date_time_format_friendly)
parser.add_argument('-t',
                    '--date-to',
                    type=valid_date_time,
                    default='',
                    help='Date and time to end with (%s)' % date_time_format_friendly)
parser.add_argument('-p',
                    '--profile',
                    type=str,
                    default=global_config_file if os.path.isfile(global_config_file) else "./config.ini",
                    help='Profile to work with')
parser.add_argument('-v',
                    '--verbose',
                    type=int,
                    default=0,
                    help="verbosity levels: "
                         "-2    necessary output. "
                         "-1    system messages. "
                         "0     status info. "
                         "1     information. "
                         "2     messages. "
                         "3     extra information. "
                         "4     debug information")
parser.add_argument('-S',
                    '--simulate',
                    type=int,
                    default=1,
                    help='simulation mode. Set to 0 to push tasks')
parser.add_argument('--force',
                    action='store_true')

args = parser.parse_args()

args.simulate = True if args.simulate == 1 else False

config = configparser.ConfigParser()

if not os.path.isfile(args.profile):
    raise FileNotFoundError("%s profile configuration is not found" % args.profile)

config.read(args.profile)


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

if args.simulate:
    verbose(-1, "Simulation mode ON. Set -S 0 to push tasks")

pushed = ReTogglAPI.ReTogglEntryList()
try:
    verbose(1, "Loading projects from ReToggl")
    rt_api = ReTogglAPI(
        argparse.Namespace(
            user_id=config['retoggl']['user_id'],
            endpoint=config['retoggl']['endpoint'],
            user_agent=config['general']['user_agent'],
            ch_user_token=config['retoggl']['ch_user_token'],
            user_token=config['retoggl']['user_token']
        ),
        verbose
    )

    for tid, task in rt_api.get_latest_tasks().items():
        if args.date_from < task.start_date < args.date_to and not args.force:
            # TODO: remove duplicates from ReToggl before push
            raise Exception("There is at least one time entry to duplicate. TW2RT doesn't handle this currently")

    rt_projects = rt_api.get_projects()
    verbose(1, "%i projects loaded" % len(rt_projects))

    verbose(1, "Loading time entries from TeamWork")
    task_data = []
    tw_api = TeamWorkAPI(
        argparse.Namespace(
           endpoint=config['teamwork']['endpoint'],
           user_agent=config['general']['user_agent'],
           api_key=config['teamwork']['api_key'],
           password=config['teamwork']['api_pass']
        ),
        verbose=verbose
    )

    task_data = tw_api.get_time_entries(args.date_from, args.date_to, config['teamwork']['user_id'])
    verbose(1, "%i time entries loaded" % len(task_data))
    rbNameHelper = RBNameHelper(config.items('rb_name_helper'))
    for task in task_data:
        verbose(
          2,
          "Pushing task [%s] at [%s] to the server%s" % (
              task.name,
              datetime.datetime.strftime(task.dt_start, date_time_format),
              " (simulation)" if args.simulate else ""
          )
        )
        try:
            time_entry = ReTogglAPI.ReTogglTimeEntry(
                start_date=task.dt_start,
                end_date=task.dt_finish,
                name=task.name,
                project_id=rbNameHelper.conv_task_name(task.name, RBNameHelper.NAME_TO_PROJECT_ID),
                user_id=config['retoggl']['user_id'],
                id=task.id
            )
            if args.simulate:
                pushed.append(time_entry)
            else:
                pushed.append(rt_api.new_time_entry(time_entry))
                verbose(
                    1,
                    "Task [%s] at [%s] pushed" % (
                        task.name,
                        datetime.datetime.strftime(task.dt_start, date_time_format)
                    )
                )
        except RBNameHelper.NameConversionError as err:
            verbose(
                -1,
                "Can't convert name to project id and task name for task [%s] (id: %s): %s" % (
                    task.name,
                    task.id,
                    str(err)
                )
            )
            continue
        except Exception as err:
            verbose(
                -1,
                "Something wrong with server while pushing task [%s] (id=%s): %s. Check server state manually" % (
                    task.name,
                    task.id,
                    str(err)
                )
            )
            continue

except Exception as err:
    verbose(-1, "Something went wrong: {0}".format(err))
    exc_type, exc_obj, exc_tb = sys.exc_info()
    verbose(-1, 'Error on line {0}'.format(exc_tb.tb_lineno))
    sys.exit(1)
verbose(-2, pushed.as_json())
