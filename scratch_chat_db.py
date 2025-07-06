"""Module importing scratchattach to use for the project"""
import os
import scratchattach as scratch3
from scratchattach import Database as db

passwrd = os.environ.get('PASS') #'PASS' is env secret in the repo, not on this device

session = scratch3.login("Boss_1sALT", passwrd)
#cloud = session.connect_cloud("895107188") #<- this is the real project
cloud = session.connect_cloud("1051418168") #<- v2.0 dev project id, not the real one!

#db
storage = cloud.storage()

os.system("cd scratch_chat")
os.system("ls")

db1 = db("chat", json_file_path="chat_db.json", save_interval=5)
#db2 = db("history", json_file_path="https://github.com/bossofcode/scratchattach/scratch_chat/chat_history_db.json", save_interval=5)

storage.add_database(db1)
# storage.add_database(db2)

@db.event
def on_save():
    print("The data was saved")

@db.event
def on_set(key, value):
    print("Key", key, "was set to value", value)

storage.start()
