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

#### Other Backend Components

The backend includes a FastAPI server for code execution:

- **FastAPI Server**: Provides API endpoints for code execution
- **Docker Setup**: Dockerfile for setting up the backend environment

To run the FastAPI server:

1. Ensure Docker is installed and running on your system
2. Build the backend Docker image:
   ```bash
   docker build -t fastapi-python-runner ./backend
   ```
3. Run the backend server:
   ```bash
   docker run -p 8000:8000 --rm -v //var/run/docker.sock:/var/run/docker.sock fastapi-python-runner
   ```
   Note: On Linux, use `-v /var/run/docker.sock:/var/run/docker.sock` instead

### Frontend

The frontend is a React application with Monaco Editor for code editing:

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

## Development

To develop the project, follow the instructions for running the backend and frontend components.

## Testing

The project includes comprehensive tests for each component:

- **Python LSP Server**: Tests for initialization, hover documentation, code completion, diagnostics, document symbols, and formatting

To run the Python LSP Server tests:

```bash
cd backend/python_pylsp
python -m pytest tests/test_pylsp_server.py -v
```

## Deployment

To deploy the application, follow the instructions for running the backend and frontend components.

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

- Python code editing with syntax highlighting
- Secure code execution in isolated Docker containers
- Real-time output display
- Error handling and execution time tracking
- Resource limits and timeouts for security

## Security Considerations

The backend runs user code in isolated Docker containers with:
- Memory limits (50MB)
- Network access disabled
- Execution timeouts (5 seconds)
