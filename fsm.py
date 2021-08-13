from socket import error
from requests.sessions import Session, default_headers, session
import time
import datetime
import asyncio

import database
import booking
import mail




def sleep_tminus(t_minus,target_datetime):
    now = datetime.datetime.today() + datetime.timedelta(hours=2)
    wake_up = target_datetime - datetime.timedelta(days=2,minutes=t_minus)
    delta_t = (wake_up-now).total_seconds()
    if delta_t < 0:
        print("skipping sleep, delta seconds was: "+str(delta_t))
        return
    print(database.log_time()+" FSM: sleeping util "+wake_up.strftime("%H:%M"))
    time.sleep(delta_t)




def get_target_time(now,hour_divide):
    hour = now.strftime("%H")
    for i in range(hour_divide):
        if i == hour_divide-1:
            hour = (now + datetime.timedelta(hours=1)).strftime("%H")
            time_obj = datetime.time.fromisoformat(hour+":"+"00")
            break
        if int(now.strftime("%M")) in range(int(60/hour_divide*i),int(60/hour_divide*(i+1))):
            time_obj = datetime.time.fromisoformat(hour+":"+str(int(60/hour_divide*(i+1))))
            break
    
    target_datetime = datetime.datetime.combine(now.date() + datetime.timedelta(days=2),time_obj)

    weekDays = ["Mandag", "Tirsdag", "Onsdag",
                "Torsdag", "Fredag", "Lordag", "Sondag"]
    target_weekday = weekDays[target_datetime.weekday()]

    return target_weekday, target_datetime.strftime("%H:%M"), target_datetime

def update_event_IDs(weekday, start_time):
    event_ID_dic = {"Glos": "", "Dragvoll": "","Moholt": "", "Portalen": "", "DMMH": ""}
    success_list_by_location = []
    with Session() as s:
        for location,ID in event_ID_dic.items():
            try:
                event_ID_dic[location] = booking.extract_event_id(s, location, weekday, start_time)
                success_list_by_location.append(location)
            except Exception as ex:
                pass
    if success_list_by_location != []:
        print(database.log_time()+" FSM: Extracted ID for: ", end='')
        print(success_list_by_location)
    return event_ID_dic

def handle_bookings(weekday, start_time, event_ID_dic):
    print(database.log_time()+" FSM: Booking for "+weekday+" "+start_time)
    queue = database.get_all_entries(weekday, start_time)

    if queue == []:
        print(database.log_time()+" FSM: No entries for " +
              weekday+" "+start_time+" in database")

    asyncio.run(booking.make_concurrent_bookings(queue,weekday,start_time,event_ID_dic))


def update_passwords(weekday,start_time):
    queue = database.get_all_entries(weekday, start_time)
    for entry in queue:
        booking.request_SMS_passoword(entry["username"])
        print("sending sms request")
    time.sleep(30) #adding some time to make sure email arrived
    mail.fetch_passwords()


def start_fsm():
    print(database.log_time()+" #ENTERING FSM#")
    while True:
        # server running in UTC, adjusting to UTC+2
        cycle_start = datetime.datetime.today() + datetime.timedelta(hours=2)
        weekday, target_time, target_datetime = get_target_time(cycle_start,2) #dividing the hour by two, meaning booking every 30minutes


        print(weekday,target_time)
        event_ID_dic = update_event_IDs(weekday, target_time)
        print(event_ID_dic)
        
        sleep_tminus(5,target_datetime)

        print("Updating passwords")
        update_passwords(weekday,target_time)

        sleep_tminus(0,target_datetime)

        handle_bookings(weekday, target_time, event_ID_dic)

