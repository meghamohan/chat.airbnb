from flask import Flask, request
import json
import requests

app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAACMZCo0BAbEBAJfVRchc79VU6mbuxn8nrzqquJTh52WhhKKePPd04vsKSy3j75GRjTZCNfDeOwZCaFFDKqpbTPPDZBBQmHprxgZAcUK0HCsS4oNWTWXbkc3BahCt15elGqVpNlfQ7UGB5PwedJwU3C62jKYSvbIe3rVmIfswbq86ccs3R5Y6'

@app.route('/', methods=['GET'])
def handle_verification():
  print("Handling Verification.")
  if request.args.get('hub.verify_token', '') == 'hbnb_verification_token':
    print("Verification successful!")
    return request.args.get('hub.challenge', '')
  else:
    print("Verification failed!")
    return 'Error, wrong validation token'

@app.route('/', methods=['POST'])
def handle_messages():
  print("Handling Messages")
  payload = request.get_json()
  for sender, message in messaging_events(payload):
    print("Incoming from %s: %s" % (sender, message))
    send_message(PAT, sender, message)
  return "ok"


def constructMsg(response):
    attachment = {}
    payload = {}
    elements = []

    if len(response) > 5:
        response = response[:5]
    for place in response:
          sub_ele = {}
          buttons = []
          subbuttons = {}
          sub_ele['title'] = place['name']
          sub_ele['subtitle'] = place['price_by_night']
          sub_ele['image_url'] = "https://pbs.twimg.com/profile_images/378800000138581024/9733bcb490d916fcd2feb5d0abef0cbc_400x400.jpeg"
          subbuttons['type'] = "web_url"
          subbuttons['url'] = "https://airbnb.com"
          subbuttons["title"] = "View Website"
          subbuttons["webview_height_ratio"] = "tall"
          buttons.append(subbuttons.copy())
          sub_ele['buttons'] = buttons
          elements.append(sub_ele.copy())



    """sub_ele['title'] = "Welcome to Peters Hats"
    sub_ele['subtitle'] = "We got the right hat for everyone."
    sub_ele['image_url'] = "https://pbs.twimg.com/profile_images/378800000138581024/9733bcb490d916fcd2feb5d0abef0cbc_400x400.jpeg"
    subbuttons['type'] = "web_url"
    subbuttons['url'] = "https://airbnb.com"
    subbuttons["title"] = "View Website"
    subbuttons["webview_height_ratio"] = "tall"
    buttons.append(subbuttons.copy())
    sub_ele['buttons'] = buttons
    elements.append(sub_ele.copy())"""

    #elements.append(subele.copy())
    payload['elements'] = elements
    payload['template_type'] = "generic"
    attachment['type'] = "template"
    attachment['payload'] = payload
    return attachment
    


def searchForLocation(name, sDict, cities_list):
    for k, v in sDict.items():
        if k == name:
            cities_list.append(v)               

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  messaging_events = payload["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:

      url1 = 'http://api.megha.space/api/v1/states_ids/'
      r1 = requests.get(url = url1)
      data1 = r1.json()

      finalDict = {}
      cities_list = []
      amn_list = []

      for i in event["message"]["nlp"]["entities"]["location"]:
        searchForLocation(i['value'], data1, cities_list)      
      finalDict["states"] = cities_list

      url2 = 'http://api.megha.space/api/v1/places_search/'
      r2 = requests.post(url = url2, data = json.dumps(finalDict), headers={'content-type': 'application/json'})
      data2 = r2.json()

      yield event["sender"]["id"], json.dumps(constructMsg(data2)).encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """
  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      #"message": {"text": text.decode('unicode_escape')}
      "message": {"attachment": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})

  finalDict = {}
  cities_list = []
  amn_list = []
  if r.status_code != requests.codes.ok:
    print(r.text)

if __name__ == '__main__':
  app.run()
