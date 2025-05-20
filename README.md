# Web-based Editor

A web-based code editor with language intelligence support for multiple programming languages.

## Components

### Backend

#### Python Language Server (pylsp)

The project includes a Python Language Server (pylsp) that provides intelligent code features for Python files:

- **Code Completion**: Get suggestions as you type
- **Hover Documentation**: View documentation when hovering over Python symbols
- **Error Diagnostics**: See syntax and semantic errors in real-time
- **Code Formatting**: Automatic formatting using Black
- **Type Checking**: Static type analysis via mypy
- **Linting**: Code quality checking with Ruff
- **Import Sorting**: Automatic import organization with isort

The language server runs in a Docker container and communicates with the editor frontend via TCP on port 3000.

##### Features

- Built on python-lsp-server with additional plugins
- Configurable through pylsp_config.json
- TCP mode allows browser-based clients to connect
- Comprehensive test suite to verify functionality
- Monaco Editor integration-ready

##### Running the Python LSP Server

```bash
cd backend/python_pylsp
docker-compose up -d
```

#### WebSocket Proxy for LSP Integration

The project includes a WebSocket proxy that bridges the browser-based editor with the TCP-based Language Server:

- **Protocol Conversion**: Transforms WebSocket messages to TCP and back
- **Real-time Communication**: Enables real-time language features in the browser
- **Error Handling**: Robust handling of connection issues and reconnection

To run the WebSocket proxy:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
   
3. Start the WebSocket proxy:
   ```bash
```bash
node backend/ws-proxy.js
```

#### Other Backend Components

The backend includes a FastAPI server for code execution:

- **FastAPI Server**: Provides API endpoints for code execution
- **Docker Setup**: Dockerfile for setting up the backend environment

To run the FastAPI server:

1. Ensure Docker is installed and running on your system
2. Build the backend Docker image:
   ```bash
   docker build -t fastapi-python-runner ./backend/python_executor
   ```
3. Run the backend server:
   ```bash
   docker run -p 8000:8000 --rm -v //var/run/docker.sock:/var/run/docker.sock fastapi-python-runner
   ```
   Note: On Linux and Mac, use `-v /var/run/docker.sock:/var/run/docker.sock` instead

### Frontend

The frontend is a React application with Monaco Editor for code editing:

#### Monaco Editor with LSP Integration

The editor now features full Language Server Protocol integration:

- **Intelligent Code Completion**: Context-aware suggestions from the LSP server
- **Real-time Error Diagnostics**: Syntax and semantic errors shown as you type
- **Connection Status Indicator**: Visual feedback on LSP connection state
- **Automatic Reconnection**: Gracefully handles server disconnections

#### Running the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open http://localhost:5173 in your browser

## Architecture

The application follows a modern web architecture:

1. **Browser-based Editor**: React + Monaco Editor in the frontend
2. **WebSocket Communication**: Real-time connection to LSP services
3. **Language Server**: TCP-based Python LSP for intelligent features
4. **Code Execution**: Secure, containerized Python execution

## Development

To develop the project:

1. Start the Python Language Server:
   ```bash
   cd backend/python_pylsp
   docker-compose up -d
   ```

2. Run the WebSocket proxy:
   ```bash
   node backend/ws-proxy.js
   ```

3. Start the FastAPI backend:
   ```bash
   docker run -p 8000:8000 --rm -v //var/run/docker.sock:/var/run/docker.sock fastapi-python-runner
   ```

4. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

## Testing

The project includes comprehensive tests for each component:

- **Python LSP Server**: Tests for initialization, hover documentation, code completion, diagnostics, document symbols, and formatting

To run the Python LSP Server tests:

```bash
cd backend/python_pylsp
python -m pytest tests/test_pylsp_server.py -v
```

## Deployment

To deploy the application:

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```

2. Use Docker Compose to deploy all components:
   ```bash
   docker-compose up -d
   ```

## Example Python Scripts

Try these examples in the editor:

### Basic Hello World
```python
print("Hello, World!")
```

### Fibonacci Sequence
```python
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b

fibonacci(10)
```

### Simple Data Analysis
```python
import math

# Create some data
data = [12, 15, 23, 7, 42, 39, 5, 18]

# Analyze the data
average = sum(data) / len(data)
variance = sum((x - average) ** 2 for x in data) / len(data)
std_dev = math.sqrt(variance)

print(f"Data: {data}")
print(f"Count: {len(data)}")
print(f"Average: {average:.2f}")
print(f"Standard Deviation: {std_dev:.2f}")
print(f"Min: {min(data)}")
print(f"Max: {max(data)}")
```

## Features

- Python code editing with syntax highlighting and intelligent code features
- Language Server Protocol integration for advanced coding assistance
- WebSocket proxy for real-time language services
- Secure code execution in isolated Docker containers
- Real-time output display
- Error handling and execution time tracking
- Resource limits and timeouts for security

## Security Considerations

The backend runs user code in isolated Docker containers with:
- Memory limits (50MB)
- Network access disabled
- Execution timeouts (5 seconds)

## Troubleshooting

### LSP Connection Issues

If the editor shows "LSP: connecting" but doesn't connect:

1. Verify the Python LSP server is running on port 3000
2. Check that the WebSocket proxy is running on port 3001
3. Inspect browser console for WebSocket connection errors
4. Ensure your firewall allows WebSocket connections
