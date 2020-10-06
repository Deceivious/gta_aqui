import os
from time import sleep
from server.flask_app import app
from server.env import IP_ADDRESS, PORT


def start_server():
    try:
        os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\\windows'), 'temp']))
    except:
        print("Administrator privilege required. Shutting down...")
        sleep(5)
        exit()
    else:
        app.run(IP_ADDRESS, PORT, threaded=False)


if __name__ == "__main__":
    start_server()
