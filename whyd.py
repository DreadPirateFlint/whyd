from __future__ import print_function

from time import sleep
import os
import datetime
import argparse
import re
import json
import requests
import sys
from datetime import timedelta
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

WHYD_URL = ''
API_KEY = ''
HOME_DIR = ''
item_list = []


def parse_duration(duration_str):
    duration_regex = re.compile(r'(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?')

    match = duration_regex.match(duration_str)

    if match:
        hours = int(match.group('hours')) if match.group('hours') else 0
        minutes = int(match.group('minutes')) if match.group('minutes') else 0

        total_minutes = hours * 60 + minutes

        return total_minutes

    return None


"""
Returns a string with a maximum length of `slen`.

Parameters:
    str (str): The input string.
    slen (int, optional): The maximum length of the output string. Defaults to 35.

Returns:
    str: The input string truncated to `slen` characters if its length is greater than `slen`, 
    otherwise the input string is returned as is.
"""
def show_str_len(str, slen=35):
    # print("Show string")
    if slen == -1:
        return str
    if len(str) > slen:
        return str[:slen] + ""
    return str


def do_whyd(func):
    url = WHYD_URL + func
    # print("Calling url: ", url)
    headers = {}
    headers['x-api-key'] = API_KEY
    returnresponse = '{}'
    try:
        r = requests.get(url, headers=headers)
        returnresponse = r.text
    except Exception as e:
        print("Exception when calling WHYD: %s\n" % e)
    # print("Got response: ", r.text)
    return returnresponse


def get_project_completions():
    global args

    jstr = do_whyd('api/projects')
    jstrjson = json.loads(jstr)
    sorted_items = jstrjson
    # sort this list by client_ident, then by name
    sorted_items = sorted(jstrjson, key=lambda x: (x['client_ident'], x['name']))

    for j in sorted_items:
        if args.c:
            if str(args.c) in str(j['client_ident']):
                print(f"'{j['project_ident']}: {j['name']}, {j['client_name']}, {j['client_ident']}'")
        else:
            print(f"'{j['project_ident']}: {j['name']}, {j['client_name']}, {j['client_ident']}'")

        # print(f"{j['id']}:{j['name']}")
    # print("get_clients returned: ", jstrjson)
    update_project_cache(sorted_items)
    return jstrjson


def get_message_completions(projectid=None, display=True):
    if projectid is None:
        jstr = do_whyd('api/messages')
    else:
        jstr = do_whyd('api/messages/' + str(projectid))

    jstrjson = json.loads(jstr)
    sorted_items = jstrjson
    z = 0
    update_message_cache(sorted_items)
    for j in sorted_items:
        if display:
            print(f"'{j['message']}: Project ID {j['pid']} ' ")
        z += 1
    return jstrjson


def update_message_cache(msgs):
    file = open(str(HOME_DIR) + "/messagecache", "w")
    for j in msgs:
        out = str(f"'{j['message']}: Project ID {j['pid']}'")
        file.write(out + "\n")
    file.close()


def update_client_cache(clients):
    file = open(str(HOME_DIR) + "/clientcache", "w")
    for j in clients:
        out = str(f"'{j['client_ident']}: {j['name']}'")
        file.write(out + "\n")
    file.close()


def update_project_cache(projects):
    file = open(str(HOME_DIR) + "/projectcache", "w")
    for j in projects:
        out = str(f"'{j['project_ident']}: {j['name']}, {j['client_name']}, {j['client_ident']}'")
        # out = str(f"'{j['message']}: Project ID {j['pid']} ' ")
        file.write(out + "\n")
    file.close()



def get_projects(use_table=False, display=True):
    # print("get_projects")
    try :
        jstr = do_whyd('api/projects')
        jstrjson = json.loads(jstr)
    except Exception as e:
        print("Error getting projects")
        print(e)
        sys.exit(1)

    # print("json is ", jstrjson)
    sorted_items = sorted(jstrjson, key=lambda x: x['client_name'])

    if use_table:
        table = Table(title="Active Clients/Projects")
        rows = []

        columns = ["Project ID", "Project", "Client (ID)"]
        for column in columns:
            table.add_column(column)

        for j in sorted_items:
            table.add_row(str(j['project_ident']), str(j['name']), str(j['client_name']) + " (" + str(j['client_ident']) + ")")
        # print(f"Client: {j['client_name']}\t\tProject: {j['name']}")
        if display:
            console = Console()
            console.print(table)
            print("")
    else:
        for j in sorted_items:
            if display:
                print(f" {j['project_ident']},{j['name']}, {j['client_name']}, {j['client_ident']} ")
    # print("get_clients returned: ", jstrjson)
    update_project_cache(sorted_items)

    return jstrjson


