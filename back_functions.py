from datetime import date, datetime, timedelta
import gspread
from models import *

# Globals
WOORKBOOK_NAME = "Events"
EVENTS_SHEET_NAME = "Events"
USERS_SHEET_NAME = "Users"
REPLY_SHEET_NAME = "Reply"

EVENTS_SHEET_COLUMNS = {
    "Event_Id":1, 
    "Event_Name":2,
    "Description":3,
    "Date":4,
    "Place":5,
    "Is_Active":6,
    "Limit":7,
    "Visitors":8
}

USERS_SHEET_COLUMNS = {
    "Id":1,
    "User_Id":2,
    "Username":3,
    "First_Name":4,
    "Last_Name":5,
    "Date_Since":6
}

REPLY_SHEET_COLUMNS = {
    "Id":1,
    "User_Id":2,
    "Event_Id":3,
    "Date_Reply":4,
    "Reply":5
}

# Connect to Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
GOOGLE_CLIENT = gspread.service_account("gs_sheets_key.json", scopes)


# Functions
def google_get_sheet(workbook_name, sheet_name):
    woorkbook = GOOGLE_CLIENT.open(workbook_name)
    worksheet = woorkbook.worksheet(sheet_name)
    return worksheet


def google_get_all_records(workbook_name, sheet_name):
    worksheet = google_get_sheet(workbook_name, sheet_name)
    records = worksheet.get_all_records()
    return records


def callback_to_string(dictionary):
    callback = json.dumps(dictionary)
    return callback


def callback_to_json(string_dictionary):
    callback = json.loads(string_dictionary)
    return callback


def back_add_new_user(message):
    user = model_get_user_info(message)
    worksheet = google_get_sheet(WOORKBOOK_NAME, USERS_SHEET_NAME)
    
    for key, val in user.items():
        worksheet.update_cell(user.get("Id") + 1, USERS_SHEET_COLUMNS[key], val) 


def back_check_event(event):
    if event.get("Visitors") > event.get("Limit"):
        return False

    if event.get("Is_Active") == "no":
        return False

    if event.get("Date") >= datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
        print('NO')
        return False

    return True


def back_get_actual_events():
    events = google_get_all_records(WOORKBOOK_NAME, EVENTS_SHEET_NAME)
    actual_events = [event for event in events if back_check_event(event)]   
    return actual_events


def back_get_user_events_ids(user_id):
    events = google_get_all_records(WOORKBOOK_NAME, REPLY_SHEET_NAME)
    user_events_ids = [str(event.get("Event_Id")) for event in events if str(event.get("User_Id")) == str(user_id)]
    return user_events_ids


def back_search_new_event(message):
    # Get user events
    user_id = message.from_user.id
    user_events_ids = back_get_user_events_ids(user_id)

    # Get actual events
    actual_events = back_get_actual_events()

    # Find diff
    events_to_send = [event for event in actual_events if str(event.get("Event_Id")) not in user_events_ids]
    if bool(events_to_send):
        return events_to_send[0]
    else:
        return {}


def back_check_user(message):
    user_id = message.from_user.id
    worksheet = google_get_sheet(WOORKBOOK_NAME, USERS_SHEET_NAME)
    users_ids = worksheet.col_values(USERS_SHEET_COLUMNS["User_Id"])
    is_user_exists = True if str(user_id) in users_ids else False
    return is_user_exists


def back_write_reply(event_id, user_id, reply):
    reply = model_get_reply_info(event_id, user_id, reply)

    worksheet = google_get_sheet(WOORKBOOK_NAME, REPLY_SHEET_NAME)
    for key, val in reply.items():
        worksheet.update_cell(reply.get("Id")+1, REPLY_SHEET_COLUMNS[key], val)


def back_update_event(event_id):
    events = google_get_all_records(WOORKBOOK_NAME, EVENTS_SHEET_NAME)
    event = [event for event in events if str(event.get("Event_Id")) == str(event_id)][0]
    col = EVENTS_SHEET_COLUMNS.get("Visitors")
    row = event.get("Event_Id") + 1
    visitors = str(event.get("Visitors") + 1)

    worksheet = google_get_sheet(WOORKBOOK_NAME, EVENTS_SHEET_NAME)
    worksheet.update_cell(row, col, visitors)


def back_get_users_registrations(user_id):
    replies = google_get_all_records(WOORKBOOK_NAME, REPLY_SHEET_NAME)
    user_registrations = [reply for reply in replies if reply.get("User_ID")==user_id and reply.get("Reply")=="register"]
    return user_registrations


def back_check_event_time(event):
    date_diff = datetime.strptime(event.get("Date"), '%Y.%m.%d %H:%M:%S') - datetime.now()
    alarm = 2 >= date_diff.total_seconds() // 3600 >= 0
    return alarm


def back_alarm_event(message):
    user_id = message.user_id
    user_registrations = back_get_users_registrations(user_id)
    events = google_get_all_records(WOORKBOOK_NAME, EVENTS_SHEET_NAME)
    user_events = [event for event in events if event.get("Event_Id") in [reg.get("Event_Id") for reg in user_registrations]]
    events_alarm = [event for event in user_events if back_check_event_time(event)]
    return events_alarm
    
