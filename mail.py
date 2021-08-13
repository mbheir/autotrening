import imaplib
import email
from email.header import decode_header
import datetime
import database


def fetch_passwords():
    username = "auto.trening.sexy@gmail.com"
    password = "**********"

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)

    status, num_msgs = imap.select("INBOX")
    num_msgs = int(num_msgs[0])

    N = 3
    timeout = datetime.datetime.today() - datetime.timedelta(minutes=1)
    # for id in range(num_msgs, num_msgs-N, -1):
    id = num_msgs
    while True:
        _ , msg = imap.fetch(str(id), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, _ = decode_header(msg["Subject"])[0]

                body = msg.get_payload()
                body_list = body.split()

                date_tuple = email.utils.parsedate_tz(msg['Date'])
                if date_tuple:
                    local_date = datetime.datetime.fromtimestamp(
                        email.utils.mktime_tz(date_tuple))
                    # print("Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S"))
                if local_date < timeout:
                    return
                

                username = body_list[body_list.index("Brukernavn:")+1]
                password = body_list[body_list.index("Passord:")+1]
                
                if database.is_in_db({"username": username}):
                    database.update_db({"username": username,"password": password})
                    print(f"Updated password for {username}")

        id -= 1
