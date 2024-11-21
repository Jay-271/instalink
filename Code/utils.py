import json
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
def to_gpt(msg, database_lock, user, target):
    """"
    Loads env file with api key to openai and sends chat completion
    
    Returns response from openai or error
    """
    # Path to the .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), 'key', '.env')
    load_dotenv(dotenv_path)
    api_key = os.getenv("GPT_TOKEN")
    client = OpenAI(
        api_key = api_key
    )

    conversation = []
    init_convo = { "role": "system", "content": "You are a helpful assistant. Be intruiguing when answering requests or simply continue the conversation. Always respond with something to add.\nBe CONCISE."}
    conversation.append(init_convo)
    ### Split data -> Comes in form of !HISTORY,target,user {pattern} prompt for ai
    left, right = gpt_msg_splitter(msg, user, target)
    print(f"{left=}\n{right=}")
    #### 
    if left is None or right is None:
        return "Error with messaging parsing."
    
    with database_lock:
        history = get_chat_history(left) # needs message to be in format protocol,target,user seprated by a comma...
    if history is not None:
        #no previous chat history, load default config
        for dm in history:
            if dm['owner'] == 'Chat':
                conversation.append({ "role": "assistant", "content": dm['contents']})
            else:
                conversation.append({ "role": "user", "content": dm['contents']})        
    ### after here messages convo is ready. lets send the prompt.
    conversation.append({ "role": "user", "content": f"{right}\nRemember to be concise."})
    conversation = conversation[:19]
    if len(conversation) == 19:
        #if messages were cut off then take first 19, reverse, append system message, re-reverse to have correct order.
        conversation  = conversation[::-1]
        conversation.append(init_convo)
        conversation  = conversation[::-1]
    print(f"The conversation thus far is: {conversation}")
    try:
        # Call the Chat Completions API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=conversation,  # Replace with first 20 msgs
            stream=False
        )
        # Process the response
        response = response.choices[0].message.content
        print(response)
        return response
    except Exception as e:
        # Handle errors from the OpenAI API
        print(f"An error occurred: {e}")
        return "Error during request. Please try again later."
def gpt_msg_splitter(msg, user, target):
    # Regex to match the pattern
    pattern = r'^!(.*?)~<>~\{(.*)$'
    try:
        print(f"Currently matching -> {msg}")
        match = re.match(pattern, msg)
        if not match:
            raise Exception("Error: Invalid message")
        print(f"Matched!")
        msg = match.group(2) 
    except Exception as e:
        return None
    format_left = f"!HISTORY,{target},{user}"
    return format_left, msg

def get_current_datetime():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%dT%H:%M:%S")
    return formatted_date

def load_users():
    with open('usernames.json', 'r') as file:
        return json.load(file)

# Check if username and password are valid
def authenticate(username, password):
    user_db = load_users()
    ph = PasswordHasher()
    try:
        # Retrieve the stored hash for the username
        stored_hash = user_db["users"].get(username)
        if not stored_hash:
            print("Username not found or incorrect hash!")
            return False
        
        # Verify the input password against the stored hash
        if ph.verify(stored_hash, password):
            print(f"Password verification successful for {username}!")
            return True
    except VerifyMismatchError:
        print("Incorrect password.")
    return False
###########
# Ex use for dummy accs:
# validate_password("Alice", "password123")  # Should print "Login successful for Alice!"
# validate_password("Bob", "wrongPass")      # Should print "Incorrect password."
# validate_password("Zebra", "zebra123")     # Should print "Login successful for Zebra!"
###########

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

#adds chat to right part in JSON file with use of helper function
def add_chat(username, target_name, message):
    #Refractored completely, was too nested.
    pattern = r'^!(.*?)~<>~\{(.*)$'
    try:
        match = re.match(pattern, message)
        if not match:
            raise Exception("Error: Invalid message")
        message = match.group(2) 
    except Exception as e:
        return print(e)
    
    # Get current chats for both users
    chats = get_chats(username)
    chats2 = get_chats(target_name)
    
    # Create new message entry
    new_message = {
        'owner': username,
        'contents': message,
        'time': get_current_datetime()
    }

    # Handle first user's chat history (sender)
    if not chats:  # No existing chats for first user
        new_chat = [{  # Create first chat entry
            target_name: {
                'messages': [new_message]
            }
        }]
        add_chats_helper(username=username, new_chats=new_chat)
    else:  # Existing chats for first user
        chat_found = False
        # Look in the first (and should be only) object in contents array
        if len(chats) > 0:
            if target_name in chats[0]:
                chats[0][target_name]['messages'].append(new_message)
                chat_found = True
            
            if not chat_found:
                # Add to existing object instead of creating new one
                chats[0][target_name] = {
                    'messages': [new_message]
                }
        add_chats_helper(username=username, new_chats=chats)

    # Handle second user's chat history (receiver)
    if not chats2:  # No existing chats for second user
        # Create new entry in database for target user if they don't exist
        new_chat = [{  # Create first chat entry
            username: {
                'messages': [new_message]
            }
        }]
        # Create new user entry in database if they don't exist
        with open('database.json', 'r+') as db:
            data = json.load(db)
            user_exists = False
            for participant in data['chat']:
                if participant['name'] == target_name:
                    user_exists = True
                    break
            
            if not user_exists:
                # Add new user to database
                data['chat'].append({
                    "name": target_name,
                    "contents": new_chat
                })
                db.seek(0)
                json.dump(data, db, indent=4)
                db.truncate()
            else:
                add_chats_helper(username=target_name, new_chats=new_chat)
    else:  # Existing chats for second user
        chat_found = False
        # Look in the first (and should be only) object in contents array
        if len(chats2) > 0:
            if username in chats2[0]:
                chats2[0][username]['messages'].append(new_message)
                chat_found = True
            
            if not chat_found:
                # Add to existing object instead of creating new one
                chats2[0][username] = {
                    'messages': [new_message]
                }
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
    
    if len(username) > 30:
        return f"Username Length too large. Please enter a length less than 30 chars."
    if len(password) < 5:
        return f"Password length too short. Enter a size greater than 5 chars."
    
    ph = PasswordHasher()
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
                users['users'][username] = ph.hash(password)
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

def send_update_target(curr_user, target_user, msg, client_dict, APPEND_CHAT_AREA):
    #check if client connected on opposite end, if so send message... how?
    pattern = r'^!(.*?)~<>~\{(.*)$'
    try:
        print(f"Currently matching -> {msg}")
        match = re.match(pattern, msg)
        if not match:
            raise Exception("Error: Invalid message")
        print(f"Matched!")
        msg = match.group(2) 
    except Exception as e:
        return print(e)
    
    if not target_user in client_dict:
        return
    client_dict[target_user]['connection'].send(f"{APPEND_CHAT_AREA}{curr_user}: {msg}\n".encode('utf-8')) #use their socket since we know it exists to send them amessage just as we would before. 
    return
def search_target(target):
    user_db = load_users()
    users = user_db["users"]
    if target in users:
        return True
    return False