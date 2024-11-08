# Team Assignments: Personas, Scenarios, and Features
- Find this in the `wiki` section.

# Main coding branch (since it has issues)

## TO RUN:
Run git clone (this repo)
> pip install the requirements.txt

> Open Terminal First, CD into directory where downloaded files are.
* RUN `main.py` with `python3 main.py`
    - TO STOP server do ctrl+c on keyboard on terminal where server is running.
    
> Open another terminal in directory where downloaded files are first then:
* RUN `tk_client.py` with `python3 tk_client.py`
    - TO EXIT just click the X in the GUI.

> Note there may be errors, if so shoot Jason a msg on teams or make an issue.

## TODO:

- Just so I (Jason) Don't forget: Fix (well not fix but will be good to) add a JSON in between people. What I mean is:

Currently -> WHOLE messages DB is replaced by new version using a lock when anyone sends any message to any user -> but this is innefecient. 

Need something (Maybe make new JSON temp db for a specific chat between users then simply append those chats?), etc.

- There is also the issue with "knowing" when the client(s) are chatting with each other. Currently it follows this pattern:
    - We "know" client is in a specifc chat area because of the !HiSTORY (user1), (user2) and sets their own flag of in chat area to true
    - When 2 people, say Alice and Bob are in each other's chat area, we check this server side by going into the dictionary of all clients.
    From Alice POV:
    ```py
    if dictionary['bob']['in_chat_area_flag'] is true:
        #check from alice pov if Bob is in chat area
        #save chat to server
        #then send message to bob using bob's socket -> why? because client side there is a thread already appending to chat area.
    ```
    From Bob POV:
    ```py
    if dictionary['Alice']['in_chat_area_flag'] is true:
        #check from Bob pov if Alice is in chat area
        #save chat to server
        #then send message to alice using her own socket -> why? because client side there is a thread already appending to chat area.
    ```
Currently, there is no logic for when they exit and checking they are inside the chat area itself is also a "grey flag". Maybe we can have Client tell us "I'm in the chat area server" and the server THEN updates the flag?