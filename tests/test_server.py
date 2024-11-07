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

def test_server_startup_and_shutdown(start_server):
    output = start_server.getvalue()  # Retrieve captured output

    # Verify that the server starts correctly
    assert "[STARTING] server is starting..." in output, "Server should print the start message."
    assert "[LISTENING] Server is listening on" in output, "Server should indicate it is listening."

    # Simulate a shutdown by raising a KeyboardInterrupt (this is what `CTRL+C` would trigger)
    # This should cause the server to cleanly shut down
    try:
        raise KeyboardInterrupt
    except KeyboardInterrupt:
        # The server should print shutdown logs
        time.sleep(1)  # Wait for server shutdown logs to be captured
        shutdown_output = start_server.getvalue()
        assert "[INFO] Server is shutting down..." in shutdown_output, "Server should print shutting down message."
        assert "[INFO] Server shutdown complete" in shutdown_output, "Server should indicate it has completed shutdown."