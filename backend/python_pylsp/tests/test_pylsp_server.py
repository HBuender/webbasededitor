import os
import json
import socket
import time
import pytest
import subprocess
from pathlib import Path

# Constants
LSP_HOST = "localhost"
LSP_PORT = 3000
TIMEOUT = 10  # seconds
PROJECT_ROOT = Path(__file__).parent.parent

# Test data - valid Python file
VALID_PYTHON = """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers and return the result.

    Parameters
    ----------
    a : int
        First number
    b : int
        Second number

    Returns
    -------
    int
        Sum of a and b
    \"\"\"
    return a + b

result = add(1, 2)
"""

# Test data - file with formatting issues
UNFORMATTED_PYTHON = """
def messy_function( x:int,y:int) ->int:
    \"\"\"This function has formatting issues.\"\"\"
    z=  x+y
    return     z

result=messy_function(1,2)
"""

# Test data - file with type errors
INVALID_PYTHON = """
def greet(name: str) -> str:
    \"\"\"Greet a person by name.\"\"\"
    return f"Hello, {name}!"

result = greet(42)  # Type error: 42 is int, not str
"""


class JsonRpcClient:
    """Simple JSON-RPC client for TCP communication with LSP server"""
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.request_id = 0
        self.buffer = b""
        
    def connect(self, timeout=TIMEOUT):
        """Connect to the LSP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((self.host, self.port))
        
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            
    def send_request(self, method, params=None):
        """Send a JSON-RPC request to the LSP server"""
        if params is None:
            params = {}
            
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        request_json = json.dumps(request)
        content_length = len(request_json)
        message = f"Content-Length: {content_length}\r\n\r\n{request_json}"
        
        self.socket.sendall(message.encode())
        return self.request_id
        
    def receive_message(self, timeout=TIMEOUT):
        """Receive a JSON-RPC message from the LSP server"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for LSP response")
                
            # Check if we have a complete header
            header_end = self.buffer.find(b"\r\n\r\n")
            if header_end == -1:
                # Need more header data
                try:
                    data = self.socket.recv(1024)
                    if not data:  # Connection closed
                        raise ConnectionError("Connection closed by server")
                    self.buffer += data
                except socket.timeout:
                    raise TimeoutError("Timeout waiting for LSP response")
                continue
                
            # Parse the Content-Length header
            header = self.buffer[:header_end].decode('utf-8', errors='replace')
            content_length = None
            
            print(f"DEBUG: Received header: {repr(header)}")
            
            for line in header.split("\r\n"):
                if line.startswith("Content-Length: "):
                    try:
                        content_length = int(line.split(": ")[1])
                        break
                    except (ValueError, IndexError) as e:
                        print(f"ERROR parsing Content-Length: {e}, header: {repr(line)}")
                        
            if content_length is None:
                print(f"WARNING: No Content-Length header found, dumping buffer: {repr(self.buffer[:100])}")
                # Skip this malformed header and try again
                self.buffer = self.buffer[header_end + 4:]
                continue
                
            # Check if we have the full message
            body_start = header_end + 4  # 4 is the length of "\r\n\r\n"
            if len(self.buffer) < body_start + content_length:
                # Need more body data
                try:
                    data = self.socket.recv(1024)
                    if not data:  # Connection closed
                        raise ConnectionError("Connection closed by server")
                    self.buffer += data
                except socket.timeout:
                    print(f"WARNING: Timeout while reading message body, got {len(self.buffer) - body_start} of {content_length} bytes")
                    raise TimeoutError("Timeout waiting for LSP response body")
                continue
                
            # Extract the message body
            body = self.buffer[body_start:body_start + content_length].decode('utf-8', errors='replace')
            
            # Update buffer to remove processed message
            self.buffer = self.buffer[body_start + content_length:]
            
            # Parse and return the JSON-RPC message
            try:
                print(f"DEBUG: Received body: {body[:100]}...")
                return json.loads(body)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON: {e}, body: {repr(body)}")
                # Continue and try to get another message
                continue


