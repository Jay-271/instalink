import socket
import threading
import logging
import utils
import rsa

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

HEADER = 64
server_ip = socket.gethostbyname(socket.gethostname())
server_port = 8000
address = (server_ip, server_port)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
LOGIN_MESSAGE = "!LOGIN"
AUTH_RESPONSE = "!CONNECTED"
HISTORY_MESSAGE = "!HISTORY"
ALL_CHATS = "!CHATS"
CREATE_ACC = "!CREATE_ACCOUNT"
MSG = "!MSG"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(address)

username_lock = threading.Lock() #locks for write/read db
database_lock = threading.Lock()

#main thread per client connected, thinking of putting parts like login in a function but later ig
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    LOGGED_IN = False
    connected = True
    target_user = "" #Variables set as soon as history is made (aka button to chat between current user and reciever is clicked)
    curr_user = "" #Therefore we can assume still same user being messaged and will never be null (i hope?)
    
    
    try:
        with open("key/private.pem", 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
    except Exception as x:
        logging.error("FATAL - Cannot continue without private Key.\nClosing.")
        logging.info("Closing socket connection")
        conn.close()
        return -1
    
    while connected:
        msg_length_data = conn.recv(HEADER)
        msg_length = msg_length_data.decode(FORMAT).strip()  
        
        logging.info(f"msg_length is {msg_length}")
        if msg_length and msg_length.isdigit():
            msg_length = int(msg_length)
            msg = conn.recv(msg_length) # REMOVE decode here since its RSAed
            #logging.info(f"inside msg_length if and statement where msg is {msg}")
            if not msg:
                logging.info("No message")
                continue
            
            # Decode first:
            msg = rsa.decrypt(msg, private_key).decode(FORMAT)
            
            ###Check message type
            if DISCONNECT_MESSAGE in msg:
                logging.info("got disconnect message, breaking from loop")
                break
            ###Logging in stuff here
            if not LOGGED_IN:
                if CREATE_ACC in msg: #if u wanna create acc
                    with database_lock:
                        _, new_user, new_pass, new_pass2 = msg.split(',')
                        message = utils.add_account(new_user, new_pass, new_pass2)
                    conn.send(message.encode(FORMAT))
                    conn.close()
                    print("Exiting thread.")
                    return
                elif msg != LOGIN_MESSAGE: #if you sent something weird like tryin to access server functions without being logged in...
                    logging.error("Not logged in.")
                    break
                else:
                    #you did send login message but not yet logged in
                    # Ask client for their username and password
                    try:
                        conn.send("Enter your username: ".encode(FORMAT))
                        username = rsa.decrypt(conn.recv(1024), private_key).decode(FORMAT)
                        conn.send("Enter your password: ".encode(FORMAT))
                        password =rsa.decrypt(conn.recv(1024), private_key).decode(FORMAT)
                        if not utils.authenticate(username, password):
                            print(f"Invalid Credentials or user {username} does not exist.")
                            break
                        conn.send(AUTH_RESPONSE.encode(FORMAT))
                        LOGGED_IN = True
                        connected_clients[username] = {
                            'ip': addr[0],
                            'port': addr[1],
                            'connection': conn
                        }
                        print(f"{username} connected.")
                        continue
                    except Exception as e:
                        logging.error(f"Unexpected error: {e}")
                        logging.error("Quitting.")
                        break
            #If here then then client still connected
            if HISTORY_MESSAGE in msg:
                logging.info("getting history")
                with database_lock:
                    history = utils.get_chat_history(msg)
                _, curr_user, target_user = msg.split(',')
                if history is None:
                    #no previous chat history
                    continue
                for dm in history:
                    conn.send(f"{dm['owner']}: {dm['contents']}\n".encode(FORMAT))
                connected_clients[username]['chat_area']  = True #only update this here since i know from client code only in chat area if history message between user and sender
            if ALL_CHATS in msg:
                _, username = msg.split(',')
                chats = utils.get_chats_only(username)
                logging.info(f"Sent chat history of: {chats}")
                if chats is None:
                    conn.send("None".encode(FORMAT))
                conn.send(str(chats).encode(FORMAT))
            if MSG in msg:
                #append chat data
                with username_lock:
                    utils.add_chat(curr_user, target_user, msg)
                if connected_clients[username]['chat_area']:
                    utils.send_update_target(curr_user, target_user, msg, connected_clients) #dont need otherwise since they get chat history automagically anyways at beginning of opening chat.
            #Logging purposes
            if msg:
                logging.info(f"Got message: {msg}")

    logging.info("Closing socket connection")
    conn.close()
    if curr_user in connected_clients:
        del connected_clients[username] # Not active anymore
    logging.info("Returning...")
    return


connected_clients = {} # For storing active clients.

def start():
    print(f"[LISTENING] Server is listening on {server_ip}")
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()

