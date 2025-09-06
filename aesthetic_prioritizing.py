import os
import time
import warnings
import time
import scratchattach as sa

warnings.filterwarnings('ignore', category=sa.LoginDataWarning)

pswd = os.environ.get("PASS") #'PASS' is an env secret in the workflow, not on this device
usnm = "Boss_1s"
session = sa.login(usnm, pswd)# Log in to your Scratch account
user = session.connect_user(usnm)# Get the user object for your account

class ProjectNotFound(Exception):
    """Custom exception raised when a project is not found."""
    def __init__(self, item_id, message="Project ID of the following was not found"):
        self.item_id = item_id
        self.message = f"{message}: {item_id}"
        super().__init__(self.message)
        
class StudioNotFound(Exception):
    """Custom exception raised when a studio is not found."""
    def __init__(self, item_id, message="Studio ID of the following was not found"):
        self.item_id = item_id
        self.message = f"{message}: {item_id}"
        super().__init__(self.message)


fav_project_ids = []
fav_studios_ids = []

def favorites():
    global fav_project_ids

    # Get the list of favorited projects
    favorited_projects = user.favorites()
   
    # Create an empty list to store the project IDs
    fav_project_ids = []
   
    # Iterate through the favorited projects and extract their IDs
    for project in favorited_projects:
        fav_project_ids.append(project.id)

max_atmp = 5
atmp = 0
# List of project IDs you want to bring to the top
project_ids_to_prioritize = [1193158560, 1193158559, 1193158558, 1193158567, 1193158568]  # Replace with actual project IDs
studio_ids_to_prioritize = [50609120, 50609126, 50609128, 50609129]  # Replace with actual studio IDs

def prioritize(attempt: int, maxAttempts: int):
    global atmp
    favorites()
    try:
        print(f"Prioritizing: Attempt {attempt + 1}")
        if attempt >= maxAttempts:
            raise ValueError("Process failed, and the maximum attempt value has been reached. Exiting.")
            
        if project_ids_to_prioritize[::-1] == fav_project_ids[:len(project_ids_to_prioritize)]:
            print("Projects already on top. No prioritizing needed.")
            return
            
        for project_id in project_ids_to_prioritize:
            project = session.connect_project(project_id)
            if project is None:
                raise ProjectNotFound(project_id)
           
            # Check if the project is already favorited by you
            if project.id in fav_project_ids:
                # Unfavorite the project
                project.unfavorite()
                print(f"Unfavorited project {project_id}")
               
                time.sleep(45)
               
                print(f"Favorited project {project_id} to move it to the top")
            else:
                print(f"Favorited project {project_id} because it was never favorited")
           
            # Favorite the project again to move it to the top
            project.favorite()

            time.sleep(45)
            
    except ValueError as e:
        print(e)
        sys.exit(1)

    except ProjectNotFound as e:
        print(f"{e}. Retrying script")
        atmp=atmp+1
        prioritize(atmp, max_atmp)
       
    except Exception as e:
        print(f"Process failed, retying. Error: {e}")
        atmp=atmp+1
        prioritize(atmp, max_atmp)

def prioritize_studio(attempt: int, maxAttempts: int):
    global atmp
    try:
        print(f"Prioritizing: Attempt {attempt + 1}")
        if attempt >= maxAttempts:
            raise ValueError("Process failed, and the maximum attempt value has been reached. Exiting.")

            
        for studio_id in studio_ids_to_prioritize:
            studio = session.connect_studio(studio_id)
            if studio is None:
                raise StudioNotFound(studio_id)
           
            # Unfavorite the project
            studio.unfollow()
            print(f"Unfollowed stuido {studio_id}")
           
            time.sleep(35)
           
            print(f"Followed studio {studio_id} to move it to the top")
       
            # Favorite the studio again to move it to the top
            studio.follow()

            time.sleep(45)
            
    except ValueError as e:
        print(e)
        sys.exit(1)

    except StudioNotFound as e:
        print(f"{e}. Retrying script")
        atmp=atmp+1
        prioritize_studio(atmp, max_atmp)
       
    except Exception as e:
        print(f"Process failed, retying. Error: {e}")
        atmp=atmp+1
        prioritize_studio(atmp, max_atmp)

#-----#

max_atmp = 5
atmp = 0

try:
    prioritize(atmp, max_atmp)
finally:
    print("Prioritized projects in your favorite list.")

max_atmp = 5
atmp = 0

try:
    prioritize_studio(atmp, max_atmp)
finally:
    print("Prioritized studios in your favorite list.")
