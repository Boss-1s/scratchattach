from typing import Any
from warnings import deprecated
from key_multivalue_storage import Storage
import os,warnings,scratchattach as sa,websocket,builtins,uuid
from scratchattach import Encoding

warnings.filterwarnings('ignore', category=sa.LoginDataWarning)

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = sa.login("Boss_1sALT", passwrd)
#cloud = session.connect_cloud("895107188") #<- this is the real project
cloud = session.connect_cloud("1202780939") #<- this is the test project

temp_objs = [None]*10

def print(*args, **kwargs) -> None:builtins.print("[scratch_chat.py] ", *args, **kwargs)
    
# When adding new client methods, remember to put print() before return, so that the console gets a copy of the output.
client = cloud.requests()

@client.request(response_priority=1)
def r_ping() -> str:
    """Ping"""
    print("Request Handler Pinged")
    return 'pong'

@client.request(response_priority=2)
def r_user_check(argument1) -> str:
    """Checks if recipient of message exists"""
    print(f"User existence requested for {argument1}")
    try:
        user = sa.get_user(argument1)
        print("Sucessful return---HTTP 200: SUCCESS")
        return user
    except Exception as e:
        print(f"{argument1} does not exist, returning error in project...(See below for details):")
        print(f"ERR HTTP 404: NOT_FOUND---Requested for:{argument1}---Status: FAILED---Reason: {e}")
        return "404 Error: user does not exist - Check Python console for more details"

@client.request(response_priority=2)
def db_create_obj(key: str | uuid.UUID, **kwargs: dict[str, Any]) -> str:
    c = 0
    for i in temp_objs:
        if not i:break
        c+=1
    if c >= len(temp_obj):
        print("Could not create new Storage object - temporary storage"+
              " space has run out. Try deleting some objects withing the space.")
        return "Error - Check Python console for more details"
    temp_objs[c]=Storage(key, **kwargs)
    if temp_objs:
        print("Sucessfully created object")
        return "Success"
    else: print("Unknown Error occured");return "Error - Check Python console for more details"

@client.request(response_priority=2)
def db_add_subval(obj_num: int, dict_obj: dict[str, Any]) -> str:
    try:temp_objs[obj_num] = temp_objs[obj_num] + dict(dict_obj)
    except Exception as e:
        print(f"Process failed: {e}")
        return f"Error: {e} - Check Python console for more details"
    print(f"Sucessfully added {dict(dict_obj)} to {temp_objs[obj_num]}")
    print(f"Spaces used: {len(temp_objs) - sum(x is None for x in temp_objs)}/10")
    return "Success"

@client.request(response_priority=2)
def db_store_obj(file: str, obj_num: int, clean_up: bool = True) -> str:
    try:temp_objs[obj_num].store(file)
    except Exception as e:
        print(f"Process failed: {e}")
        return f"Error: {e} - Check Python console for more details"
    print(f"Sucessfully stored {temp_objs[obj_num]} to {file}")
    if clean_up:
        try:temp_obj[obj_num] = None
        except Exception as e:
            print(f"Process failed: {e}")
            return f"Error: {e} - Check Python console for more details"
        print(f"Sucessfully deleted {temp_objs[obj_num]} from temporary storage.")
        print(f"Spaces used: {len(temp_objs) - sum(x is None for x in temp_objs)}/10")
    return "Success"

@client.request(response_priority=2)
def db_delete_obj(obj_num: int) -> str:
    try:temp_obj[obj_num] = None
    except Exception as e:
        print(f"Process failed: {e}")
        return f"Error: {e} - Check Python console for more details"
    print(f"Sucessfully deleted {temp_objs[obj_num]} from temporary storage.")
    print(f"Spaces used: {len(temp_objs) - sum(x is None for x in temp_objs)}/10")
    return "Success"

@client.request(response_priority=2)
def db_set_val(db, key, subkey, val) -> str:
    try:
        Storage.Edit.propval(db, key, subkey, val)
    except Exception as e:
        print(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    print(f"Sucessfully set subkey {subkey} to value {val}.")
    return "Success"

@client.request(response_priority=3)
def db_get_keys(db) -> list[Any]:
    print(f"client.requester requested keys from database '{db}'")
    return Storage.Load.keys(db)

@client.request(response_priority=3)
def db_get_subkeys_values(db, top_lv_key, keys, raw) -> list[Any]:
    print(f"client.requester requested subkeys under the top level key '{top_lv_key}' in database '{db}'")
    return Storage.Load.values(db, top_lv_key, keys=keys, raw=raw)
    
@client.request(response_priority=2)    
def db_delete_key(db, key) -> str:
    try:
        Storage.Delete.by_key(db, key)
    except Exception as e:
        print(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    print(f"Sucessfully deleted key {key} and all its child data.")
    return "Success"

@client.request(response_priority=2)
def db_delete_all(db) -> str:
    try:
        Storage.Delete.all(db, warn=False)
    except Exception as e:
        print(f"Process failed: {e}")
        return f"unknown error occured: {e}"
    print(f"Sucessfully deleted all data from {db}.")
    return "Success"
    
@client.event
def on_ready() -> None:
    """Runs when client is ready."""
    print("Request handler is running")

@client.event
def on_request(request) -> None:
    """Runs when request is recieved."""
    print(f"Received request {request.request_name}, requested by {request.requester}, args {request.arguments}, timestamp {request.timestamp}, id {request.request_id}")

@client.event
def on_unknown_request(request) -> None:
    """Runs when unknown request is recieved."""
    print(f"Received unknown request {request.request_name}, requester {request.requester}, args {request.arguments}, timestamp {request.timestamp}, id {request.request_id}. Check the project to make sure there are no typing and/or spelling errors.")

client.start(thread=True)
