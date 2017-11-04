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
  for sender, message in messaging_events(payload):
    print("Incoming from %s: %s" % (sender, message))
    send_message(PAT, sender, message)
  return "ok"


finalDict = {}
cities_list = []
amn_list = []

def searchForLocation(name, sDict):
      for k, v in sDict.items():
          if k == name:
              print(v)
              cities_list.append(v)               

def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  #data = json.loads(payload)
  messaging_events = payload["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
#    if event["message"]["nlp"]["entities"]["location"]["value"] in ["San Francisco", "San Jose"]:

      url1 = 'http://api.megha.space/api/v1/states_ids/'
      r1 = requests.get(url = url1)
      data1 = r1.json()


      for i in event["message"]["nlp"]["entities"]["location"]:
        searchForLocation(i['value'], data1)      
        #if i['value'] == "San Francisco":
        #  cities_dict["05b0b99c-f10e-4e3a-88d1-b3187d6998ee"] = i['value']
        #if i['value'] == "San Jose":
        #  cities_dict["33c525b5-f087-421c-946d-ba8c7a1c2efe"] = i['value']
      finalDict["states"] = cities_list
#      yield event["sender"]["id"], (event["message"]["nlp"]["entities"]["location"][0]["value"]+" and " + event["message"]["nlp"]["entities"]["amenities"][0]["value"]).encode('unicode_escape')
      print(finalDict)
          

      url2 = 'http://api.megha.space/api/v1/places_search/'
      r2 = requests.post(url = url2, data = json.dumps(finalDict), headers={'content-type': 'application/json'})
      data2 = r2.json()
      print("PRINTING FINAL response")
      print(len(data2))




      yield event["sender"]["id"], json.dumps("Hi").encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print(r.text)

if __name__ == '__main__':
  app.run()
