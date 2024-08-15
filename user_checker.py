"""Module importing scratchattach to use for the projrct"""
import scratchattach as scratch3

session = scratch3.login("Boss_1sALT", "han2nppQJi^w.p:")
conn = session.connect_cloud("895107188") #replace with your project id

client = scratch3.CloudRequests(conn)

@client.request(thread=True)
def message_ping(argument1):
    "Main client request"
    print(f"User existance requested for {argument1}")
    user = scratch3.get_user(argument1)
    return user

@client.event
def on_ready():
    "Runs when client is ready."
    print("Request handler is running")

@client.event
def on_request(request):
    "Runs when request is recieved."
    print("Received request", request.name, "Requester:", request.requester, "Request arguments:",
          request.arguments, "Timestamp:", request.timestamp, "Request ID:", request.id)

client.run() #make sure this is ALWAYS at the bottom of your Python file
