# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from email.policy import default
from typing import Any, Text, Dict, List
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import date
import calendar


class ActionSummarizeOrder(Action):

    def name(self) -> Text:
        return "action_summarize_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order = dict()
        menu_items = self.__menu_list()
        msg = tracker.get_slot('order').lower().split(' ')
        print(msg)
        print(menu_items)
        default = 1
        for word in msg:
            if word in menu_items:
                order[word] = default

        print(order)

        dispatcher.utter_message(text="Hello World!")

        return []

    def __menu_list(self):
        with open('menu.json') as file:
            menu = json.load(file)
        return [item['name'].lower() for item in menu['items']]


class ActionConfirmOpen(Action):

    def name(self) -> Text:
        return "action_confirm_open"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        day, hour = "", ""
        with open('opening_hours.json') as file:
            opening_time = json.load(file)
        opening_json = opening_time.get('items')

        for blob in tracker.latest_message['entities']:
            print(blob)
            if blob['entity'] == 'day':
                day = blob['value']

            if blob['entity'] == 'hour':
                hour = blob['value']

        # If "today" gets day of the week looks for such day i opening.json
        if day == "today":
            my_date = date.today()
            day_name = calendar.day_name[my_date.weekday()]
            days = opening_json.get(day_name)
        else:
            days = opening_json.get(day.capitalize())
        if days is None:
            dispatcher.utter_message(
                text=f"I couldn't understand {day}")
            return []

        if hour == '':
            dispatcher.utter_message(
                text=f"The restaurant is open from {days.get('open')} to {days.get('close')} on {day}"
            )
            return []
        if int(hour) not in range(1, 25):
            dispatcher.utter_message(
                text=f"Not funny. There is no such hour in a day!")
            return []
        opening_hour = days.get('open')
        close_hour = days.get('close')

        if int(hour) in range(opening_hour, close_hour+1):
            dispatcher.utter_message(
                text=f"Yes, on {day} we are open from {days.get('open')} to {days.get('close')} ")
        else:
            dispatcher.utter_message(
                text=f"No, sorry, on {day} at {hour} o'clock the restaurant is closed :(")

        return []


class ActionShowMenu(Action):

    def name(self) -> Text:
        return "action_show_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('menu.json') as file:
            menu = json.load(file)
        menu_json = menu.get('items')
        menu = "I'm glad you asked! :D \nWe have: \n"
        for item in menu_json:
            meal = item.get('name')
            menu = menu + f'  * {meal}\n'
        menu += "\nIs there something you would like to order? :)"
        dispatcher.utter_message(text=menu)

        return []
