import json
import time
from datetime import datetime
from multiprocessing import Process, Value

import requests
from flask import Flask, request, make_response, json

# Define shared variables between process
SEND = Value("b", False)
INTERVAL = Value("i", 5)
LAMP01_ON = Value("b", False)

app = Flask(__name__)

lamp_on_timestamp = None


@app.route("/", methods=["GET", "POST"])
def index():
    print(f"request: {request.json}")
    return make_response(json.dumps({"on": "method executed"}), 200)


@app.route("/lamp01", methods=["GET", "POST"])
def lamp01():
    if request.method == "POST":
        data = request.json
        if "switch" in data:
            if SEND.value == False:
                # Turn on the lamp
                SEND.value = True
                LAMP01_ON.value = True
                return make_response(json.dumps({"switch": "Lamp turned on"}), 200)
            elif SEND.value == True:
                # Turn off the lamp
                SEND.value = False
                LAMP01_ON.value = False
                return make_response(json.dumps({"switch": "Lamp turned off"}), 200)
            else:
                return make_response(json.dumps({"error": "Method not allowed"}), 405)
        elif "interval" in data:
            try:
                INTERVAL.value = int(data["interval"])
                return make_response(json.dumps({"interval": "Interval changed"}), 200)
            except:
                return make_response(json.dumps({"error": "Method not allowed"}), 405)
        else:
            return make_response(json.dumps({"error": "Method not allowed"}), 405)


# Function to send data to the iot agent
def send_lamp_data(elapsed_time):
    url = "http://fiware-iot-agent-json:7896/iot/json?k=4jggokgpepnvsb2uv4s40d59ov&i=device001"

    payload = json.dumps({
        "time_on": elapsed_time
    })

    headers = {
        'fiware-service': 'openiot',
        'fiware-servicepath': '/',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except:
        print("Error sending data")


def lamp_timer():
    global lamp_on_timestamp

    while True:
        if LAMP01_ON.value:
            if LAMP01_ON.value:
                if lamp_on_timestamp is None:
                    lamp_on_timestamp = datetime.now()

            elapsed_time = (datetime.now() - lamp_on_timestamp).total_seconds()
            send_lamp_data(elapsed_time)

            # Reset the timestamp every time data is sent
            lamp_on_timestamp = datetime.now()

            time.sleep(INTERVAL.value)
        else:
            lamp_on_timestamp = None


lamp_process = Process(target=lamp_timer).start()

if __name__ == "__main__":
    lamp_timer()
