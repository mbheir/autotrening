from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import server
import database
import ssl



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        
        self.end_headers()
        f = open("html/skjema.html","r")
        html = f.read()
        f.close()

        self.wfile.write(bytes(html, "utf8"))


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        html = server.respond(body.decode('utf-8'))
        self.wfile.write(bytes(html, "utf8"))


def start_http_server():
    httpd = HTTPServer(('c68eb0c.online-server.cloud', 80), SimpleHTTPRequestHandler)
    # httpd.socket = ssl.wrap_socket(httpd.socket, certfile='./fullchain.pem', keyfile='./privkey.pem', server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)
    print("##HTTP SERVER RUNNING##")
    httpd.serve_forever()

