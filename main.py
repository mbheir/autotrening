#!/usr/bin/python3
import threading
import fsm
# import http_server
import flask_server
from time import sleep

def main():
    # s = threading.Thread(target=flask_server.start_server)
    # s.start()

    f = threading.Thread(target=fsm.start_fsm)
    f.start()
    while True:
        sleep(1)

    f.join()
    # s.join()





if __name__ == "__main__":
    main()