import socket
import threading
import logging
import utils
import rsa
import signal #stopping with CTRL + C
import select # ^

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
APPEND_CHAT_AREA = """!~<>~{""" #THIS IS NOT REGEX, we use REGEX CHECK to check for this

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
    
    while connected and not shutdown_flag.is_set():  # if server closed then kill thread. need to add handling for client on sudden connection loss if server dies randomly.
        
        ready = select.select([conn], [], [], 1.0)  # 1 second timeout
        if ready[0]:
            try:
                msg_length_data = conn.recv(HEADER)
                msg_length = msg_length_data.decode(FORMAT).strip()  
                
                logging.info(f"[NEW MESSAGE] - msg_length is {msg_length}")
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
                            conn.send(f"{APPEND_CHAT_AREA}{dm['owner']}: {dm['contents']}\n".encode(FORMAT)) #New protocol to append if in chat area
                            print(f"sending: {APPEND_CHAT_AREA}{dm['owner']}: {dm['contents']}\n")
                        connected_clients[username]['chat_area']  = True #only update this here since i know from client code only in chat area if history message between user and sender
                    if ALL_CHATS in msg:
                        _, username = msg.split(',')
                        chats = utils.get_chats_only(username)
                        logging.info(f"Sent chat history of: {chats}")
                        if chats is None:
                            conn.send("None".encode(FORMAT))
                        conn.send(str(chats).encode(FORMAT))
                        print(f"sending: {chats}")
                    if MSG in msg:
                        #append chat data
                        with username_lock:
                            utils.add_chat(curr_user, target_user, msg)
                        if connected_clients[username]['chat_area']:
                            utils.send_update_target(curr_user, target_user, msg, connected_clients) #dont need otherwise since they get chat history automagically anyways at beginning of opening chat.
                    #Logging purposes
                    if msg:
                        logging.info(f"Got message: {msg}")
            except socket.error: #if error (like client closes)
                break

    logging.info("Closing socket connection")
    conn.close()
    if curr_user in connected_clients:
        del connected_clients[username] # Not active anymore
    logging.info("Returning...")
    return

def signal_handler(sig, frame):
    """Handle CTRL+C shutdown"""
    print("\n[INFO] Server is shutting down...")
    shutdown_flag.set()  # Set the shutdown flag
    
    # Close all client connections
    for client_info in connected_clients.values():
        try:
            client_info['connection'].close()
        except:
            pass
    connected_clients.clear()
    
    # Create a dummy connection to unblock accept()
    try:
        dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy.connect((server_ip, server_port))
        dummy.close()
    except:
        pass

connected_clients = {} # For storing active clients.
shutdown_flag = threading.Event()  # global flag to shutdown

def start():
    print(f"[LISTENING] Server is listening on {server_ip}")
    server.listen()
    signal.signal(signal.SIGINT, signal_handler) #Added for stopping server with CTRL + C
    while not shutdown_flag.is_set():
        try:
            # Use select to make accept() interruptible
            ready = select.select([server], [], [], 1.0)  # 1 second timeout -> Check bottom
            if ready[0]:
                conn, addr = server.accept()
                if shutdown_flag.is_set():  # check flag again after timeout
                    conn.close()
                    break
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except Exception as e:
            if not shutdown_flag.is_set():  # Only log if not shutting down
                print(f"[ERROR] {e}")
            break
    
    print("[INFO] Server shutdown complete")

print("[STARTING] server is starting...")
start()

###### Additional Comments:
### FOR CODE ### 
# ready = select.select([server], [], [], 1.0)
# ----
# wait up to 1 sec to see if `server` has any data ready to read
# - select.select() checks list of sockets to see if they're ready for something (shown below)
# - first list ([server]) is sockets we wanna check for *read readiness*
# - second list ([]) is for sockets we wanna check for *write readiness* (not using here)
# - third list ([]) is for sockets we wanna check for *errors* (also not using here)
# - last part (1.0) is timeout in seconds:
#      * if `server` is ready in 1 sec, `ready` will have `[server]`
#      * if not, `ready` will just be empty `[]`
# lets us check for data without getting stuck waiting forever
# What data???? CTRL + C 
# https://docs.python.org/3/library/select.html
# ----

### FOR FUNCTION ### signal_handler 
# ---- 
# Handle CTRL+C shutdown for the server
# - Print a message to let us know shutdown started
# - Set the shutdown flag to signal other parts of the server to stop
# - Close each client connection in connected_clients:
#   - For each client, try to close the connection
#   - Ignore any errors (e.g., if client already disconnected)
#   - Clear out connected_clients to remove references to closed connections
# - Create a dummy connection to the server:
#   - This is to "wake up" the server if it's stuck in accept() waiting for a connection
#   - Connect and immediately close the dummy socket to unblock the server's accept() call
# - This whole function ensures the server shuts down cleanly and frees up resources
# ----