def get_messages():
    jstr = do_whyd('api/messages')
    jstrjson = json.loads(jstr)
    for j in jstrjson:
        print(f"'{j['ident']}: {j['name']}'")
    # print("get_clients returned: ", jstrjson)
    return jstrjson



def get_clients(display=True):
    jstr = do_whyd('api/clients')
    jstrjson = json.loads(jstr)

    for j in jstrjson:
        print(f"'{j['client_ident']}: {j['name']}'")
    # print("get_clients returned: ", jstrjson)
    update_client_cache(jstrjson)
    return jstrjson


def send_new_time(durationmin, projectid, message):
    duration = durationmin * 1000 * 60
    url = WHYD_URL + 'api/newtime'
    headers = {}
    headers['x-api-key'] = API_KEY
    pp = {'time': duration, 'project': projectid, 'message': message}
    req = requests.get(url, headers=headers, params=pp)
    if req.status_code != 200:
        print(req.text)
    get_message_completions(display=False)



def refresh_caches():
    get_projects(display=False)
    get_clients(display=False)
    get_message_completions(display=False)



def display_times_table(data, title="Time Tracked"):
    global item_list
    table = Table(title=title, show_footer=True)
    rows = []
    durtotal = 0
    for j in data:
        tdur = int(j['duration'] / 1000 / 60)
        durtotal += tdur
    td_str = str(timedelta(seconds=durtotal * 60))
    x = td_str.split(':')
    td = "" + x[0] + "h " + x[1] + "m "
    # print('Time in hh:mm:ss:', x[0], 'Hours', x[1], 'Minutes', x[2], 'Seconds')

    columns = ["ID", "Dur.", "Message", "Project", "Client", "Start"]
    table.add_column(columns[0], style="cyan")
    table.add_column(columns[1], footer=f"{td}", style="yellow")
    table.add_column(columns[2])
    table.add_column(columns[3])
    table.add_column(columns[4])
    table.add_column(columns[5])
    cntr = 1
    # we rebuild this item list so that the user can select an item to delete
    item_list = []
    for j in data:
        tdur = str(int(j['duration'] / 1000 / 60)) + "m"
        item_list.append(j)
        tproj = show_str_len(j['project'], slen=16) + " (" + str(j['projectid']) + ")"
        sident = str(j['ident'])
        table.add_row(str(sident), tdur,
                      show_str_len(j['message']), tproj,
                      show_str_len(j['client'], slen=10) + " (" + str(j['clientid']) + ")",
                      j['start_time'])
        cntr += 1
    # sec.add_row("1", "2", "3", "4", "5")
    console = Console()
    console.print(table)


def display_times_ascii(data, title="Time Tracked"):
    global item_list
    for d in data:
        item_list.append(d)
        tdur = d['duration'] / 1000 / 60
        print(f"Duration: {int(tdur)}m\t Message: {d['message']}\t  Start: {d['start_time']} End: {d['end_time']} ")
        # d['start_time'], d['end_time'], d['duration'], d['message'])


def make_api_request(url):
    headers = {}
    headers = {'x-api-key': API_KEY}
    req = requests.get(url, headers=headers)
    if req.status_code != 200:
        print("Error on API request for url ", url)
        print(req.text)
        sys.exit(1)

    return req


def build_items_from_json(text):
    js = json.loads(text)
    item_list = []
    for d in js:
        item_list.append(d)
    return js


def list_today(use_table=False, clientid=False):
    clientpart = ""
    if clientid:
        clientpart = "/" + str(clientid)
    url = WHYD_URL + 'api/list_today' + clientpart
    req = make_api_request(url)
    data = build_items_from_json(req.text)
    if use_table:
        display_times_table(data, title="Time Tracked Today")
    else:
        display_times_ascii(data, title="Time Tracked Today")
    return json.loads(req.text)


def list_week(use_table=True, clientid=False):
    clientpart = ""
    if clientid:
        clientpart = "/" + str(clientid)
    url = WHYD_URL + 'api/list_week' + clientpart
    req = make_api_request(url)
    data = build_items_from_json(req.text)
    if use_table:
        display_times_table(data, title="Time Tracked This Week")
    else:
        display_times_ascii(data, title="Time Tracked This Week")

    return json.loads(req.text)


def list_month(use_table=True, clientid=False):
    clientpart = ""
    if clientid:
        clientpart = "/" + str(clientid)
    url = WHYD_URL + 'api/list_month' + clientpart
    req = make_api_request(url)
    data = build_items_from_json(req.text)
    if use_table:
        display_times_table(data, title="Time Tracked This Month")
    else:
        display_times_ascii(data, title="Time Tracked This Month")
    return data


