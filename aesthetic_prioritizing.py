import os
import sys
import time
import scratchattach as sa

pswd = os.environ.get("PASS") #'PASS' is an env secret in the workflow, not on this device

usnm = "Boss_1s"

# Log in to your Scratch account
session = sa.login(usnm, pswd)

# Get the user object for your account
user = session.connect_user(usnm)

max_atmp = 5
atmp = 0

# List of project IDs you want to bring to the top
project_ids_to_prioritize = [1193158560, 1193158559, 1193158558, 1193158567, 1193158568]  # Replace with actual project IDs

def prioritize(attempt: int, maxAttempts: int):
    try:
        print(f"Prioritizing: Attempt {attempt + 1}")
        if attempt >= maxAttempts:
            raise ValueError("Process failed, and the maximum attempt value has been reached. Exiting.")
        for project_id in project_ids_to_prioritize:
            project = session.connect_project(project_id)
           
            # Check if the project is already favorited by you
            if project in user.favorites():
                # Unfavorite the project
                project.unfavorite()
                print(f"Unfavorited project {project_id}")
   
            time.sleep(5)
           
            # Favorite the project again to move it to the top
            project.favorite()
            print(f"Favorited project {project_id} to move it to the top")
           
    except ValueError as e:
        print(e)
        sys.exit(1)
       
    except Exception as e:
        print(f"Process failed, retying. Error: {e}")
        global atmp
        atmp=atmp+1
        prioritize(atmp, max_atmp)

#-----#

try:
    prioritize(atmp, max_atmp)
finally:
    print("Prioritized projects in your favorite list.")
  
