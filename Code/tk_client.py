import tkinter as tk
from tkinter import Button, Entry, Frame, Label, PhotoImage, ttk, scrolledtext, messagebox
import socket
import threading
import logging
import time
import ast

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# protocols
DISCONNECT_MESSAGE = "!DISCONNECT"
LOGIN_MESSAGE = "!LOGIN"
AUTH_RESPONSE = "!CONNECTED"
HISTORY_MESSAGE = "!HISTORY"
ALL_CHATS = "!CHATS"
MSG = "!MSG"

HOST = socket.gethostbyname(socket.gethostname())
PORT = 8000

class ChatClientGUI:
    #master = root method (main method of tkinter)
    def __init__(self, master):
        self.master = master
        self.master.title("Instalink")
        self.master.geometry("925x500+300+200")
        self.master.configure(bg="#fff")
        self.master.resizable(False, False)
        self.master.img = PhotoImage(file='images/Logo.png')
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing) #just inits first frame window and adds function for when clicking X

        self.history = set() #for history (needs to be modified later since it only gives and sends update to get history from server once (when you click button on chat name))
        self.client_socket = None
        self.username = "" #your userbane
        self.respond = "" #Auth (if logged in then this is the AUTH message gotten back from server, used in check for if AUTH in repsond...)
        self.start_logo() #init widgets
    
    def on_closing(self):
        # Show a confirmation message box before closing
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.client_socket:
                try:
                    self.client_socket.send(str(len(DISCONNECT_MESSAGE)).encode('utf-8'))
                    time.sleep(1)
                    self.client_socket.send(DISCONNECT_MESSAGE.encode('utf-8'))
                    self.client_socket.close()
                except Exception as e:
                    logging.error(f"Error closing socket: {e}")
            
            # Close the application
            self.master.destroy()
                    
    #Basically sets up login without connecting until time to.
    def create_widgets(self):
        self.master.img = PhotoImage(file='images/login.png')
        Label(self.master, image=self.master.img, bg='white').place(x=50, y=50)
        
        self.main_frame = Frame(self.master, width=350, height=350, bg="white")
        self.main_frame.place(x=480, y=70)

        heading = Label(self.main_frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
        heading.place(x=100, y=5)
        
        # Login Frame
        
        self.username_entry = Entry(self.main_frame, width=25, fg='black', border=0, highlightthickness=0, bg="white", highlightbackground='white', font=('Microsoft YaHei UI Light', 11), insertbackground='black', insertwidth=2)
        self.username_entry.place(x=30, y=80)
        self.username_entry.insert(0, 'Username')
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.delete(0, 'end'))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.insert(0, 'Username') if self.username_entry.get() == '' else None)

        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=107)
        self.password_entry = Entry(self.main_frame, width=25, fg='black', border=0, highlightthickness=0, bg="white", font=('Microsoft YaHei UI Light', 11), insertbackground='black', insertwidth=2)
        self.password_entry.place(x=30, y=150)
        self.password_entry.insert(0, 'Password')
        self.password_entry.bind('<FocusIn>', lambda e: self.on_enter_password(self.password_entry))
        self.password_entry.bind('<FocusOut>', lambda e: self.on_leave_password(self.password_entry))
        
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=177)
        
        Button(self.main_frame, width=30, pady=7, text='Sign in', bg='#57a1f8', fg='white', border=0, command=self.login).place(x=25, y=204)
        label = Label(self.main_frame, text="Don't have an account?", fg='black', bg='white', font=('Microsoft YaHei UI Light', 9))
        label.place(x=75, y=270) ### this is WIP still 

    def on_enter_password(self, code):
        code.delete(0, 'end')
        code.config(show='*')
        
    def on_leave_password(self, code):
        name = code.get()
        if name == '':
            code.config(show='')  # Show normal text if empty
            code.insert(0, 'Password')
            
    def clear_screen(self, event):
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.unbind("<Key>")
        self.create_widgets()

    def start_logo(self):
        Label(self.master, image=self.master.img, bg='white').place(x=250, y=50)
        heading = Label(self.master, text='InstaLink', fg='#7703fc', bg='white', font=('Microsoft YaHei UI Light', 30, 'bold'))
        heading.place(x=375, y=5)
        self.master.bind("<Key>", self.clear_screen)
    
    #if here then gui for prev chats ran and it wants to get actual buttons where u click and go to talk to that person, currently no button to create new chat.
    def populate_chat_names(self):
        chat_names = self.prev_chats()
        if not chat_names:
            return None
        #print(type(chat_names))
        #print(chat_names)
        for idx, chat_name in enumerate(chat_names):
            button = ttk.Button(self.scrollable_frame, text=chat_name, command=lambda name=chat_name: self.init_dms(target=name))
            button.grid(row=idx, column=0, sticky="ew", pady=2)
            
    def prev_chats(self):
        payload = f"{ALL_CHATS},{self.username}"
        payload_len = len(payload)
        self.client_socket.send(str(payload_len).encode('utf-8'))
        time.sleep(1)
        self.client_socket.send(payload.encode('utf-8'))
        message = self.client_socket.recv(1024).decode('utf-8')
        if message and message is not None:
            return ast.literal_eval(message)
    
    #if here then succesfful login, clear frame from before and make new one of all chat history (that we may have to change?)
    def init_chat_area(self):
        # All Messages frame
        self.users_area_frame = ttk.Frame(self.main_frame, padding="10")
        self.users_area_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.users_area_frame.columnconfigure(0, weight=1)
        self.users_area_frame.rowconfigure(0, weight=1)
        
        ttk.Label(self.users_area_frame, text="Past Chats").grid(row=0, column=0, sticky=(tk.N, tk.E, tk.W))
        
        # Scrollable area for user names
        self.canvas = tk.Canvas(self.users_area_frame)
        self.scrollbar = ttk.Scrollbar(self.users_area_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        #just fancy lambda for custom clickable button in canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        # Populate the scrollable area with clickable chat names
        self.populate_chat_names()
    
    #if here then u clicked a button!! this clears GUi and sets up new GUi for chat area. this is all bare bones but everything shouldwork
    def init_dms(self, target): 
        # clear area
        threading.Thread(target=self.receive_messages_chat_area, daemon=True).start()
        self.users_area_frame.grid_remove()
        self.canvas.grid_remove()
        self.scrollbar.grid_remove()

        # Create the chat frame
        self.chat_frame = ttk.Frame(self.main_frame, padding="10", relief="solid", borderwidth=1)
        self.chat_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add chat area
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, width=50, height=20)
        self.chat_area.grid(column=0, row=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        ttk.Label(self.chat_frame, text=f"To: {target}").grid(column=0, row=1, sticky=tk.W)
        #Get histroy (for that specific person)
        threading.Thread(target=self.handle_history, args=(target,), daemon=True).start()
        
        # Add message box
        self.message_entry = ttk.Entry(self.chat_frame, text="Message:", width=30)
        self.message_entry.grid(column=0, row=2, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Button(self.chat_frame, text="Send", command=lambda: self.threadding_wrapper(self.send_message)).grid(column=1, row=3, sticky=tk.E)
        
        # Configure grid stuff
        self.chat_frame.columnconfigure(0, weight=1)
        self.chat_frame.rowconfigure(0, weight=1)

    #this is a thread
    def login_logic(self, password):
        self.client_socket.send(str(len(LOGIN_MESSAGE)).encode('utf-8'))
        time.sleep(1)
        self.client_socket.send(LOGIN_MESSAGE.encode('utf-8'))
        
        # Skip server prompts as we already have the username and password
        self.client_socket.recv(1024)  # Username prompt
        self.client_socket.send(self.username.encode('utf-8'))
        self.client_socket.recv(1024)  # Password prompt
        self.client_socket.send(password.encode('utf-8'))
        
        respond = self.client_socket.recv(1024).decode('utf-8')
        self.respond = respond
    def handle_auth(self): #need to make this somehow loop forever until AUTH response is returned but for now just sleep 2
        time.sleep(2)
        if AUTH_RESPONSE in self.respond:
            for widget in self.master.winfo_children():
                widget.destroy()
            ### TODO This needs work:
            self.main_frame = ttk.Frame(self.master, padding="10")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            threading.Thread(target=self.init_chat_area, daemon=True).start()
        else:
            messagebox.showerror("Authentication Error", "Invalid username or password")
            self.client_socket.close()
    
    #if here then button was clicked to login, handle using threads for no GUI freezing. (tbh idk what happens if you spam click the login button but don't do that)
    def login(self):
        self.username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not self.username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
            return
        
        login_thread = threading.Thread(target=self.login_logic, args=(password,), daemon=True)
        login_thread.start()
        ###idle here but not block
        auth_thread = threading.Thread(target=self.handle_auth, daemon=True)
        auth_thread.start()

    
    def receive_messages_chat_area(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message and message is not None:
                    self.chat_area.insert(tk.END, f"\n{message}")
                    self.chat_area.see(tk.END)
            except:
                print("Connection closed.")
                break
    #basically pass func into and will execute on thread (can use this for everything tbh I shouldve made this sooner)
    def threadding_wrapper(self, func):
        threading.Thread(target=func, daemon=True).start()
    
    #this probably needs to run on a thread itself too
    def send_message(self):
        message = self.message_entry.get()
        if not message:
            logging.info(f"got message: {message}")
            return

        # Send the message
        full_message = f"{MSG},{message}"
        self.client_socket.send(str(len(full_message)).encode('utf-8'))
        #insert to canvas, server handles history itself
        self.chat_area.insert(tk.END, f"\n{message}")
        self.chat_area.see(tk.END)
        #chill
        time.sleep(1)
        #send msg to server
        self.client_socket.send(full_message.encode('utf-8'))
        self.message_entry.delete(0, tk.END)

    #if here called from button function just gets history from server
    def handle_history(self, target):
        if target in self.history:
            return
        payload = f"{HISTORY_MESSAGE},{self.username},{target}"
        payload_len = len(payload)
        self.client_socket.send(str(payload_len).encode('utf-8'))
        time.sleep(1)
        self.client_socket.send(payload.encode('utf-8'))
        self.history.add(target)

def main():
    root = tk.Tk()
    ChatClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()