import tkinter as tk
from tkinter import Button, Entry, Frame, Label, PhotoImage, ttk, scrolledtext, messagebox
import socket
import threading
import logging
import time
import ast
import rsa


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
CREATE_ACC = "!CREATE_ACCOUNT"
FORMAT = "utf-8"
HEADER = 64

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
        self.username = None #your userbane
        self.respond = None #Auth (if logged in then this is the AUTH message gotten back from server, used in check for if AUTH in repsond...)
        self.pub_key = None
        self.get_key()
        self.start_logo() #init widgets
    
    # sending encrypted messages functionality
    ########################################
    def get_key(self):
        try:
            with open("key/public.pem", 'rb') as f:
                self.pub_key = rsa.PublicKey.load_pkcs1(f.read())
        except Exception as x:
            logging.error("FATAL - Cannot continue without Public Key.\nClosing.")
            self.master.destroy()
    #Only for txt for now
    def encode(self, msg):
        assert isinstance(msg, str)
        return rsa.encrypt(msg.encode(encoding=FORMAT), self.pub_key)
    #Assuming you have a message to send to the server we can now use this wrapper function
    def communicate(self, msg):
        enc_msg = self.encode(msg)
        enc_msg_len = len(enc_msg)
        msg_length = str(enc_msg_len).encode(encoding=FORMAT)
        msg_length = msg_length.ljust(HEADER)
        
        self.client_socket.send(msg_length)
        time.sleep(1)
        self.client_socket.send(enc_msg)
    ## A special version for sending password and username
    def communicate_pass(self, password):
        # Skip server prompts as we already have the username and password
        self.client_socket.recv(1024)  # Username prompt being eaten
        self.client_socket.send(self.encode(self.username))
        
        self.client_socket.recv(1024)  # Password prompt being eaten
        self.client_socket.send(self.encode(password))
    
    def communicate_newacc(self, msg):
        enc_msg = self.encode(msg)
        enc_msg_len = len(enc_msg)
        msg_length = str(enc_msg_len).encode(encoding=FORMAT)
        msg_length = msg_length.ljust(HEADER)
        
        self.client_socket.send(msg_length)
        time.sleep(1)
        self.client_socket.send(enc_msg)
        return self.client_socket.recv(1024)
    #########################################################################
    
    def on_closing(self):
        # Show a confirmation message box before closing
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if self.client_socket and self.client_socket.fileno() != -1: # returns positive int if socket open, else -1
                try:
                    self.communicate(DISCONNECT_MESSAGE)
                    self.client_socket.close()
                except Exception as e:
                    logging.error(f"Error closing socket: {e}")
            
            # Close the application
            self.master.destroy()
    
    #Basically sets up login without connecting until time to.
    def create_widgets(self):
        self.master.img = PhotoImage(file='images/login.png')
        Label(self.master, image=self.master.img, bg='white').place(x=50, y=50)
        
        self.main_frame = Frame(self.master, width=350, height=350, bg="white") #frame for login
        self.main_frame.place(x=480, y=70)

        heading = Label(self.main_frame, text='Sign in', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
        heading.place(x=100, y=5) #label with sign in text
        
        #Entry for username field        
        self.username_entry = Entry(self.main_frame, width=25, fg='black', border=0, highlightthickness=0, bg="white", highlightbackground='white', font=('Microsoft YaHei UI Light', 11), insertbackground='black', insertwidth=2)
        self.username_entry.place(x=30, y=80)
        self.username_entry.insert(0, 'Username')
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.delete(0, 'end'))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.insert(0, 'Username') if self.username_entry.get() == '' else None)

        #new frame for password entry
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=107)
        self.password_entry = Entry(self.main_frame, width=25, fg='black', border=0, highlightthickness=0, bg="white", font=('Microsoft YaHei UI Light', 11), insertbackground='black', insertwidth=2)
        self.password_entry.place(x=30, y=150)
        self.password_entry.insert(0, 'Password')
        self.password_entry.bind('<FocusIn>', lambda e: self.on_enter_password(self.password_entry))
        self.password_entry.bind('<FocusOut>', lambda e: self.on_leave_password(self.password_entry))
        
        #new frame for button to sign in
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=177)
        self.sign_in_button = Button(self.main_frame, width=30, pady=7, text='Sign in', bg='#57a1f8', fg='white', border=0, command=self.login)
        self.sign_in_button.place(x=25, y=204)
        
        #label + button for no acc page
        self.no_acc_label = Label(self.main_frame, text="Don't have an account?", fg='black', bg='white', font=('Microsoft YaHei UI Light', 9))
        self.no_acc_label.place(x=75, y=270) 
        self.btn_sign_up = Button(self.main_frame, width=6, text='Sign up', border=0, bd=0, highlightthickness=0, highlightbackground='white', highlightcolor='white', relief='flat', bg='white', fg='#57a1f8', command=lambda: self.sign_up_page())
        self.btn_sign_up.place(x=215, y=270)
        
    def sign_up_page(self):
        #make sure its clear, load img
        self.clear_window()
        self.master.img = PhotoImage(file='images/signup.png')
        Label(self.master, image=self.master.img, bg='white').place(x=50, y=90)
        
        #create frame + label with main sign up text
        self.main_frame = Frame(self.master, width=350, height=390, bg='#fff')
        self.main_frame.place(x=480, y=50)
        heading = Label(self.master, text='Sign up', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI', 23, 'bold'))
        heading.place(x=100, y=5)
        
        #make new entry in same frame for username field
        self.username_entry = Entry(self.main_frame, width=25, fg='black', bg='white', border=0, highlightthickness=0, font=('Microsoft YaHei UI', 11), insertbackground='black', insertwidth=2)
        self.username_entry.place(x=30, y=80)
        self.username_entry.insert(0, 'Username')
        self.username_entry.bind('<FocusIn>', lambda e: self.username_entry.delete(0, 'end'))
        self.username_entry.bind('<FocusOut>', lambda e: self.username_entry.insert(0, 'Username') if self.username_entry.get() == '' else None)
        
        #make new frame + entry for password
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=107)
        self.password_entry = Entry(self.main_frame, width=25, fg='black', border=0, highlightthickness=0, bg="white", font=('Microsoft YaHei UI Light', 11), insertbackground='black', insertwidth=2)
        self.password_entry.place(x=30, y=150)
        self.password_entry.insert(0, 'Password')
        self.password_entry.bind('<FocusIn>', lambda e: self.on_enter_password(self.password_entry))
        self.password_entry.bind('<FocusOut>', lambda e: self.on_leave_password(self.password_entry))
        
        #make new frame + confirm pass
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=177)
        self.confirm = Entry(self.main_frame, width=25, fg='black', bg='white', border=0, highlightthickness=0, font=('Microsoft YaHei UI', 11), insertbackground='black', insertwidth=2)
        self.confirm.place(x=30, y=220)
        self.confirm.insert(0, 'Confirm Password')
        self.confirm.bind('<FocusIn>', lambda e: self.on_enter_password(self.confirm))
        self.confirm.bind('<FocusOut>', lambda e: self.on_leave_confirm_password(self.confirm))
        
        #make new frame + button for new acc creation (TODO - actual functionality)
        Frame(self.main_frame, width=295, height=2, bg='black').place(x=25, y=247)
        self.new_acc_btn = Button(self.main_frame, width=30, pady=7, text='Sign up', bg='#57a1f8', fg='#57a1f8', border=0, command= lambda: self.signup())
        self.new_acc_btn.place(x=35,y=280)
        
        #new label + button  to go back to login page
        self.some_label = Label(self.main_frame, text='I have an account', fg='#57a1f8', border=0, bd=0, highlightthickness=0, highlightbackground='white', highlightcolor='white', relief='flat', bg='white', font=('Microsoft YaHei UI', 9)).place(x=90,y=340)
        self.master.bind('<Return>', lambda event: self.signup())
        self.back_to_login_btn = Button(self.main_frame, width=6, text='Sign in', border=0, bd=0, highlightthickness=0, highlightbackground='white', highlightcolor='white', relief='flat', bg='white', fg='#57a1f8', command=lambda : self.back_to_login())
        self.back_to_login_btn.place(x=200, y=340)
        
    def signup(self):
        #if clicked once diable until done.
        self.new_acc_btn.config(state='disabled')
        
        username=self.username_entry.get()
        password=self.password_entry.get()
        confirm_password=self.confirm.get()

        data = f"{CREATE_ACC},{username},{password},{confirm_password}"

        if password==confirm_password:
            ###Create socket to connect temp:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.client_socket.connect((HOST, PORT))
            except Exception as e:
                messagebox.showerror("Connection Error", f"Unable to connect to server: {e}")
                return
            
            message = self.communicate_newacc(data).decode(FORMAT)
            self.client_socket.close()
            if "Successful account creation" in message:
                messagebox.showinfo("Signup", f"{message}")
                if self.new_acc_btn and self.new_acc_btn.winfo_exists():
                    self.new_acc_btn.config(state='normal')
                self.back_to_login()
            else:
                messagebox.showerror("Error", f"{message}")
        else:
            messagebox.showerror("Error", "Passwords do not match")    
        if self.new_acc_btn and self.new_acc_btn.winfo_exists():
                    self.new_acc_btn.config(state='normal')
    ## Helper functions for login gui
    ###########################################
    
    #asthetic
    def on_enter_password(self, code):
        code.delete(0, 'end')
        code.config(show='*') 
    #asthetic
    def on_leave_password(self, code):
        name = code.get()
        if name == '':
            code.config(show='')  # Show normal text if empty
            code.insert(0, 'Password')
    #asthetic
    def on_leave_confirm_password(self, code):
        name = code.get()
        if name == '':
            code.config(show='')  # Show normal text if empty
            code.insert(0, 'Confirm Password')
    
    #only used at beginning (after pressing enter to remove main logo)
    def clear_screen(self, event): 
        for widget in self.master.winfo_children():
            widget.destroy()
        self.master.unbind("<Key>")
        self.create_widgets()
    
    #used by sign up page
    def back_to_login(self):
        self.clear_window()
        self.create_widgets()
    
    #more generic version of cleanup
    def clear_window(self): 
        for widget in self.master.winfo_children():
            widget.destroy()

    # basically start with logo, remove and actually start gui on any button key press
    def start_logo(self):
        Label(self.master, image=self.master.img, bg='white').place(x=250, y=50)
        heading = Label(self.master, text='InstaLink', fg='#7703fc', bg='white', font=('Microsoft YaHei UI Light', 30, 'bold'))
        heading.place(x=375, y=5)
        self.master.bind("<Key>", self.clear_screen)
    ###########################################################
    
    
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
        
        self.communicate(payload)        
        message = self.client_socket.recv(1024).decode(FORMAT)
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
        
        self.communicate(LOGIN_MESSAGE)
        self.communicate_pass(password=password)
        
        respond = self.client_socket.recv(1024).decode(FORMAT)
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
            if self.sign_in_button and self.sign_in_button.winfo_exists():  # Check if the button still exists
                self.master.after(0, lambda: self.sign_in_button.config(state='normal'))
            self.client_socket.close()
    
    #if here then button was clicked to login, handle using threads for no GUI freezing. (tbh idk what happens if you spam click the login button but don't do that)
    def login(self):
        self.sign_in_button.config(state='disabled')
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
            if self.sign_in_button and self.sign_in_button.winfo_exists():  # Check if the button still exists
                self.master.after(0, lambda: self.sign_in_button.config(state='normal'))
            return
        
        login_thread = threading.Thread(target=self.login_logic, args=(password,), daemon=True)
        login_thread.start()
        ###idle here but not block
        auth_thread = threading.Thread(target=self.handle_auth, daemon=True)
        auth_thread.start()

    
    def receive_messages_chat_area(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode(FORMAT)
                if message and message is not None: # get history/listener that inserts into chat frame area
                    self.chat_area.insert(tk.END, f"{message}")
                    self.chat_area.see(tk.END)
                    pass
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

        pattern = """~<>~{"""
        # Send the message
        full_message = f"{MSG}{pattern}{message}"
        self.communicate(full_message)
        #insert to canvas, server handles history itself
        self.chat_area.insert(tk.END, f"{self.username}: {message}\n")
        self.chat_area.see(tk.END)
        self.message_entry.delete(0, tk.END)

    #if here called from button function just gets history from server
    def handle_history(self, target):
        if target in self.history:
            return
        payload = f"{HISTORY_MESSAGE},{self.username},{target}"
        self.communicate(payload)
        self.history.add(target)

def main():
    root = tk.Tk()
    ChatClientGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    