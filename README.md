# Team Assignments, Homeworks, Etc
- Find this in the `wiki` section.

# A more readable human version of what our program does (WIP):

[Guide.md](guide/guide.md)


# **Please create a virtual environment and then run these commands**
----

## TO RUN:

Run `git clone` on (this repo)
Run the command below:
> pip install -r requirements.txt

> CD into `code` directory where main.py and tkclient.py files are.
* RUN `main.py` with `python3 main.py`
    - TO STOP server do ctrl+c on keyboard on terminal where server is running.
    
> Open another terminal in directory where downloaded files are first then:
* RUN `tk_client.py` with `python3 tk_client.py`
    - TO EXIT just click the X in the GUI.

> Note there may be bugs but no errors. If so shoot Jason a msg on teams or make an issue.

## TODO/Notes:

- Just so I (Jason) Don't forget: Fix (well not fix but will be good to) add a JSON in between people. What I mean is:

Currently -> WHOLE messages DB is replaced by new version using a lock when anyone sends any message to any user -> but this is innefecient. 

Need something (Maybe make new JSON temp db for a specific chat between users then simply append those chats?), etc.
