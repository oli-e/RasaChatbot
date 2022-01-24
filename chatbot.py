from http import client
from urllib import response
from flask import Flask, request
from slackeventsapi import SlackEventAdapter
import slack
import requests
from tokens import VERIFICATION_TOKEN, TOKEN

app = Flask(__name__)
# @app.route("/slack/events",methods=['GET','POST'])
# def authorize():
#   output = request.get_json()
#   return output["challenge"]

slack_events_adapter = SlackEventAdapter(VERIFICATION_TOKEN, 
                                         "/slack/events", app)

client = slack.WebClient(token=TOKEN)
bot = client.api_call("auth.test")['user_id']

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    response = requests.post(
          'http://localhost:5005/webhooks/rest/webhook',
          json={"sender": user_id, "message": text})
    response_text = response.json()
    message_back = ""
    for r_text in response_text:
      message_back += r_text['text'] + '\n'
        
    if user_id != bot:
      client.chat_postMessage(channel="D0307SZ3S7J", text=message_back)   




if __name__ == "__main__":
  app.run(port=3000, debug=False)