def list_last_month(use_table=True, clientid=False):
    clientpart = ""
    if clientid:
        clientpart = "/" + str(clientid)
    url = WHYD_URL + 'api/list_last_month' + clientpart
    req = make_api_request(url)
    data = build_items_from_json(req.text)
    if use_table:
        display_times_table(data, title="Time Tracked Last Month")
    else:
        display_times_ascii(data, title="Time Tracked Last Month")
    return data


def delete_item(item_id):
    url = WHYD_URL + 'api/delete_time/' + str(item_id)
    req = make_api_request(url)
    print(req.text)
    return req.text

def write_start_time(start_datetime):
    # write time out to a file
    nowtime = start_datetime
    file = open(HOME_DIR + "/starttime.txt", "w")
    # start_time = datetime.datetime.strptime(nowtime, '%Y-%m-%d %H:%M:%S')
    start_time = str(nowtime)
    string_to_write = str(start_time)
    file.write(string_to_write)
    file.close()

def read_start_time():
    # read time from a file
    file = open(HOME_DIR + "/starttime.txt", "r")
    date_time_str = file.readline().strip()
    date_time = ""
    if date_time_str != "":
        date_time = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        file.close()
        return date_time
    file.close()
    return "Not Tracking"


def clear_start_time():
    file = open(HOME_DIR + "/starttime.txt", "w")
    file.write("")
    file.close()


def load_config():
    global API_KEY, WHYD_URL, HOME_DIR

    home_dir = os.path.expanduser("~")
    load_dotenv(home_dir + "/.whyd/config")
    API_KEY = os.getenv("WHYD_API_KEY") or os.getenv("API_KEY")
    WHYD_URL = os.getenv("WHYD_URL")
    HOME_DIR = os.path.expanduser(os.getenv("HOME_DIR", "~/.whyd"))


# def stripe_test():
#     try:
#         email = 'kurt.overberg+rogerdaltry@gmail.com'
#         email = 'ed@hotdogrecords.com'
#         user = stripe.Customer.list(email=email)
#
#         if len(user['data']) == 0: # No customer found
#             print(f"Customer {email} not found")
#             return
#
#         customer_id = user['data'][0].id
#
#         print(json.dumps(user))
#         # Retrieve all subscriptions for given customer
#         subscriptions = stripe.Subscription.list(
#             customer=customer_id,
#             status='all',
#             expand=['data.default_payment_method']
#         )
#         print(json.dumps(subscriptions))
#         if subscriptions['data'][0]['plan'].active:
#             print("User has an active plan.")
#         else:
#             print("User is Active")
#
#     except Exception as e:
#         return json.loads(str(e)), 403
#
#     return json.dumps({'status': 'success'})
#

