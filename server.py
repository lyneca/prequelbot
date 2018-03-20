from flask import Flask, request
import json
import requests
import os
import random

app = Flask(__name__)

PAT = os.environ.get('MESSENGER_PAGE_ACCESS_TOKEN')
MVT = os.environ.get('MESSENGER_VALIDATION_TOKEN')
reddit_headers = {
    'User-Agent': 'facebook:prequelmemesbot:v1.0.0 (by /u/lyneca)'
}

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
    return "ok"

def messaging_events(payload):
    """
    Generate types of (sender_id, message_text) from the provided payload.
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]
    for event in messaging_events:
        sender = event['sender']
        if "message" in event and "text" in event["message"]:
            message = event['message']['text']
            if 'random' in message.lower():
                if 'top' in message.lower():
                    r = requests.get('https://reddit.com/r/prequelmemes/top.json', headers=reddit_headers).json()
                else:
                    r = requests.get('https://reddit.com/r/prequelmemes/new.json', headers=reddit_headers).json()
                post = random.choice(r['data']['children'])['data']
                message = "{} (/u/{}, {} points)".format(post['title'], post['author'], post['score'])
                send_message(PAT, sender['id'], message)
                send_image(PAT, sender['id'], post['url'])
                yield sender["id"], post['title']
            elif 'newest' in message.lower():
                r = requests.get('https://reddit.com/r/prequelmemes/new.json', headers=reddit_headers).json()
                post = r['data']['children'][0]
                yield event["sender"]["id"], event["message"]["text"]
        else:
            ...
            #  yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
    """
    Send the message text to recipient with id `recipient`
    """

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {
                "text": text,
            }
        }),
        headers={"Content-Type": "application/json"}
    )
    if r.status_code != requests.codes.ok:
        print(r.text)

def send_image(token, recipient, link):
    """
    Send the image url to recipient with id `recipient`
    """

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
        params={"access_token": token},
        data=json.dumps({
            "recipient": {"id": recipient},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "open_graph",
                        "elements": [
                            {
                                "url": link
                            }
                        ]
                    }
                }
            }
        }),
        headers={"Content-Type": "application/json"}
    )
    if r.status_code != requests.codes.ok:
        print(r.text)

