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
  print(payload)
  for sender, message, txtOutput in messaging_events(payload):
    print("Incoming from %s: %s %s" % (sender, message, str(txtOutput)))
    send_message(PAT, sender, message, txtOutput)
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
          if place['name'] == "SORRY!!!":
            sub_ele['image_url'] = "https://emojipedia-us.s3.amazonaws.com/thumbs/120/samsung/100/crying-face_1f622.png"
          else:
            sub_ele['image_url'] = "https://pbs.twimg.com/profile_images/378800000138581024/9733bcb490d916fcd2feb5d0abef0cbc_400x400.jpeg"
          subbuttons['type'] = "web_url"
          if place.get('id'):
            subbuttons['url'] = "http://megha.space/detailpage/" + place['id']
          else:
            subbuttons['url'] = "http://megha.space/eoyProject"
          subbuttons["title"] = "View Website"
          subbuttons["webview_height_ratio"] = "tall"
          buttons.append(subbuttons.copy())
          sub_ele['buttons'] = buttons
          elements.append(sub_ele.copy())

    #elements.append(subele.copy())
    payload['elements'] = elements
    payload['template_type'] = "generic"
    payload['image_aspect_ratio'] = "Square"
    attachment['type'] = "template"
    attachment['payload'] = payload
    return attachment
    


def searchForStates(name, sDict, states_list):
    for k, v in sDict.items():
        if k.lower() == name.lower():
            states_list.append(v)
            return True
def searchForCities(name, cDict, cities_list):
    for k, v in cDict.items():
        if k.lower() == name.lower():
            cities_list.append(v)
            return True
def searchForAmenities(name, aDict, amn_list):
    for k, v in aDict.items():
        if k.lower() == name.lower():
            amn_list.append(v)
            return True

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  messaging_events = payload["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:

      url_states = 'http://api.megha.space/api/v1/states_ids/'
      r_states = requests.get(url = url_states)
      data_states = r_states.json()
      url_cities = 'http://api.megha.space/api/v1/cities_ids/'
      r_cities = requests.get(url = url_cities)
      data_cities = r_cities.json()
      url_amn = 'http://api.megha.space/api/v1/amenities_ids/'
      r_amn = requests.get(url = url_amn)
      data_amn = r_amn.json()

      finalDict = {}
      cities_list = []
      states_list = []
      amn_list = []
      print(payload)

      txtOutput = False
      if event["message"]["nlp"]["entities"].get("greetings"):
        txtOutput = True
        yield event["sender"]["id"], json.dumps("Hi..! How can I help you").encode('unicode_escape'), txtOutput

      if event["message"]["nlp"]["entities"].get("location"):
        for i in event["message"]["nlp"]["entities"]["location"]:
          if not searchForStates(i['value'], data_states, states_list):
            searchForCities(i['value'], data_cities, cities_list)
      finalDict["states"] = states_list
      finalDict["cities"] = cities_list
      if event["message"]["nlp"]["entities"].get("amenities"):
        for i in event["message"]["nlp"]["entities"]["amenities"]:
          searchForAmenities(i['value'], data_amn, amn_list)
        finalDict["amenities"] = amn_list

      url2 = 'http://api.megha.space/api/v1/places_search/'
      r2 = requests.post(url = url2, data = json.dumps(finalDict), headers={'content-type': 'application/json'})
      data2 = r2.json()
      if not data2:
        tempD = {}
        tempD['name'] = "SORRY!!!"
        tempD['price_by_night'] = "There is no listing matching your requirement :("
        data2.append(tempD)
      yield event["sender"]["id"], json.dumps(constructMsg(data2)).encode('unicode_escape'), txtOutput
    else:
      txtOutput = True
      yield event["sender"]["id"], json.dumps("I can't echo this").encode('unicode_escape'), txtOutput

def send_message(token, recipient, text, txtOutput):
  """Send the message text to recipient with id recipient.
  """

  print(">>>>>>>>>>>>>>>>>>>>>>>>>>FINAL<<<<<<<<<<<<<<<<<<<<<<<")

  if txtOutput:
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"text": text.decode('unicode_escape')}
      }),
      headers={'Content-type': 'application/json'})
  else:
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
      params={"access_token": token},
      data=json.dumps({
        "recipient": {"id": recipient},
        "message": {"attachment": text.decode('unicode_escape')}
      }),
      headers={'Content-type': 'application/json'})

  print(r)

  finalDict = {}
  cities_list = []
  amn_list = []
  states_list = []
  if r.status_code != requests.codes.ok:
    print(r.text)

if __name__ == '__main__':
  app.run()
