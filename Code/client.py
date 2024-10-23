import socket
import threading
import logging
import time
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
DISCONNECT_MESSAGE = "!DISCONNECT"
LOGIN_MESSAGE = "!LOGIN"
AUTH_RESPONSE = "!CONNECTED"
HISTORY_MESSAGE = "!HISTORY"

#######
# Remember to send length of msg first before sending actual msg.
######
# Server Information
HOST = socket.gethostbyname(socket.gethostname())
PORT = 8000  # Server Port


# Handle receiving messages
def receive_messages(username, client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message and message is not None:
                print(f"\n{message}")
        except:
            print("Connection closed.")
            break


# Handle sending messages
def send_messages(username, client_socket):
    def handle_history(username, target):
        payload = f"{HISTORY_MESSAGE},{username},{target}"
        payload_len = len(payload)
        client_socket.send(str(payload_len).encode('utf-8'))
        time.sleep(1)
        client_socket.send(payload.encode('utf-8'))
    #gets history if exists
    dm_history = set()
    while True:
        message = input(f"Message to (enter a name): ")
        if DISCONNECT_MESSAGE in message:
            client_socket.send(str(len(DISCONNECT_MESSAGE)).encode('utf-8'))
            time.sleep(1)
            client_socket.send(str(DISCONNECT_MESSAGE).encode('utf-8'))
            break
        if message not in dm_history:
            handle_history(username, message)
            dm_history.add(message)
        time.sleep(1)
        message = input(f"Please enter contents to send to {message} or press [ENTER]:")
        if DISCONNECT_MESSAGE in message:
            client_socket.send(str(len(DISCONNECT_MESSAGE)).encode('utf-8'))
            time.sleep(1)
            client_socket.send(str(DISCONNECT_MESSAGE).encode('utf-8'))
            logging.info("Sent disconnect message")
            break
        client_socket.send(str(len(message)).encode('utf-8'))
        time.sleep(1)
        client_socket.send(message.encode('utf-8'))
    logging.info("Closing socket")
    client_socket.close()
    logging.info("returning...")
    return
    


# Start client and connect to server
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    client_socket.send(str(len(LOGIN_MESSAGE)).encode('utf-8'))
    logging.info(f"sent size of {str(len(LOGIN_MESSAGE))}")
    time.sleep(1)
    client_socket.send(LOGIN_MESSAGE.encode('utf-8'))    
    logging.info(f"Sent {LOGIN_MESSAGE}")
    # Enter username and password
    username = input(client_socket.recv(1024).decode('utf-8'))

    client_socket.send(username.encode('utf-8'))

    password = input(client_socket.recv(1024).decode('utf-8'))
    client_socket.send(password.encode('utf-8'))

    # Check if authentication is successful
    auth_response = client_socket.recv(1024).decode('utf-8')

    if AUTH_RESPONSE in auth_response:
        logging.info("Connected to server!")
        # Start a thread to receive messages
        receive_thread = threading.Thread(target=receive_messages, args=(username,client_socket,))
        receive_thread.start()

        # Start a thread to send messages
        send_thread = threading.Thread(target=send_messages, args=(username, client_socket,))
        send_thread.start()
    else:
        logging.error("Error connecting due to invalid credentials.")
        client_socket.close()


if __name__ == "__main__":
    logging.warn("DEPECRATED - DO NOT USE")
    start_client()
