import datetime
import traceback
import asyncio
import aiohttp
from requests import Session
from bs4 import BeautifulSoup as bs
from aiohttp import ClientSession, ClientConnectorError
from database import log_time



def extract_event_id(s, location, weekday, start_time):
    [date, delta_week] = get_date_of_upcoming_weekday(weekday)
    url = get_event_url(location, delta_week)
    web_page = s.get(url)
    web_page_parsed = bs(web_page.content, "html.parser")

    #DEBUG
    if weekday == "Lordag":
        weekday = "Lørdag"
    if weekday == "Sondag":
        weekday = "Søndag"


    div_target_day = web_page_parsed.find(
        "li", text=weekday+" "+date).find_all_next("li")
    

    for div_trening in div_target_day:

        div_egentrening = div_trening.find("div", {"class": "clock border"})

        if is_correct_time(div_egentrening.get_text(strip=True), start_time):
            for element in div_egentrening.parent.parent.parent():
                return element.get('id')[6:14]

    raise Exception("Failed to get ID of Event, no event_url was found")


def get_event_url(location, delta_week):
    code = {"Gløs": "306", "Glos": "306", "Moholt": "540",
            "Dragvoll": "307", "Portalen": "308", "DMMH": "402"}
    url_base = "https://ibooking.sit.no/index.php?location="
    if delta_week:
        url = url_base+code[location]+"&type=13&week=%2B1+weeks"
    else:
        url = url_base+code[location]+"&type=13&week=now"
    return url


def is_correct_time(time, start_time):
    return time[0:5] == start_time


def get_id_from_string_url(string_url):
    event_id_str = string_url.split("index.php?page=reservation&aid=")[1]
    assert int(event_id_str), "Event ID_invalid, not an int"
    return event_id_str


def get_date_of_upcoming_weekday(weekday):
    today = datetime.datetime.today()
    today_weekday = today.weekday()
    weekDays = ["Mandag", "Tirsdag", "Onsdag",
                "Torsdag", "Fredag", "Lordag", "Sondag"]
    target_weekday = weekDays.index(weekday)

    if target_weekday > today_weekday:
        delta_day = target_weekday - today_weekday
        delta_week = 0
    else:
        delta_day = 7 - (today_weekday - target_weekday)
        delta_week = 1

    target_date = today + datetime.timedelta(days=delta_day)

    return [target_date.strftime("%d/%m"), delta_week]


def print_error_details(location, username, weekday, start_time, error):
    print("\nERROR!")
    print("username: " + username)
    print("weekday: "+weekday)
    print("start time: "+start_time)
    print("location: "+location)
    print("error message: "+error+"\n")
    traceback.print_exc()


async def login_and_book_entry(entry, weekday, start_time, event_ids):
    login_url = "https://ibooking.sit.no/index.php?page=login"
    username = entry["username"]
    password = entry["password"]
    location = entry["location"]
    
    async with ClientSession() as session:
        try:
            print("sending login request for: "+username)
            login_page = await session.request(method="GET", url=login_url)
            login_data = {"action": "login", "[hidden_fields.name]": "",
                        "cookiechk": 1, "username": username, "password": password}
            async with session.post(login_url, data=login_data) as login_response:
                login_response_text = await login_response.text() #awaiting before moving further
                if str(login_response.url) == "https://ibooking.sit.no/index.php?page=login":
                    raise Exception(
                        "Failed to login to ibooking, check username and password. The respond url was: "+str(login_response.url))
            print("Login sucess for: "+entry["username"])
        except Exception as error:
            print("Login error: " + entry["username"], end=' ')
            print(error)
            return
        try:
            booking_id = event_ids[location]
            booking_url = "https://ibooking.sit.no/index.php?page=reservation&aid=" + booking_id
            booking_data = {"page": "reservation", "action": "confirm_reservation",
                            "aid": booking_id, "bid": "", "submit": "Reserver"}
            async with session.post(booking_url, data=booking_data) as booking_response:
                booking_response_text = await booking_response.text() #awaiting before moving further
            print(log_time()+" Booking success for: "+username+"at ->"+weekday+" "+start_time+" "+location)
        except Exception as error:
            print(log_time()+" Booking error: " + entry["username"], end=' ')
            print(error)




async def make_concurrent_bookings(queue, weekday, start_time, event_ids):
    post_tasks = []
    for entry in queue:
        post_tasks.append(login_and_book_entry(entry, weekday, start_time, event_ids))
    await asyncio.gather(*post_tasks)


def request_SMS_passoword(username):
    url = "https://ibooking.sit.no/index.php?page=password&login_redirect=1"
    with Session() as s:
        try:
            login_page = s.get(url)
            payload = {"action": "register", "[hidden_fields.name]": "", "user_email": username}
            s.post(url,payload)
        except Exception as exp:
            print("Error requesting new SMS-password")