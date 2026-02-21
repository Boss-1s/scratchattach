import scratchattach as scratch3

session = scratch3.login("Boss_1sALT", "")

user = session.get_linked_user()

ujd = user.join_date

print("Your session id is " + session.session_id)
print("Boss_1sALT's join date is " + ujd)