###################  Main  ####################
def main():

    load_config()

    parser = argparse.ArgumentParser(description='Track time with What Have You Done')
    timergroup = parser.add_argument_group('Time Tracking')
    timergroup.add_argument('-n', help='Add a new time', action='store_true')
    timergroup.add_argument('-t', type=str, default='1h', required='-n' in sys.argv,
                            help='Time duration to track (ex 1h30m)', metavar='time')
    timergroup.add_argument('-p', help='Attach message to project ID #',
                            required='-n' in sys.argv, type=str, metavar='projectid')
    timergroup.add_argument('-m', '--msg', nargs='+', type=str, required='-n' in sys.argv, help='Message to include with time tracking')
    timergroup.add_argument('-s', help='Start tracking timer', action='store_true')
    timergroup.add_argument('-v', help='Show tracking timer', action='store_true')
    timergroup.add_argument('-x', help='Record tracking timer and reset', action='store_true')
    timergroup.add_argument('-clear', help='Clear tracking timer', action='store_true')
    timergroup.add_argument('-d', type=int, help='Delete a time by id, use in conjuntion with reporting')

    reportgroup = parser.add_argument_group('Reporting')
    reportgroup.add_argument('-ap', help='Show all clients/projects', action='store_true')
    reportgroup.add_argument('-apt', '-listtable', help='Show all clients/projects', action='store_true')
    reportgroup.add_argument('-today', help='Show time tracked today in a table', action='store_true')
    reportgroup.add_argument('-week', help='Show time tracked this week in a table', action='store_true')
    reportgroup.add_argument('-month', help='Show time tracked this month in a table', action='store_true')
    reportgroup.add_argument('-lastmonth', help='Show time tracked last month in a table', action='store_true')
    reportgroup.add_argument('-c', help='Specify a client id to report on', type=str)

    toolsgroup = parser.add_argument_group('Tools')
    toolsgroup.add_argument('-pcomp', help='Autocomplete projects',action='store_true')
    toolsgroup.add_argument('-ccomp', help='Autocomplete clients',action='store_true')
    toolsgroup.add_argument('-mcomp', help='Autocomplete messages',action='store_true')
    toolsgroup.add_argument('-refresh', help='Refresh Caches',action='store_true')
    toolsgroup.add_argument('-st', help='Refresh Caches',action='store_true')


    args = parser.parse_args()

    if args.st:
        print("Stripe testing disabled")
        sys.exit(0)

    if args.refresh:
        refresh_caches()
        sys.exit(0)

    if args.s:
        nowtime = datetime.datetime.now()
        write_start_time(nowtime)
        sleep(1)
        print("Started tracking time.")
        sys.exit(0)

    if args.v:
        running_time = read_start_time()
        if running_time == "Not Tracking":
            print("Not Tracking")
            sys.exit(0)

        timediff = datetime.datetime.now() - running_time
        hours, remainder = divmod(timediff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            formatted_time_diff = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
        else:
            formatted_time_diff = "{:02}:{:02}".format(minutes, seconds)

        if hours == 0 and minutes == 0 and seconds == 0:
            print("Not Tracking")
            sys.exit(0)

        print(""+formatted_time_diff.strip() + "")
        sys.exit(0)

    if args.x:
        print("Track running time")
        running_time = read_start_time()
        timediff = datetime.datetime.now() - running_time
        time_diff_seconds = (datetime.datetime.now() - running_time).total_seconds()
        time_diff_min = int(time_diff_seconds / 60)
        get_projects(use_table=True)
        print("Recording time of ", time_diff_min, " minutes")
        projstr = str(input("Which project?: "))
        if projstr == "":
            print("No project specified, quitting")
            sys.exit(1)

        proj = projstr
        msg = str(input("Message: "))
        print("Tracking time of ", time_diff_min, " minutes to project ", proj, " with message ", msg)

        send_new_time(time_diff_min, proj, msg)
        clear_start_time()
        sys.exit(0)

    if args.clear:
        print("Clearing start time")
        clear_start_time()
        sys.exit(0)

    if args.ap:
        get_projects()
        sys.exit(0)

    if args.pcomp:
        get_project_completions()
        sys.exit(0)

    if args.ccomp:
        get_clients()
        sys.exit(0)

    if args.mcomp:
        if args.p:
            get_message_completions(args.p)
        else:
            get_message_completions()
        sys.exit(0)

    if args.apt:
        get_projects(use_table=True)
        sys.exit(0)

    if args.today:
        if args.c:
            list_today(use_table=True, clientid=args.c)
        else:
            list_today(use_table=True)
        if args.d:
            item_to_delete = item_list[args.d - 1]
            print("Deleting time ", item_to_delete['id'])
            delete_item(item_to_delete['id'])
        sys.exit(0)

    if args.week:
        if args.c:
            list_week(use_table=True, clientid=args.c)
        else:
            list_week(use_table=True)
        if args.d:
            item_to_delete = item_list[args.d - 1]
            print("Deleting time ", item_to_delete['id'])
            delete_item(item_to_delete['id'])
        sys.exit(0)

    if args.month:
        clientid = False
        if args.c:
            clientid = args.c
        list_month(use_table=True, clientid=clientid)

        if args.d:
            item_to_delete = item_list[args.d - 1]
            print("Deleting time ", item_to_delete['id'])
            delete_item(item_to_delete['id'])
        sys.exit(0)

    if args.lastmonth:
        clientid = False
        if args.c:
            clientid = args.c
        list_last_month(use_table=True, clientid=clientid)
        sys.exit(0)

    # We want to add a new time
    if args.n:
        if args.t is None or args.msg is None or args.p is None:
            print("You must include a time, message, and project")
            sys.exit(1)
        duration = "30m"
        if args.t:
            duration = parse_duration(args.t)

        if args.msg:
            noop = 1
        else:
            print("Error: No message specified")

        if args.p:
            print("Project is: ", args.p)
        else:
            print("Error: No project specified")

        newmsg = ' '.join(args.msg)
        print("Adding new time track, time is ", args.t,  " project is ", args.p, " message is ", newmsg)
        send_new_time(duration, args.p, newmsg)
        print("Time tracked successfully.")
        sys.exit(0)

    print("Error: No arguments given.  Use -h for help.")
    parser.print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()

