"""Module importing scratchattach to use for the project"""
import os
import scratchattach as scratch3
from scratchattach import Database as db

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
#cloud = session.connect_cloud("895107188") #<- this is the real project
cloud = session.connect_cloud("1051418168") #<- v2.0 dev project id, not the real one!

#db
storage = cloud.storage(used_cloud_vars=["3","4"])

db1 = db("chat", json_file_path="chat_db.json", save_interval=5)
db2 = db("history", json_file_path="chat_history_db.json", save_interval=5)

storage.add_database(db1)
storage.add_database(db2)

@storage.request(response_priority=1)
def ping2():
    return "pong"
    print("Database handler pinged")

@storage.request(name="delete")
def delete_request(db_name, key):
    del storage.get_database(db_name).data[key]

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
