# Web-Based Python Editor

A web-based Python code editor with real-time execution capabilities. This project consists of a React frontend with Monaco Editor for code editing and a FastAPI backend that securely executes Python code in Docker containers.

## Project Structure

```
webbasededitor/
├── backend/        # FastAPI server for code execution
│   ├── main.py     # API endpoint implementation
│   └── Dockerfile  # Docker setup for backend
├── frontend/       # React frontend application
│   ├── src/        # React source code
│   └── ...         # Frontend configuration files
└── README.md       # This file
```

## Running the Application

### Backend

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
