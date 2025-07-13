"""Module importing scratchattach to use for the project"""
import os
import warnings
import scratchattach as scratch3
from scratchattach import Encoding

warnings.filterwarnings('ignore', category=scratch3.LoginDataWarning)

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
cloud = session.connect_cloud("895107188") #<- this is the real project

#requests
client = cloud.requests(used_cloud_vars=["1", "2"],respond_order="priority")

@client.request(response_priority=1)
def ping1():
    return 'pong'
    print("Request Handler Pinged")

@client.request(response_priority=2)
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

@client.request(response_priority=5)
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

@client.request(response_priority=100)
def set(argument1, argument2):
    print("A request named 'set' was recieved, and was realyed to the Database Handler."+
          f"\nRequest Name: 'set'\n - arg1: {argument1}\n - arg2: {argument2}\nStatus: RELAYED"+
          "\nReason: this request belongs to the database handler")

@client.request(response_priority=100)
def get(agrument1, argument2):
    print("A request named 'get' was recieved, and was realyed to the Database Handler."+
          f"\nRequest Name: 'set'\n - arg1: {argument1}\n - arg2: {argument2}\nStatus: RELAYED"+
          "\nReason: this request belongs to the database handler")
    
@client.request(response_priority=100)
def keys(argument1):
    print("A request named 'keys' was recieved, and was realyed to the Database Handler."+
          f"\nRequest Name: 'set'\n - arg1: {argument1}\n - arg2: NULL\nStatus: RELAYED"+
          "\nReason: this request belongs to the database handler")
    
def delete(argument1, argument2):
    print("A request named 'delete' was recieved, and was realyed to the Database Handler."+
          f"\nRequest Name: 'set'\n - arg1: {argument1}\n - arg2: {argument2}\nStatus: RELAYED"+
          "\nReason: this request belongs to the database handler")
    
@client.request(name="delete",response_priority=100)
def delete_request(db_name, key):
    print("A request named 'delete' was recieved, and was realyed to the Database Handler."+
          f"\nRequest Name: 'set'\n - arg1: {db_name}\n - arg2: {key}\nStatus: RELAYED"+
          "\nReason: this request belongs to the database handler")
    
@client.event
def on_ready():
    "Runs when client is ready."
    print("Request handler is running")

@client.event
def on_request(request):
    "Runs when request is recieved."
    print("Received request", request.request.name, request.requester, request.arguments, request.timestamp, request.request_id)
    
client.start(thread=True) #make sure this is ALWAYS at the bottom of your Python file
