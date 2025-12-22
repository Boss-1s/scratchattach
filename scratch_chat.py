"""Module importing scratchattach to use for the project"""
from typing import Any, List
from warnings import deprecated
from key_multivalue_storage import Storage as s
import os
import warnings
import scratchattach as scratch3
from scratchattach import Encoding

warnings.filterwarnings('ignore', category=scratch3.LoginDataWarning)

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
#cloud = session.connect_cloud("895107188") #<- this is the real project
cloud = session.connect_cloud("1202780939") #<- this is the test project

def dprint(str) -> None:
    print(str)
    os.system("echo " + str)
    
# When adding new client methods, remember to put dprint() before return, so that the console gets a copy of the output.
client = cloud.requests(used_cloud_vars=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

@client.request(response_priority=1)
def r_ping() -> str:
    """Ping"""
    dprint("Request Handler Pinged")
    return 'pong'

@client.request(response_priority=2)
def r_user_check(argument1) -> str:
    """Checks if recipient of message exists"""
    dprint(f"User existence requested for {argument1}")
    try:
        user = scratch3.get_user(argument1)
        dprint("Sucessful return\nHTTP 200: SUCCESS")
        return user
    except Exception as e:
        dprint(f"{argument1} does not exist, returning error in project...(See below for details):")
        dprint(f"ERR HTTP 404: NOT_FOUND\nRequested for:{argument1}\nStatus: FAILED\nReason: {e}")
        return "404 Error: user does not exist - Check Python console for more details"

@client.request(response_priority=5)
@deprecated("This method does not truly work, as new scratchers cannot actually use cloud variables.")
def r_new_scratcher_detect(argument1) -> str:
    """DEPRECATED
    Validates if user is a new scratcher, proving if they can use the program."""
    dprint(f"Checking if {argument1} is a new scratcher")
    try:
        user = session.connect_user(argument1)
        answer = Encoding.encode(user.is_new_scratcher())
        return answer
    except Exception as e:
        dprint(f'{argument1} may not use this project, per "new_scratcher" status rules...(See below for details):')
        dprint(f"ERR HTTP 403: FORBIDDEN\nRequested for:{argument1}\nStatus: REJECTED\nReason: {e}")
        return "403 Error: user is a new scratcher - Check Python console for more details"

@client.request(response_priority=2)
def db_add_subval(db, key, subkey, val, subkey2=None, val2=None, subkey3=None, val3=None) -> str:
    #max 3 subkey-value pairs at the same time
    skwargs = {}
    skwargs.update({subkey: val})
    if subkey2 is not None and val2 is not None:
        skwargs.update({subkey2: val2})
    if subkey3 is not None and val3 is not None:
        skwargs.update({subkey3: val3})
    
    try:
        s(key, **skwargs).store(db)
    except Exception as e:
        dprint(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    dprint(f"Sucessfully added values {list(skwargs.values())} to subkeys {list(skwargs.keys())}, respectively.")
    return "Success"

@client.request(response_priority=2)
def db_set_val(db, key, subkey, val) -> str:
    try:
        s.Edit.propval(db, key, subkey, val)
    except Exception as e:
        dprint(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    dprint(f"Sucessfully set subkey {subkey} to value {val}.")
    return "Success"

@client.request(response_priority=3)
def db_get_keys(db) -> List[Any]:
    dprint(f"client.requester requested keys from database '{db}'")
    return s.Load.keys(db)

@client.request(response_priority=3)
def db_get_subkeys_values(db, top_lv_key, keys, raw) -> List[Any]:
    dprint(f"client.requester requested subkeys under the top level key '{top_lv_key}' in database '{db}'")
    return s.Load.values(db, top_lv_key, keys=keys, raw=raw)
    
@client.request(response_priority=2)    
def db_delete_key(db, key) -> str:
    try:
        s.Delete.by_key(db, key)
    except Exception as e:
        dprint(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    dprint(f"Sucessfully deleted key {key} and all its child data.")
    return "Success"

@client.request(response_priority=2)
def db_delete_all(db) -> str:
    try:
        s.Delete.all(db, warn=False)
    except Exception as e:
        dprint(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    dprint(f"Sucessfully deleted all data from {db}.")
    return "Success"
    
@client.event
def on_ready() -> None:
    """Runs when client is ready."""
    dprint("Request handler is running")

@client.event
def on_request(request) -> None:
    """Runs when request is recieved."""
    dprint(f"Received request {request.request_name}, requested by {request.requester}, args {request.arguments}, timestamp {request.timestamp}, id {request.request_id}\n")

@client.event
def on_unknown_request(request) -> None:
    """Runs when unknown request is recieved."""
    dprint(f"Received unknown request {request.request_name}, requester {request.requester}, args {request.arguments}, timestamp {request.timestamp}, id {request.request_id}. Check the project to make sure there are no typing and/or spelling errors.")
    
client.start(thread=True)
