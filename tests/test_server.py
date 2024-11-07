# tests/test_server.py
import os
import threading
import time
import pytest
from io import StringIO
from contextlib import redirect_stdout
from Code import main
import signal

@pytest.fixture(scope="module")
def start_server():
    # Create a StringIO buffer before starting the thread
    buf = StringIO()
    
    # Start server in a thread
    server_thread = threading.Thread(target=main.start, daemon=True)
    
    with redirect_stdout(buf):
        server_thread.start()
        time.sleep(1)
        # Get initial output
        startup_output = buf.getvalue()
        
        # Clear the buffer for shutdown output
        buf.truncate(0)
        buf.seek(0)
        
        yield {
            'startup_output': startup_output,
            'buffer': buf,
            'thread': server_thread
        }
        # Send CTRL+C signal instead of flag setting.
        os.kill(os.getpid(), signal.SIGINT)
        
        # Wait for server to shutdown
        time.sleep(2)
        server_thread.join(timeout=5)

def test_server_startup_and_shutdown(start_server):
    # Check startup messages
    assert "[STARTING] server is starting..." in start_server['startup_output'], \
        "Server should print the start message"
    assert "[LISTENING] Server is listening on" in start_server['startup_output'], \
        "Server should indicate it is listening"
    os.kill(os.getpid(), signal.SIGINT)
    time.sleep(2)
    
    # Get final output
    shutdown_output = start_server['buffer'].getvalue()
    
    # Check for shutdown messages
    assert "[INFO] Server is shutting down..." in shutdown_output or \
        "[INFO] Server shutdown complete" in shutdown_output, \
        "Server should print shutdown-related messages"
    