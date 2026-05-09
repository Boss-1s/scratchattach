import scratchattach as scratch3

session = scratch3.login("Boss_1sALT", "") 
conn = session.connect_cloud("992921739") #replace with your project id

client = scratch3.CloudRequests(conn)

@client.request
def ping(): #called when client receives request
    print("Ping request received")
    return "pong" #sends back 'pong' to the Scratch project

@client.request
def message_count(argument1):
    print(f"Message count requested for user {argument1}")
    user = scratch3.get_user(argument1)
    return user.message_count()

@client.request
def user_stats(argument1):
    print(f"User Stats requested for user {argument1}")

    user = scratch3.get_user(argument1)
    stats = user.stats()

    return_data = []
    return_data.append(f"Total loves: {stats['loves']}")
    return_data.append(f"Total favorites: {stats['favorites']}")
    return_data.append(f"Total views: {stats['views']}")

    return return_data

@client.event
def on_ready():
    print("Request handler is running")

client.run() #make sure this is ALWAYS at the bottom of your Python file
