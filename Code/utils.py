import json
from datetime import datetime
import copy


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
    with open('database.json', 'r') as db:
        try:
            data = json.load(db)
            
            # Iterate through the chat participants
            for participant in data['chat']:
                # Check if the current participant's name matches c_name
                if participant['name'] == c_name:
                    work = participant['contents']
                    break;
        except FileNotFoundError:
            print("Error: The file 'database.json' was not found.")
            return None
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None
    if not work: #no chat history for current user
        return None
    
    list_of_names = [name for name in work[0]]
    return list_of_names

#adds chat to right part in JSON file with use of helper function
def add_chat(username, target_name, message):
    #check if msg history exists first for that person
    _, message = message.split(",")

    chats = get_chats(username)
    chats2 =   get_chats(target_name)
    #print(f"username: {username}\ntarget: {target_name}")
    if not chats:
        print(f"No chats for {message}")
        return None

    # chats = [{'Zebra': {'messages': [{'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}]
    # chats[0] = {'Zebra': {'messages': [{'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}
    #ls = []
    for chat in chats:
        #print(f"chat var: {chat}")
        #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
        if target_name not in chat:
            #if chat history doesnt exist (idk how you will get here for rn)
            chat[target_name] = {'messages': [{'owner': username, 'contents': message, 'time': get_current_datetime()}]}
            return
        if chat[target_name] is not None and chat[target_name]:
            #{'Zebra': {'messages': [{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]}}
            history = chat[target_name]['messages']
            #[{'owner': 'Alice', 'contents': 'Whats cookin?', 'time': '2024-10-10T10:05:00'}, {'owner': 'Zebra', 'contents': 'All good here, just working.', 'time': '2024-10-10T10:10:00'}]
            history.append({'owner': username, 'contents': message, 'time': get_current_datetime()})
            break
    add_chats_helper(username=username, new_chats=chats)

    ###The above adds chats on one side, lets do the other for updating both chat arrays so when loading loads right:
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
            return None
        except json.JSONDecodeError:
            print("Error: The file is not a valid JSON.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None