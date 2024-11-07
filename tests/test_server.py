# tests/test_server.py
import threading
import time
import pytest
from io import StringIO
from contextlib import redirect_stdout
from Code import main

@pytest.fixture(scope="module")
def start_server():
    #start on thread
    server_thread = threading.Thread(target=main.start, daemon=True)
    with StringIO() as buf, redirect_stdout(buf):
        server_thread.start()
        #wait for server to start
        time.sleep(1)
        yield buf  # gives output to the test function

def test_server_startup(start_server):
    output = start_server.getvalue()  # Retrieve captured output
    
    # Verify that the expected startup messages are present
    assert "[STARTING] server is starting..." in output, "Server should print start message."
    assert "[LISTENING] Server is listening on" in output, "Server should indicate it is listening."