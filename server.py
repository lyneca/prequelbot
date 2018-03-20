from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

PAT = os.environ.get('MESSENGER_PAGE_ACCESS_TOKEN')
MVT = os.environ.get('MESSENGER_VALIDATION_TOKEN')

@app.route('/webhook', methods=['GET'])
def handle_verification():
    print("Handling verification...")
    if request.args.get('hub.verify_token', '') == MVT:
        return request.args.get('hub.challenge', '')
    else:
        print("Verification failed!")
        return "Error, wrong validation token"

@app.route('/webhook', methods=['POST'])
def handle_messages():
    print("Handling messages...")
    payload = request.get_data()
    print(payload)
    for sender, message in messaging_events(payload):
        print("Incoming from {}: {}".format(sender, message))
        send_message(PAT, sender, message)
    return "ok"

def messaging_events(payload):
    """
    Generate types of (sender_id, message_text) from the provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        if "message" in event and "text" in event["message"]:
            yield event["sender"]["id"], event["message"]["text"].encode("unicode_escape")
        else:
            yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
    """
    Send the message text to recipient with id `recipient`
    """

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {"text": text.decode("unicode_escape")}
        }),
        headers={"Content-Type": "application/json"}
    )
    if r.status_code != requests.codes.ok:
        print(r.text)

