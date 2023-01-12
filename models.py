from configs import DATA_FILE
from datetime import datetime
import json


def model_get_user_info(message, data_file=DATA_FILE):
    with open(data_file, 'r') as file:
        data = json.loads(file.read())
        data["user_number"] += 1
        
    with open(data_file, 'w') as file:
        file.write(json.dumps(data))        

    user = {
        "Id": data.get("user_number"),
        "User_Id": message.from_user.id,
        "Username": message.from_user.username,
        "First_Name": message.from_user.first_name,
        "Last_Name": message.from_user.last_name,
        "Date_Since": datetime.now().strftime('%d.%m.%Y %H:%M')
    }

    return user


def model_get_event_info(event):
    event = {
        "Event_Id": event.get("Event_Id"),
        "Event_Name": event.get("Event_Name"),
        "Description": event.get("Description") if event.get("Description") else "No description provided",
        "Date": event.get("Date") if event.get("Date") else "In process...",
        "Place": event.get("Place") if event.get("Place") else "In process...",
        "Visitors": event.get("Visitors")
    }

    return event


def model_get_reply_info(event_id, user_id, reply, data_file=DATA_FILE):
    with open(data_file, 'r') as file:
        data = json.loads(file.read())
        data["reply_number"] += 1

    with open(data_file, 'w') as file:
        file.write(json.dumps(data))

    reply = {
        "Id": data.get("reply_number"),
        "User_Id": user_id,
        "Event_Id": event_id,
        "Date_Reply": datetime.now().strftime('%d.%m.%Y %H:%M'),
        "Reply": reply
    }

    return reply