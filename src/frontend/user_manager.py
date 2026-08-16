import json
import os
import uuid

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) 
USER_FILE = os.path.join(BASE_DIR, "data", "user.json")

def load_users():
    """Loads the user dictionary from the JSON file."""
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE,"r") as f:
        return json.load(f)

def save_users(users_data):
    """Saves the user dictionary to the JSON file."""
    os.makedirs("data",exist_ok=True)
    with open(USER_FILE,"w") as f:
        json.dump(users_data,f,indent=4)


def add_new_user(username):
    """Creates a new user profile"""
    users = load_users()
    if username not in users:
        users[username] = {"sessions":{}}
        save_users(users)
        return True
    return False

def create_new_session(username, session_name):
    """Creates a new session and generates a unique langgraph thread_id"""
    users = load_users()
    thread_id = f"{username.replace(' ', '_').lower()}_{str(uuid.uuid4())[:6]}"

    users[username]['sessions'][session_name] = thread_id
    save_users(users)
    return thread_id