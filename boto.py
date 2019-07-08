"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request
import json
from collections import OrderedDict
from boto_response_functions import *


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

