"""Module importing scratchattach to use for the projrct"""
import os
import sys
import time
import warnings
import scratchattach as scratch3
from warnings import deprecated
from scratchattach import Encoding

warnings.filterwarnings('ignore', category=scratch3.LoginDataWarning)

passwrd = os.environ.get('PASS')

session = scratch3.login("Boss_1sALT", passwrd)
cloud = session.connect_cloud("1054907254") #replace with your project id
client = cloud.requests()

@client.request
def message_ping(argument1):
    "Main client request"
    os.system(f"echo Message Count requested for {argument1}")
    user = scratch3.get_user(argument1)
    return user.message_count()

@deprecated("method deprecated because you cannot truly check if a new scratcher is a new scratcher, as they cannot use cloud vars.")
@client.request
def new_scratcher_detect(argument1):
    "Secondary client request"
    os.system(f"echo Checking if {argument1} is a new scratcher")
    user = session.connect_user(argument1)
    answer = Encoding.encode(user.is_new_scratcher())
    return answer

@client.event
def on_ready():
    "Runs when client is ready."
    os.system("echo Request handler is running")

@client.event
def on_error(request, e):
    "Runs when client runs into error"
    os.system(f"echo Request: {request.request.name} {request.requester} {request.arguments} {request.timestamp} {request.request_id}")
    os.system("echo Error that occured: {e}")

@client.event
def on_request(request):
    "Runs when client receives request"
    os.system(f"echo Received Request: {request.request.name} {request.requester} {request.arguments} {request.timestamp} {request.request_id}")

@client.event
def on_unknown_request(request):
    "Runs when client receives unknown request"
    os.system(f"echo Received unknown request: {request.request.name} {request.requester} {request.arguments} {request.timestamp} {request.request_id}\n"+
             "echo Check the project and/or script to ensure there are no spelling errors, mistakes, etc. If the request seems suspicious, stop all backend jobs "+
             "immediately.")
    
client.start(thread=True) #make sure this is ALWAYS at the bottom of your Python file
