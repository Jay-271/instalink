import tkinter as tk
from tkinter import ttk
from datetime import datetime

# Sample chat data to simulate conversation history
chat_data = {
    "Alice": [
        {"sender": "Alice", "message": "Hey Zebra, how's your day going?", "time": "2024-10-10T10:05:00"},
        {"sender": "Zebra", "message": "Hey Alice! It's going well, just busy with work. How about you?", "time": "2024-10-10T10:07:00"}
    ]
}

class ChatApp:
    def __init__(self, root):
        """Initialize the Chat Application GUI."""
        self.root = root
        self.root.title("Enhanced Chat App")
        self.root.geometry("500x700")

        # Configure styles for consistency
        self._configure_styles()

        # Create the chat display section
        self._create_chat_display()

        # Create the message input section
        self._create_message_input()

        # Load chat history for the user
        self.load_chat_history("Alice")

    def _configure_styles(self):
        """Configure styles for the application."""
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 12))
        style.configure("Header.TLabel", font=("Arial", 14, "bold"))

    def _create_chat_display(self):
        """Set up the chat display area."""
        self.chat_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable chat area
        self.chat_canvas = tk.Canvas(self.chat_frame, bg="#f5f5f5", highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_scrollbar = ttk.Scrollbar(self.chat_frame, orient=tk.VERTICAL, command=self.chat_canvas.yview)
        self.chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)
        self.chat_inner_frame = tk.Frame(self.chat_canvas, bg="#f5f5f5")
        self.chat_canvas.create_window((0, 0), window=self.chat_inner_frame, anchor="nw")

        # Update scroll region dynamically
        self.chat_inner_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

    def _create_message_input(self):
        """Set up the message input area."""
        self.input_frame = tk.Frame(self.root, bg="#ffffff")
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.message_entry = ttk.Entry(self.input_frame, font=("Arial", 12))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind("<Return>", self._handle_send_message)

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self._handle_send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5)

    def load_chat_history(self, user):
        """Load and display chat messages for a given user."""
        # Clear existing messages
        for widget in self.chat_inner_frame.winfo_children():
            widget.destroy()

        # Display chat history
        if user in chat_data:
            for message in chat_data[user]:
                self._display_message(message["sender"], message["message"], message["time"])

    def _display_message(self, sender, message, timestamp):
        """Display a single message in the chat window."""
        formatted_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").strftime("%I:%M %p")
        
        # Create a message bubble
        bubble_frame = tk.Frame(self.chat_inner_frame, bg="#f5f5f5", pady=5)
        bubble_frame.pack(anchor="w" if sender == "Alice" else "e", padx=10)

        bubble_label = tk.Label(
            bubble_frame,
            text=f"{sender}: {message}\n{formatted_time}",
            bg="#d1e7dd" if sender == "Alice" else "#f8d7da",
            wraplength=350,
            justify="left" if sender == "Alice" else "right",
            font=("Arial", 12),
            padx=10,
            pady=5,
            relief=tk.RAISED
        )
        bubble_label.pack()

    def _handle_send_message(self, event=None):
        """Handle the event of sending a message."""
        message_text = self.message_entry.get().strip()
        if message_text:
            # Add message to chat history
            current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            chat_data["Alice"].append({"sender": "Alice", "message": message_text, "time": current_time})

            # Display the new message
            self._display_message("Alice", message_text, current_time)

            # Clear the message entry
            self.message_entry.delete(0, tk.END)

# Run the Chat Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
