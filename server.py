import datetime
from socket import *
from bs4 import BeautifulSoup as bs
import database
import traceback




def put_in_database(valid_data):
    if database.is_in_db(valid_data):
        database.update_db(valid_data)
        print(database.log_time()+" SERVER LOG: updated entry in database\n")
        # kanskje ikke ha at den printer passord etterhvert...
        print(valid_data, end="\n")
    else:
        database.add_entry(valid_data)
        print(database.log_time()+" SERVER LOG: added new entry to database\n")
        print(valid_data, end="\n")




def format_input_fields(dic):
    for index in range(1, 8):
        time = dic["start_time_"+str(index)]
        if '%3A' in time:
            first, second = time.split("%3A")
            dic["start_time_"+str(index)] = first+":"+second

        username = dic["username"]
        if username[0:3] == "%2B":
            dic["username"] = "+"+username[3:]
    return dic


def get_status_html(valid_data):
    if database.is_in_db(valid_data):
        dic = database.get_entry(valid_data["username"])
        # if dic["password"] == valid_data["password"]:
        if len(dic)==18: #For å sjekke om det er sendt 3/5 treninger.
            f = open("html/status_5.html","r")
            html = f.read().format(**dic)
            f.close()
        else:
            f = open("html/status_7.html","r")
            html = f.read().format(**dic)
            f.close()
        return html

    return "<!DOCTYPE html><html lang=no><head></head><body><h4>ERROR: Mobilnummer / passord feil, eller så finnes ikke bruker i database.</h4><div><p></body></html>\r\n"


def get_confirmation_html(valid_data):
    if ((len(valid_data["username"]) == 8) or (len(valid_data["username"]) == 12)):

        put_in_database(valid_data)
        return "<!DOCTYPE html><html lang=no><head></head><body><h1>Success!</h1><p>Dersom mobilnummeret og passordet du oppga er riktig, vil du nå bli autmatisk meldt opp til timene du anga.<div> Husk at dersom du ikke skal på timen likevel må du melde deg av minst en time før på sit.no. God Trening!<div><p></body></html>\r\n"
    else:
        username = valid_data["username"]
        return f"<!DOCTYPE html><html lang=no><head></head><body><h4>ERROR: Mobilnummer ikke riktig format: {username}</h4><div><p></body></html>\r\n"
def respond(message):
    valid_data = format_input_fields(message)
    if valid_data["submit"] == "Sjekk Status":
        html = get_status_html(valid_data)
    else:
        html = get_confirmation_html(valid_data)
    return html


def start_server():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverPort = 8000
    serverSocket.bind(('', serverPort))
    print('###SERVER RUNNING###')

    while True:
        print(database.log_time()+' READY TO RECIEVE...\r\n')
        serverSocket.listen(6)
        connectionSocket, addr = serverSocket.accept()

        try:
            message = connectionSocket.recv(1024).decode('utf-8')

        except:
            print(database.log_time()+"SERVER ERROR: tilkoblingsfeil\n")

        try:
            print(message[0:4])
            if message[0:3] == "GET":
                raise Exception("Ignoring GET")
            print(message)
            respond(message, connectionSocket)

        except Exception as error:
            print(database.log_time() +
                  "SERVER ERROR: kunne ikke tolke streng\n->", end="")
            print(error, end="\n")
            traceback.print_exc()
            connectionSocket.close()
