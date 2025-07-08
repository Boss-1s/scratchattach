"""Module importing scratchattach to use for the project"""
import os
import scratchattach as scratch3
from scratchattach import Encoding

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
#cloud = session.connect_cloud("895107188") #<- this is the real project
cloud = session.connect_cloud("1051418168") #<- v2.0 dev project id, not the real one!

#requests
client = cloud.requests(used_cloud_vars=["1", "2"])

@client.request(response_priority=1)
def ping():
    return 'pong'
    print("Request Handler Pinged")

@client.request
def user_check(argument1):
    "Checks if recipient of message exists"
    print(f"User existence requested for {argument1}")
    try:
        user = scratch3.get_user(argument1)
        return user
        print("Sucessful return\nHTTP 200: SUCCESS")
    except Exception as e:
        print(f"{argument1} does not exist, returning error in project...(See below for details):")
        print(f"ERR HTTP 404: NOT_FOUND\nRequested for:{argument1}\nStatus: FAILED\nReason: {e}")
        return "404 Error: user does not exist - Check Python console for more details"

@client.request
def new_scratcher_detect(argument1):
    "Validates if user is a new scratcher, proving if they can use the program."
    print(f"Checking if {argument1} is a new scratcher")
    try:
        user = session.connect_user(argument1)
        answer = Encoding.encode(user.is_new_scratcher())
        return answer
    except Exception as e:
        print(f'{argument1} may not use this project, per "new_scratcher" status rules...(See below for details):')
        print(f"ERR HTTP 403: FORBIDDEN\nRequested for:{argument1}\nStatus: REJECTED\nReason: {e}")
        return "403 Error: user is a new scratcher - Check Python console for more details"

@client.event
def on_ready():
    "Runs when client is ready."
    print("Request handler is running")

@client.event
def on_request(request):
    "Runs when request is recieved."
    print("Received request", request.name, request.requester, request.arguments, request.timestamp, request.request_id)

client.start(thread=True) #make sure this is ALWAYS at the bottom of your Python file
