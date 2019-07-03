"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request
import json
from collections import OrderedDict

@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg').lower()
    responses = OrderedDict([
        (input_info, response_info),
        (input_check_swear, response_swear),
        (input_check_name, response_name),
        (input_check_age, response_age),
    ])
    for k, v in responses.items():
        if k(user_message):
            response = v()
            return json.dumps({"animation": response["animation"], "msg": response["response"]})
    return json.dumps({"animation": "confused", "msg": "Sorry, I don't know what you mean. Please write full"
                                                       " sentences. You can write \"info\" to get some phrases."})


# Registered user information
user_information = {
    "name": "",
    "age": "",
    "isAdult": False
}


# Response functions start from here
# Info about registered commands
def input_info(message):
    if "info" in message:
        return True


def response_info():
    return{
        "animation": "takeoff",
        "response": 'Some of the commands that I can understand are as follows:'
                    'You can fill the dotted part accordingly "My name is .....", "I am .... years old",'
                    ' "How is the weather in .... ", "Please tell me a joke"'
    }


# Checking if the input contains a swear word
def input_check_swear(message):
    swear_words = ["fuck", "shit", "bitch", "bastard", "cunt", "dick"]
    for swear in swear_words:
        if swear in message:
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


def weather():
    import requests
    url = 'api.openweathermap.org/data/2.5/weather?q=London'
    response = requests.get(url)
    #return response["weather"]["description"]
    return "ikinciye geldi"

def findweather():
    return True






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

