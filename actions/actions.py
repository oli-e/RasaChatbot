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
from math import floor
import calendar
import re


class ActionAddress(Action):

    def name(self) -> Text:
        return "action_address"

    def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        msg = tracker.get_slot('address')
        x = re.search("[a-zA-Z]+\s([0-9]+/[0-9]+|[0-9]+)", msg)
        print(x.group())
        dispatcher.utter_message(
            text=f"Your order will be delivered to : {x.group()}\Thank you for your order!")

        return []


class ActionSummarizeOrder(Action):

    def name(self) -> Text:
        return "action_summarize_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        ingredient, order_str = "", ""
        total, time, costs, preparation_time = 0, 0, 0, 0

        for blob in tracker.latest_message['entities']:
            if blob['entity'] == 'ingredient':
                ingredient = blob['value']

        numbers = '1 2 3 4 5 6 7 8 9 0'.split(' ')
        order = dict()
        menu_items = self.__menu_list('name')
        msg = tracker.get_slot('order').lower().split(' ')
        ingred_idx = 0
        if ingredient in msg:
            ingred_idx = msg.index(ingredient)
        msg_single = [
            w[:-1] if w.endswith('s') or w.endswith('.') or w.endswith(',') else w for w in msg]

        default = 1
        for word in msg_single:
            item = dict()
            if word in menu_items:
                index = msg_single.index(word)
                if index != 0:
                    if msg_single[index - 1] in numbers:
                        default = int(msg_single[index - 1])
                name = msg[index]
                if ingred_idx - index > 0:
                    name = " ".join(
                        [msg[index], msg[ingred_idx-1], ingredient])
                order[word] = {'name': name,
                               'amount': default}

        for key in order:
            order_str += f"{order[key]['amount']} {order[key]['name']}, "
            for item in self.menu['items']:
                if item["name"].lower() == key:
                    time = item["preparation_time"]
                    costs = item["price"]
            preparation_time += time * order[key]['amount']
            total += costs * order[key]['amount']
        time_str = self.__stringifyTime(preparation_time)
        dispatcher.utter_message(
            text=f"Let me summarize :D\nYour order is: {order_str[:-2]}\nIt'll take aproximatelly {time_str}\nTotal sums up to {total}$\nDo you want takeaway or delivery?")

        return []

    def __stringifyTime(self, time: int) -> str:
        hours = floor(time)

        minutes = int((time - int(hours)) * 60)

        if hours == 0:
            return f"{minutes} minutes"
        elif hours != 0 and minutes == 0:
            if hours > 1:
                return f"{hours} hours"
            else:
                return f"{hours} hour"
        else:
            if hours > 1:
                return f"{hours} hours and {minutes} minutes"
            else:
                return f"{hours} hour and {minutes} minutes"

    def __menu_list(self, name: str):
        with open('menu.json') as file:
            menu = json.load(file)
        self.menu = menu
        return [item[name].lower() for item in menu['items']]


class ActionConfirmOpen(Action):

    def name(self) -> Text:
        return "action_confirm_open"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        day, hour = "", ""
        with open('opening_hours.json') as file:
            opening_time = json.load(file)
        opening_json = opening_time.get('items')

        for blob in tracker.latest_message['entities']:
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
