from tinydb import TinyDB, Query
import datetime

db = TinyDB('db.json')
User = Query()


def is_in_db(dic_data):
    if db.search(User.username == dic_data["username"]) == []:
        return False
    else:
        return True


def add_entry(dic_data):
    db.insert(dic_data)


def remove_entry(username):
    db.remove(User.username == username)


def update_db(dic_data):
    db.update(dic_data, User.username == dic_data["username"])

def get_entry(username):
    return db.search(User.username == username)[0]

def get_all_entries(weekday, start_time):
    queue = []
    for i in range(1, 8):
        result = db.search( (User["weekday_"+str(i)] == weekday) & (User["start_time_"+str(i)] == start_time))
        if result != []:
            for entry in result:
                queue.append(
                    {"username": entry["username"], "password": entry["password"], "location": entry["location_"+str(i)]})
    return queue

def log_time():
    now = datetime.datetime.today() + datetime.timedelta(hours=2)
    return '['+now.strftime("%H:%M:%S")+']'