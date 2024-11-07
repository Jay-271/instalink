import socket
import threading
import time
import pytest
from io import StringIO
from contextlib import redirect_stdout
from Code import main

@pytest.fixture(scope="module")
def start_server():
    buf = StringIO()
    
    # Start server in a thread
    server_thread = threading.Thread(target=main.start, daemon=True)
    
    with redirect_stdout(buf):
        server_thread.start()
        time.sleep(1)  # Wait for server to start
        
        # Get initial output
        startup_output = buf.getvalue()
        
        # Clear buffer for shutdown output
        buf.truncate(0)
        buf.seek(0)
        
        yield {
            'startup_output': startup_output,
            'buffer': buf,
            'thread': server_thread
        }
        
        # Set shutdown flag directly instead of using SIGINT
        main.shutdown_flag.set()
        
        # Create a dummy connection to unblock accept()
        try:
            dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dummy.connect((main.server_ip, main.server_port))
            dummy.close()
        except:
            pass
        
        # Wait for server to shutdown
        time.sleep(2)
        server_thread.join(timeout=5)

def test_server_startup_and_shutdown(start_server):
    # Check startup messages
    assert "[STARTING] server is starting..." in start_server['startup_output'], \
        "Server should print the start message"
    assert "[LISTENING] Server is listening on" in start_server['startup_output'], \
        "Server should indicate it is listening"
    
    # Set shutdown flag directly
    main.shutdown_flag.set()
    
    # Create dummy connection to unblock accept()
    try:
        dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dummy.connect((main.server_ip, main.server_port))
        dummy.close()
    except:
        pass
    
    time.sleep(2)
    
    # Get final output
    shutdown_output = start_server['buffer'].getvalue()
    
    # Check for shutdown messages
    assert "[INFO] Server is shutting down..." in shutdown_output or \
        "[INFO] Server shutdown complete" in shutdown_output, \
        "Server should print shutdown-related messages"