@pytest.fixture(scope="module")
def pylsp_container():
    """Start the Python LSP container and yield, then tear it down after tests"""
    print("Starting Python LSP container...")
    
    # Change to the directory containing docker-compose.yml
    original_dir = os.getcwd()
    os.chdir(PROJECT_ROOT)
    
    try:
        # Start the container
        print("Running docker-compose up -d...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"stdout: {result.stdout.decode()}")
        print(f"stderr: {result.stderr.decode()}")
        
        # Debug - show container logs
        print("Container logs:")
        subprocess.run(
            ["docker-compose", "logs"],
            check=False  # Don't fail if logs command fails
        )
        
        # Wait for the container to be healthy
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                print(f"Checking container health (attempt {attempt+1}/{max_attempts})...")
                result = subprocess.run(
                    ["docker-compose", "ps", "-q", "pylsp"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                container_id = result.stdout.decode().strip()
                
                if container_id:
                    print(f"Container ID: {container_id}")
                    health = subprocess.run(
                        ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_id],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    health_status = health.stdout.decode().strip()
                    print(f"Health status: {health_status}")
                    
                    if health_status == "healthy":
                        print("Container is healthy!")
                        break
                        
                    # If health is failing, show the last health check log
                    health_log = subprocess.run(
                        ["docker", "inspect", "--format", "{{json .State.Health.Log}}", container_id],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    print(f"Health check log: {health_log.stdout.decode()}")
                    
            except subprocess.CalledProcessError as e:
                print(f"Error checking container: {e}")
                
            if attempt < max_attempts - 1:
                print(f"Waiting for container to be healthy (attempt {attempt+1}/{max_attempts})...")
                time.sleep(5)
            else:
                pytest.fail("Container failed to become healthy")
                
        # Wait a bit more to ensure the server is fully initialized
        time.sleep(3)
        
        yield
    finally:
        # Tear down the container
        print("Tearing down Python LSP container...")
        subprocess.run(
            ["docker-compose", "down", "-v"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Change back to the original directory
        os.chdir(original_dir)


def test_server_initialization(pylsp_container):
    """Test that the LSP server properly responds to an initialize request."""
    client = JsonRpcClient(LSP_HOST, LSP_PORT)
    
    try:
        client.connect()
        
        # Send initialize request
        request_id = client.send_request(
            "initialize", 
            {
                "processId": os.getpid(),
                "rootPath": None,
                "rootUri": "file:///app/workspace",
                "capabilities": {},
                "trace": "off",
                "workspaceFolders": None
            }
        )
        
        # Wait for response
        max_attempts = 5
        for attempt in range(max_attempts):
            response = client.receive_message()
            print(f"Received message (attempt {attempt+1}/{max_attempts}): {json.dumps(response, indent=2)[:200]}...")
            
            # Check if this is our expected response
            if "id" in response and response["id"] == request_id:
                print("Found matching initialize response!")
                break
                
            # If it's a notification, continue reading
            if "method" in response:
                print(f"Received notification: {response['method']}")
                if attempt == max_attempts - 1:
                    pytest.fail(f"Received too many notifications without getting an initialize response")
                continue
                
            # If it's some other response, that's unexpected
            pytest.fail(f"Received unexpected response: {response}")
        
        # Validate response
        assert "jsonrpc" in response, "Response missing jsonrpc field"
        assert "id" in response, f"Response missing id field: {response}"
        assert response["id"] == request_id, f"Expected id {request_id}, got {response.get('id')}"
        assert "result" in response, f"Response missing result field: {response}"
        assert "capabilities" in response["result"], f"Result missing capabilities: {response['result']}"
        
        # Verify essential capabilities
        capabilities = response["result"]["capabilities"]
        assert "textDocumentSync" in capabilities, "Missing textDocumentSync capability"
        assert "completionProvider" in capabilities, "Missing completionProvider capability"
        assert "hoverProvider" in capabilities, "Missing hoverProvider capability"
        assert "definitionProvider" in capabilities, "Missing definitionProvider capability"
        
        # Send initialized notification
        client.send_request("initialized", {})
        
    finally:
        client.close()


def test_hover_documentation(pylsp_container):
    """Test that the LSP server provides hover documentation."""
    client = JsonRpcClient(LSP_HOST, LSP_PORT)
    
    try:
        client.connect()
        
        # Initialize connection
        client.send_request(
            "initialize", 
            {
                "processId": os.getpid(),
                "rootPath": None,
                "rootUri": "file:///app/workspace",
                "capabilities": {},
                "trace": "off",
                "workspaceFolders": None
            }
        )
        client.receive_message()  # Consume initialize response
        client.send_request("initialized", {})
        
        # Send textDocument/didOpen with valid Python file
        uri = "file:///app/workspace/test.py"
        client.send_request(
            "textDocument/didOpen", 
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "python",
                    "version": 1,
                    "text": VALID_PYTHON
                }
            }
        )
        
        # Skip any diagnostic notifications that might come after didOpen
        try:
            while True:
                response = client.receive_message(timeout=2)
                if "method" in response and response["method"] == "textDocument/publishDiagnostics":
                    print("Skipping diagnostic notification")
                    continue
                else:
                    # Put the message back in the buffer (we'll need it later)
                    raw_message = json.dumps(response)
                    content_length = len(raw_message)
                    full_message = f"Content-Length: {content_length}\r\n\r\n{raw_message}"
                    client.buffer = full_message.encode() + client.buffer
                    break
        except TimeoutError:
            # No more notifications, that's fine
            pass
        
        # Request hover information for the 'add' function
        hover_request_id = client.send_request(
            "textDocument/hover",
            {
                "textDocument": {"uri": uri},
                "position": {"line": 1, "character": 6}  # Position on the 'add' function
            }
        )
        
        # Wait for hover response
        max_attempts = 5
        for attempt in range(max_attempts):
            response = client.receive_message()
            
            # Check if this is our expected response
            if "id" in response and response["id"] == hover_request_id:
                break
                
            # If it's a notification, continue reading
            if "method" in response:
                print(f"Skipping notification: {response['method']}")
                if attempt == max_attempts - 1:
                    pytest.fail(f"Received too many notifications without getting hover response")
                continue
        
        # Validate hover response
        assert "result" in response, f"Response missing result field: {response}"
        assert response["result"] is not None, "Hover result is None"
        
        # Check if the hover content contains the function docstring
        hover_content = response["result"].get("contents", {})
        
        # The hover content can be either a string, a list, or a MarkupContent object
        if isinstance(hover_content, dict):
            hover_text = hover_content.get("value", "")
        elif isinstance(hover_content, list):
            hover_text = "".join(str(item) for item in hover_content)
        else:
            hover_text = str(hover_content)
        
        assert "Add two numbers and return the result" in hover_text, f"Expected docstring not found in hover text: {hover_text}"
        
    finally:
        client.close()


def test_code_completion(pylsp_container):
    """Test that the LSP server provides code completions."""
    client = JsonRpcClient(LSP_HOST, LSP_PORT)
    
    try:
        client.connect()
        
        # Initialize connection
        client.send_request(
            "initialize", 
            {
                "processId": os.getpid(),
                "rootPath": None,
                "rootUri": "file:///app/workspace",
                "capabilities": {},
                "trace": "off",
                "workspaceFolders": None
            }
        )
        client.receive_message()  # Consume initialize response
        client.send_request("initialized", {})
        
        # Send textDocument/didOpen with valid Python file
        uri = "file:///app/workspace/test.py"
        client.send_request(
            "textDocument/didOpen", 
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "python",
                    "version": 1,
                    "text": "import os\n\nos."  # Setup for completion after 'os.'
                }
            }
        )
        
        # Skip any diagnostic notifications
        try:
            while True:
                response = client.receive_message(timeout=2)
                if "method" in response and response["method"] == "textDocument/publishDiagnostics":
                    print("Skipping diagnostic notification")
                    continue
                else:
                    # Put the message back in the buffer
                    raw_message = json.dumps(response)
                    content_length = len(raw_message)
                    full_message = f"Content-Length: {content_length}\r\n\r\n{raw_message}"
                    client.buffer = full_message.encode() + client.buffer
                    break
        except TimeoutError:
            # No more notifications, that's fine
            pass
        
        # Request completions after 'os.'
        completion_request_id = client.send_request(
            "textDocument/completion",
            {
                "textDocument": {"uri": uri},
                "position": {"line": 2, "character": 3},  # Position after 'os.'
                "context": {"triggerKind": 1}
            }
        )
        
        # Wait for completion response
        max_attempts = 5
        for attempt in range(max_attempts):
            response = client.receive_message()
            
            # Check if this is our expected response
            if "id" in response and response["id"] == completion_request_id:
                break
                
            # If it's a notification, continue reading
            if "method" in response:
                print(f"Skipping notification: {response['method']}")
                if attempt == max_attempts - 1:
                    pytest.fail(f"Received too many notifications without getting completion response")
                continue
        
        # Validate completion response
        assert "result" in response, f"Response missing result field: {response}"
        assert response["result"] is not None, "Completion result is None"
        
        # Check if the completion items contain common os module functions
        if isinstance(response["result"], dict):
            completion_items = response["result"].get("items", [])
        else:
            completion_items = response["result"]
        
        completion_labels = [item.get("label") for item in completion_items]
        
        # Check for common os functions that should be in completions
        common_os_functions = ["path", "getcwd", "listdir", "environ"]
        for func in common_os_functions:
            assert any(func in label for label in completion_labels), f"Expected os.{func} in completions, got: {completion_labels[:10]}"
        
    finally:
        client.close()


def test_diagnostics(pylsp_container):
    """Test that the LSP server provides diagnostics for errors."""
    client = JsonRpcClient(LSP_HOST, LSP_PORT)
    
    try:
        client.connect()
        
        # Initialize connection
        client.send_request(
            "initialize", 
            {
                "processId": os.getpid(),
                "rootPath": None,
                "rootUri": "file:///app/workspace",
                "capabilities": {},
                "trace": "off",
                "workspaceFolders": None
            }
        )
        client.receive_message()  # Consume initialize response
        client.send_request("initialized", {})
        
        # Send textDocument/didOpen with Python file containing errors
        uri = "file:///app/workspace/test_errors.py"
        client.send_request(
            "textDocument/didOpen", 
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "python",
                    "version": 1,
                    "text": "def func():\n    return undefined_variable\n"  # undefined variable error
                }
            }
        )
        
        # Wait for diagnostic notification
        received_diagnostics = False
        max_attempts = 10  # More attempts as diagnostics can be slow
        
        for attempt in range(max_attempts):
            try:
                response = client.receive_message(timeout=3)
                
                if "method" in response and response["method"] == "textDocument/publishDiagnostics":
                    diagnostics = response["params"]["diagnostics"]
                    print(f"Received diagnostics: {json.dumps(diagnostics)}")
                    
                    if diagnostics and len(diagnostics) > 0:
                        received_diagnostics = True
                        break
                else:
                    print(f"Skipping non-diagnostic message: {json.dumps(response)[:100]}...")
            except TimeoutError:
                if attempt < max_attempts - 1:
                    print(f"Timeout waiting for diagnostics (attempt {attempt+1}/{max_attempts})")
                    time.sleep(1)
        
        assert received_diagnostics, "Did not receive diagnostics for file with errors"
        
        # Check that at least one diagnostic relates to undefined variable
        assert any("undefined" in diag.get("message", "").lower() for diag in diagnostics), \
            f"Expected diagnostic about undefined variable, got: {diagnostics}"
        
    finally:
        client.close()


