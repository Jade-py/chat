from locust import HttpUser, User, task, between
from websocket import create_connection
import requests


class WebSocketUser(User):
    wait_time = between(1, 2)

    def on_start(self):
        # First, authenticate and get sessionid or token
        session = requests.Session()
        resp = session.post("http://127.0.0.1:8000/login/", json={"username": "0000", "password": "0000"})

        if resp.status_code == 200:
            cookies = session.cookies.get_dict()
            cookie_header = '; '.join([f'{key}={value}' for key, value in cookies.items()])
            headers = {
                "Cookie": cookie_header,
                "Origin": "http://127.0.0.1:8000",
            }
            self.ws = create_connection("ws://127.0.0.1:8000/ws/chat/", header=headers)
        else:
            print("Login failed:", resp.status_code, resp.text)

    @task
    def send_message(self):
        try:
            self.ws.send("Hello")
            print(self.ws.recv())
        except Exception as e:
            print("WebSocket error:", e)

    def on_stop(self):
        self.ws.close()


class DjangoUser(HttpUser):
    def on_start(self):
        self.client.post('/login/', json={"username":"0000", "password":"0000"})

    @task()
    def get_page(self):
        self.client.get('/chat/')