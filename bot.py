from telebot import TeleBot, types
import gspread
from configs import *
from messages import *
from back_functions import *

# INIT 
bot = TeleBot(TELEGRAMM_BOT_TOKEN)


# Connect to Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
gs_client = gspread.service_account("gs_sheets_key.json", scopes)


# INLINE KEYBORD\BUTTONS
inlineKB = types.InlineKeyboardMarkup
inlineBTN = types.InlineKeyboardButton

# BOT functions
@bot.message_handler(commands=['help'])
def bot_send_help(message):
    """
    Bot help command
    """
    bot.send_message(message.chat.id, HELP_MSG, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def bot_send_welcome(message):
    """
    Bot entry point
    """

    # Collect user info
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    name = [name for name in [username, first_name, last_name] if name][0]
    welcome_msg = WELCOME_MSG.format(username=name)

    # Send welcome msg    
    btn1 = inlineBTN("Let's go \U0001F680", callback_data="go")
    btn2 = inlineBTN("Die 🪦", callback_data="die")
    
    reply_kb = inlineKB(row_width=2)
    reply_kb.add(btn1, btn2)
    bot.send_message(message.chat.id, welcome_msg, reply_markup=reply_kb)


@bot.callback_query_handler(func=lambda x: x.data == "die")
def bot_send_first_event(call):
    """
    If user has choosen 'Die'
    """
    animation = open("pressf.gif", "rb")
    bot.send_animation(call.message.chat.id, animation=animation, caption=DIE_MSG)


@bot.callback_query_handler(func=lambda x: x.data == "go")
def bot_send_first_event(call):
    """
    If user has choosen 'Let's go'
    """

    # Send first event
    is_user_exists = back_check_user(call)
    
    if not is_user_exists:
        back_add_new_user(call)

    new_event = back_search_new_event(call)
    if bool(new_event):
        event = model_get_event_info(new_event)
        event_msg = EVENT_MSG_TEMPLATE.format(**event)

        callback1 = callback_to_string({"reply":"register", "event_id":event.get("Event_Id")})
        callback2 = callback_to_string({"reply":"next", "event_id":event.get("Event_Id")})
        btn1 = inlineBTN("Register me \U00002705", callback_data=callback1)
        btn2 = inlineBTN("Next \U000027A1", callback_data=callback2)
        
        reply_kb = inlineKB(row_width=2)
        reply_kb.add(btn1, btn2)
        bot.send_message(call.message.chat.id, event_msg, parse_mode="HTML", reply_markup=reply_kb)
    else:
        bot.send_message(call.message.chat.id, NO_EVENT_MSG, parse_mode="HTML")

    
@bot.callback_query_handler(func=lambda x: "register" in x.data)
def bot_approve_registration(call):
    # Write user's reply
    callback_data = callback_to_json(call.data)
    back_write_reply(callback_data.get("event_id"), call.from_user.id, callback_data.get("reply"))

    # Update event info
    back_update_event(callback_data.get("event_id"))

    # Send approve msg
    callback1 = callback_to_string({"reply":"show_more"})
    callback2 = callback_to_string({"reply":"no_thanks"})
    btn1 = inlineBTN("Show more \U00002705", callback_data=callback1)
    btn2 = inlineBTN("No. Thanks \U0001F645", callback_data=callback2)
    reply_kb = inlineKB(row_width=2)
    reply_kb.add(btn1, btn2)
    bot.send_message(call.message.chat.id, APPROVE_REGISTRATION_MSG, parse_mode="HTML", reply_markup=reply_kb)


@bot.callback_query_handler(func=lambda x: "next" in x.data or "show_more" in x.data)
def bot_send_next_event(call):
    # Write user's reply
    callback_data = callback_to_json(call.data)
    back_write_reply(callback_data.get("event_id"), call.from_user.id, callback_data.get("reply"))

    # Search new event
    new_event = back_search_new_event(call)
    if bool(new_event):
        event = model_get_event_info(new_event)
        event_msg = EVENT_MSG_TEMPLATE.format(**event)

        # Send new event
        callback1 = callback_to_string({"reply":"register", "event_id":event.get("Event_Id")})
        callback2 = callback_to_string({"reply":"next", "event_id":event.get("Event_Id")})
        btn1 = inlineBTN("Register me \U00002705", callback_data=callback1)
        btn2 = inlineBTN("Next \U000027A1", callback_data=callback2)
        reply_kb = inlineKB(row_width=2)
        reply_kb.add(btn1, btn2)
        bot.send_message(call.message.chat.id, event_msg, parse_mode="HTML", reply_markup=reply_kb)
    else:
        bot.send_message(call.message.chat.id, NO_EVENT_MSG, parse_mode="HTML")


@bot.callback_query_handler(func=lambda x: "no_thanks" in x.data)
def bot_reply_no_thanks(call):
    callback = callback_to_string({"reply":"show_more"})
    btn1 = inlineBTN("Get new events \U0001F680", callback_data=callback)
    
    reply_kb = inlineKB(row_width=1)
    reply_kb.add(btn1)
    bot.send_message(call.message.chat.id, NO_THANKS_MSG, parse_mode="HTML", reply_markup=reply_kb)


@bot.message_handler(content_types=["text"])
def bot_reply_text_msg(message):
    bot.send_message(message.chat.id, SORRY_MSG, reply_to_message_id=message.id)
    bot.send_message(message.chat.id, HELP_MSG)


@bot.message_handler(func=lambda x: bool(back_alarm_event(x)) == True)
def bot_alarm_event(message):
    events_alarm = back_alarm_event(message)
    msg = EVENT_ALARM_MSG
    for event in events_alarm:
        msg += EVENT_ALARM_TEMPLATE_MSG.format(**event)
        msg += '\n' + '-'*10 + '\n'

    bot.send_message(message.chat.id, msg)


if __name__ == '__main__':
    bot.polling()
