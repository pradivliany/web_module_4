import socket
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse, unquote_plus
from pathlib import Path
import mimetypes
from datetime import datetime
import json

if not Path("/app/storage/data.json").exists():
    if not Path("/app/storage/").exists():
        Path("/app/storage/").mkdir(parents=True, exist_ok=True)
    try:
        with open("/app/storage/data.json", "w") as file:
            json.dump({}, file)
    except Exception as e:
        print(f"Виникла помилка: {e}")


WEB_PORT, UDP_PORT = 3000, 5000
UDP_IP = "localhost"


class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        match parsed_url.path:
            case "/":
                self.send_html_file("templates/index.html")
            case "/contact":
                self.send_html_file("templates/message.html")
            case _:
                if Path(parsed_url.path[1:]).exists():
                    self.send_static()
                else:
                    self.send_html_file("templates/error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as html_file:
            self.wfile.write(html_file.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        (
            self.send_header("Content-type", mt[0])
            if mt
            else self.send_header("Content-type", "text/plain")
        )
        self.end_headers()
        with open(f".{self.path}", "rb") as static_file:
            self.wfile.write(static_file.read())

    def do_POST(self):
        count_bytes_to_read = int(self.headers["Content-Length"])
        data = self.rfile.read(count_bytes_to_read)
        normal_data = unquote_plus(data.decode())

        #  створюю клієнтський сокет UDP який байти перешле на сокет-сервер
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(normal_data.encode(), (UDP_IP, UDP_PORT))
        sock.close()

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run_socket_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    try:
        while True:
            data, address = sock.recvfrom(1024)
            time_now = datetime.now()
            data_dict = {
                k: v for k, v in [el.split("=") for el in data.decode().split("&")]
            }

            # зчитую, що вже є в data.json
            with open("storage/data.json", "r") as json_file:
                data_from_json_file = json.load(json_file)

            # додаю отримане через сокет повідомлення
            data_from_json_file[str(time_now)] = data_dict

            # записую в data.json новий вміст
            with open("storage/data.json", "w", encoding="utf-8") as json_file:
                json.dump(data_from_json_file, json_file, indent=2, ensure_ascii=False)
    except KeyboardInterrupt:
        print("Destroy server...")
    finally:
        sock.close()


if __name__ == "__main__":
    web_server = HTTPServer(("", WEB_PORT), HTTPHandler)

    # створюю і запускаю потік для веб-застосунку
    web_server_thread = Thread(target=web_server.serve_forever)
    web_server_thread.start()

    # створюю і запускаю потік для сокет-серверу
    socket_server_thread = Thread(target=run_socket_server, args=[UDP_IP, UDP_PORT])
    socket_server_thread.start()

    time.sleep(0.5)