def test_document_symbols(pylsp_container):
    """Test that the LSP server provides document symbols."""
    client = JsonRpcClient(LSP_HOST, LSP_PORT)
    
    try:
        client.connect()
        
        # Initialize connection
        client.send_request(
            "initialize", 
            {
                "processId": os.getpid(),
                "rootPath": None,
                "rootUri": "file:///app/workspace",
                "capabilities": {},
                "trace": "off",
                "workspaceFolders": None
            }
        )
        client.receive_message()  # Consume initialize response
        client.send_request("initialized", {})
        
        # Send textDocument/didOpen with a Python file containing symbols
        uri = "file:///app/workspace/test_symbols.py"
        test_file = """
class TestClass:
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        return self.value
        
def test_function():
    return "test"
        
TEST_CONSTANT = 42
"""
        client.send_request(
            "textDocument/didOpen", 
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "python",
                    "version": 1,
                    "text": test_file
                }
            }
        )
        
        # Skip any diagnostic notifications
        try:
            while True:
                response = client.receive_message(timeout=2)
                if "method" in response and response["method"] == "textDocument/publishDiagnostics":
                    print("Skipping diagnostic notification")
                    continue
                else:
                    # Put the message back in the buffer
                    raw_message = json.dumps(response)
                    content_length = len(raw_message)
                    full_message = f"Content-Length: {content_length}\r\n\r\n{raw_message}"
                    client.buffer = full_message.encode() + client.buffer
                    break
        except TimeoutError:
            # No more notifications, that's fine
            pass
        
        # Request document symbols
        symbols_request_id = client.send_request(
            "textDocument/documentSymbol",
            {
                "textDocument": {"uri": uri}
            }
        )
        
        # Wait for symbols response
        max_attempts = 5
        for attempt in range(max_attempts):
            response = client.receive_message()
            
            # Check if this is our expected response
            if "id" in response and response["id"] == symbols_request_id:
                break
                
            # If it's a notification, continue reading
            if "method" in response:
                print(f"Skipping notification: {response['method']}")
                if attempt == max_attempts - 1:
                    pytest.fail(f"Received too many notifications without getting symbols response")
                continue
        
        # Validate symbols response
        assert "result" in response, f"Response missing result field: {response}"
        symbols = response["result"]
        assert symbols is not None, "Symbols result is None"
        assert len(symbols) > 0, "No symbols returned"
        
        # Check for expected symbols
        symbol_names = [symbol.get("name") for symbol in symbols]
        expected_symbols = ["TestClass", "__init__", "get_value", "test_function", "TEST_CONSTANT"]
        
        for expected in expected_symbols:
            assert any(expected in name for name in symbol_names), \
                f"Expected symbol '{expected}' not found in symbols: {symbol_names}"
        
    finally:
        client.close()


