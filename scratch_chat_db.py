"""Module importing scratchattach to use for the project"""
import os
import json
import scratchattach as scratch3
from scratchattach import Database as db

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
cloud = session.connect_cloud("895107188") #<- this is the real project

#db
storage = cloud.storage(used_cloud_vars=["3","4"])

db1 = db("chat", json_file_path="chat_db.json", save_interval=60)
db2 = db("history", json_file_path="chat_history_db.json", save_interval=60)

storage.add_database(db1)
storage.add_database(db2)

@storage.request(response_priority=1)
def ping2():
    return "pong"
    print("Database handler pinged")

@storage.request(name="delete")
def delete_request(db_name, key):
    del storage.get_database(db_name).data[key]

@storage.request(name="delete_all")
def delete_all(db_name):
    # write an empty dictionary to the file
    if db_name == "chat":
        with open("chat_db.json", "w") as f:
            json.dump({}, f)
    elif db_name == "history":
        with open("chat_history_db.json", "w") as f:
            json.dump({}, f)
    print(f"All data deleted from database {db_name}.")
    return ""

@db1.event
def on_save():
    print("Data was saved to db chat")

@db1.event
def on_set(key, value):
    print("Key", key, "was set to value", value, "in db chat")

@db2.event
def on_save():
    print("Data was saved to db history")

@db2.event
def on_set(key, value):
    print("Key", key, "was set to value", value, "in db history")

storage.start()
