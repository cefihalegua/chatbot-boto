"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request
import json
from collections import OrderedDict
from threading import Timer
import requests
from math import floor
import random


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg').lower()
    responses = OrderedDict([
        (is_offended, response_offended),
        (input_info, response_info),
        (check_answer_for_questions, response_for_questions),
        (input_check_swear, response_swear),
        (input_check_name, response_name),
        (input_check_age, response_age),
        (input_check_joke, response_joke),
        (input_check_weather, response_weather),
        (input_check_search_engine, response_search_engine)
    ])
    for k, v in responses.items():
        if k(user_message):
            response = v()
            return json.dumps({"animation": response["animation"], "msg": response["response"]})
    return json.dumps({"animation": "confused", "msg": "Sorry, I don't know what you mean."
                                                       " You can write \"info\" to get some phrases."})


# Registered user information
user_information = {
    "last_question_was_name": True,  # Boto asks name initially
    "last_question_was_age": False,
    "name": "",
    "age": "",
    "isAdult": False,
    "swear_count": 0,
    "said_sorry": False,
    "swear_again_in_is_offended": False,
}


# Response functions start from here
# If a user swears a lot Boto gets offended and does not answer the user
def is_offended(message):
    if "sorry" in message:
        user_information["said_sorry"] = True
    if user_information["swear_count"] > 5:
        if input_check_swear(message):
            user_information["swear_again_in_is_offended"] = True
        return True


def response_offended():
    if user_information["said_sorry"]:
        user_information["said_sorry"] = False
        reset_swear_counter()
        return {
            "animation": "heartbroke",
            "response": "Please don't break my heart again, I have feelings too!"
        }
    else:
        timer_reset_swear_counter = Timer(90.0, reset_swear_counter)
        timer_reset_swear_counter.start()
        if user_information["swear_again_in_is_offended"]:
            user_information["swear_again_in_is_offended"] = False
            return {
                "animation": "afraid",
                "response": "I don't talk with rude people, you are scaring me"
            }
        else:
            return {
                "animation": "no",
                "response": "I don't talk with rude people."
            }


def reset_swear_counter():
    user_information["swear_count"] = 0
    print("swear counter reset")


# Info about registered commands
def input_info(message):
    if "info" in message:
        return True


def response_info():
    return{
        "animation": "takeoff",
        "response": 'Some of the commands that I can understand are as follows: '
                    'You can fill the dotted part accordingly "My name is .....", "I am .... years old",'
                    ' "How is the weather in ....(city name only)", "Tell me a joke" '
                    'or you can always type a name, place etc to get some information about it.'
    }


# Checking if the user is answering a question Boto has asked
def check_answer_for_questions(message):
    if user_information["last_question_was_name"]:
        words = message.split()
        name = words[len(words)-1]
        user_information["name"] = name[0:1].upper() + name[1:]
        return True
    if user_information["last_question_was_age"]:
        user_information["age"] = [int(age) for age in message.split() if age.isdigit()]
        if user_information["age"] == []:
            user_information["last_question_was_age"] = False
            return False
        return True


def response_for_questions():
    if user_information["last_question_was_name"]:
        user_information["last_question_was_name"] = False
        return response_name()
    elif user_information["last_question_was_age"]:
        user_information["last_question_was_age"] = False
        return response_age()
    else:
        return {
            "animation": "waiting",
            "response": "There was an error, could you please write again"
        }


# Checking if the input contains a swear word
def input_check_swear(message):
    swear_words = ["fuck", "shit", "bitch", "bastard", "cunt", "dick", "asshole"]
    for swear in swear_words:
        if swear in message:
            user_information["swear_count"] = user_information["swear_count"] + 1
            return True
    return False


def response_swear():
    return{
        "animation": "no",
        "response": "Please do not use swear words..."
    }


# Getting the user name
def input_check_name(message):
    if "my name is" in message:
        user_information["name"] = message[11:12].upper() + message[12:]
        return True


def response_name():
    ask_age = ""
    if user_information['age'] == "":
        ask_age = " How old are you?"
        user_information["last_question_was_age"] = True
    return {
        "animation": "excited",
        "response": f"Nice to meet you {user_information['name']}.{ask_age}"
    }


# Getting user age
def input_check_age(message):
    if "years old" in message:
        user_information["age"] = [int(age) for age in message.split() if age.isdigit()]
        return True


def response_age():
    age = user_information['age'][0]
    if age >= 18:
        user_information["isAdult"] = True
        age_response = "Wow you are an adult! I'm just 1 years old."
    else:
        age_response = f"We are both not adults yet :) I'm 1 years old"
    return {
        "animation": "excited",
        "response": age_response
    }


# Telling a random joke upon request
def input_check_joke(message):
    if "joke" in message or "kidding" in message:
        return True
    else:
        return False


def response_joke():
    jokes = ["What’s the best thing about Switzerland? I don’t know, but the flag is a big plus.",
             "Why do we tell actors to “break a leg?” Because every play has a cast.",
             "Hear about the new restaurant called Karma? There’s no menu: You get what you deserve.",
             "Did you hear about the actor who fell through the floorboards? He was just going through a stage.",
             "Did you hear about the claustrophobic astronaut? He just needed a little space.",
             "Why don’t scientists trust atoms? Because they make up everything.",
             "How do you drown a hipster? Throw him in the mainstream.",
             "Why don’t Calculus majors throw house parties? Because you should never drink and derive.",
             "What did the left eye say to the right eye? Between you and me, something smells."]
    joke_number = random.randint(0, len(jokes)-1)
    return {
        "animation": "laughing",
        "response": jokes[joke_number]
    }


# Telling how is the weather in the desired city
def input_check_weather(message):
    if "weather" in message:
        user_information["weather_city"] = message[22:]
        if user_information["weather_city"] == "tel aviv":
            user_information["weather_city"] = "tel aviv, il"
        return True


def response_weather():
    city = user_information["weather_city"]
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID=fb0e6229d78973814f4cf193f2900387'
    weather_report = requests.get(url)
    description = weather_report.json()["weather"][0]["description"]
    temperature = weather_report.json()["main"]["temp"]
    temperature = floor(temperature)
    return {
        "animation": "dog",
        "response": f"It's {temperature} degrees with {description}"
    }


# Giving search engine results
def input_check_search_engine(message):
    url = f'https://api.duckduckgo.com/?q={message}&format=json&pretty=1'
    search_engine = requests.get(url)
    try:
        user_information["search_engine_result"] = search_engine.json()["RelatedTopics"][0]["Text"]
        return True
    except:
        return False


def response_search_engine():
    return {
        "animation": "giggling",
        "response": user_information["search_engine_result"]
    }


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    return json.dumps({"animation": "inlove", "msg": user_message})


@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def main():
    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()

