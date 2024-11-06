import json
from datetime import datetime
import copy
import re


def get_current_datetime():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    return formatted_date

def load_users():
    with open('usernames.json', 'r') as file:
        return json.load(file)

# Check if username and password are valid
def authenticate( username, password):
    user_db = load_users()
    return user_db['users'].get(username) == password

#returns ALL chat history for current user
def get_chats(username):
    c_name = username
    with open('database.json', 'r') as db:
        try:
            data = json.load(db)
            
            # Iterate through the chat participants
            for participant in data['chat']:
                # Check if the current participant's name matches c_name
                if participant['name'] == c_name:
                    return participant['contents']
            
            # If no matching name is found, return None
            return None
        except FileNotFoundError:
            print("Error: The file 'database.json' was not found.")
            return None
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

#This function will return chat history for A specific user
def get_chat_history(message):
    #check if msg history exists first for that person
    _, username, target_name = message.split(',')
    chats = get_chats(username)
    #print(f"username: {username}\ntarget: {target_name}")
    if not chats:
        print(f"No chats for {message}")
        return None
    if not target_name:
        print(f"No target name: {target_name}")
        return None

    # chats = [{'Zebra': {'messages': [{'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}]
    # chats[0] = Zebra...
    #ls = []
    for chat in chats:
        #print(f"chat var: {chat}")
        #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
        if target_name not in chat:
            #no history, could fix with making new chat history or something idk
            return None
        if chat[target_name] is not None and chat[target_name]:
            #print(f"inside chat == target_name contents: {chat}")
            #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
            history = chat[target_name]['messages']
            #print(f"GOT HISTORY: {history}")
            #[{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]
            return history
            #for dm in history:
            #    ls.append(f"{dm['owner']}, {dm['contents']}")
    return None
    #print(str(ls))
    #['Alice, Whats cookin?', 'Zebra, All good here, just working.']
    #return ls

#Gets history with data (client needs to format it tbh)
def display_chat_history(history):
    if not history:
        print("No chat history!")
        return
    for dm in history:
        print(f"User: {dm['owner']}\nMessage: {dm['contents']}")

#returns chats for current user only (no data attatched)
def get_chats_only(username):
    c_name = username
    work = None
    with open('database.json', 'r') as db:
        try:
            data = json.load(db)
            
            # Iterate through the chat participants
            for participant in data['chat']:
                # Check if the current participant's name matches c_name
                if participant['name'] == c_name:
                    work = participant['contents']
                    break
        except FileNotFoundError:
            print("Error: The file 'database.json' was not found.")
            return None
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    if work is None: #no chat history for current user
        return None
    
    list_of_names = [name for name in work[0]]
    return list_of_names

#TODO Fix the below...
#adds chat to right part in JSON file with use of helper function
def add_chat(username, target_name, message):
    #check if msg history exists first for that person
    _, message = message.split(",")

    chats = get_chats(username)
    chats2 =   get_chats(target_name)
    #print(f"username: {username}\ntarget: {target_name}")

    if not chats: #if user 1 dont have history append
        print(f"No chats for {message}, making new chat")
        chat[target_name] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
        add_chats_helper(username=username, new_chats=chat) #done for side 1
        if not chats2: #if other dude also does not have history
            print(f"No chats for {message}, creating new chat?")
            chat[username] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
            add_chats_helper(username=target_name, new_chats=chat) #Done for side 2 if no chats and only here if both were null
        else: #if other dude DOES have history AND first dude no history
            for chat in chats2:
                if username not in chat:
                    #if chat history doesnt exist (idk how you will get here for rn)
                    chat[username] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
                    return
                if chat[username] is not None and chat[username]:
                    history = chat[username]['messages']
                    history.append({'owner': username, 'contents': message, 'time': get_current_datetime()})
                    break
            add_chats_helper(username=target_name, new_chats=chats2) # if here other dude had chat already and was not deleted
    else: #IF first dude DOES have history
        for chat in chats:
            #print(f"chat var: {chat}")
            #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
            if target_name not in chat:
                chat[target_name] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
                return
            if chat[target_name] is not None and chat[target_name]:
                #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
                history = chat[target_name]['messages']
                #[{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]
                history.append({'owner': username, 'contents': message, 'time': get_current_datetime()})
                break
        add_chats_helper(username=username, new_chats=chats)
        if not chats2: #if other dude has no history AND first dude DID have history
            print(f"No chats for {message}, creating new chat?")
            chat[username] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
            add_chats_helper(username=target_name, new_chats=chat) #Done for side 2 if no chats and only here if both were null
        else: #if history exists for both 
            for chat in chats2:
                if username not in chat:
                    #if chat history doesnt exist (idk how you will get here for rn)
                    chat[username] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
                    return
                if chat[username] is not None and chat[username]:
                    history = chat[username]['messages']
                    history.append({'owner': username, 'contents': message, 'time': get_current_datetime()})
                    break
            add_chats_helper(username=target_name, new_chats=chats2)
            return 

    
def add_chats_helper(username, new_chats):
    c_name = username
    with open('database.json', 'r+') as db:
        try:
            data = json.load(db)
            
            for participant in data['chat']:
                # Check if the current participant's = matches c_name
                if participant['name'] == c_name:
                    participant['contents'] = new_chats
                    
                    db.seek(0)  #Reset pointer to the start of the file
                    json.dump(data, db, indent=4)  # actually writes
                    db.truncate()  # Truncate the file if leftvoers
                    print("Successfully replaced chats in the database.")
                    return
            
            # If no matching name is found, return None
            return None
        except FileNotFoundError:
            print("Error: The file 'database.json' was not found.")
            return "Internal error -1"
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return "Internal error -2"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Internal error -3"
def add_account(username, password, c_pass):
    if password != c_pass:
        return "Error confirming passwords."
    
    pattern = r'^[a-zA-Z1-9]+$'
    try:
        if not re.match(pattern, username):
            raise Exception("Error: Username must only contain letters a-z, A-Z, and digits 1-9.")
    except Exception as e:
        return str(e)
    
    with open('usernames.json', 'r+') as db:
        try:
            users = json.load(db)
            if username not in users['users']:
                users['users'][username] = password
                db.seek(0)
                json.dump(users, db, indent=4)  # actually writes
                db.truncate()  # Truncate the file if leftvoers
                print("Successfully added new user.")
            else:
                return "Username not available. Please try again"
            # If no matching name is found, return None
            return "Successful account creation."
        except FileNotFoundError:
            print("Error: The file 'database.json' was not found.")
            return "Internal error -1"
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return "Internal error -2"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "Internal error -3"

