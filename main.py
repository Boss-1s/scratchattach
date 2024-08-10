import os
os.system ("pip install -U scratchattach")

import scratchattach as scratch3

session = scratch3.login("Boss_1s", "han2nppQJi^w.p:")
conn = session.connect_cloud("992921739")

events = scratch3.CloudEvents("992921739")

@events.event
def on_set(event):
    conn.set_var("FROM_HOST_1")