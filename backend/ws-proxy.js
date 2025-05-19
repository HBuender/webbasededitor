const WebSocket = require('ws');
const net = require('net');

// Configuration
const WS_PORT = 3001;
const LSP_HOST = 'localhost';
const LSP_PORT = 3000;
const PATH = '/python-lsp';

// Create WebSocket server
const wss = new WebSocket.Server({ port: WS_PORT, path: PATH });
console.log(`WebSocket Proxy Server started on port ${WS_PORT}`);
console.log(`Forwarding to LSP server at ${LSP_HOST}:${LSP_PORT}`);

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Connect to the LSP server
  const socket = net.connect(LSP_PORT, LSP_HOST);
  
  // Handle WebSocket messages (client to LSP server)
  ws.on('message', (message) => {
    if (socket.writable) {
      const data = message.toString();
      try {
        // Parse the message to handle JSON-RPC correctly
        const jsonRpcMessage = JSON.parse(data);
        const contentLength = data.length;
        
        // Format as LSP message with content length header
        const lspMessage = `Content-Length: ${contentLength}\r\n\r\n${data}`;
        socket.write(lspMessage);
      } catch (err) {
        console.error('Error processing message:', err);
        socket.write(data);
      }
    }
  });
  
  // LSP server to WebSocket client
  let buffer = Buffer.alloc(0);
  
  socket.on('data', (data) => {
    buffer = Buffer.concat([buffer, data]);
    
    // Parse the buffer for complete LSP messages
    let processed = 0;
    while (processed < buffer.length) {
      // Find the header separator
      const headerEnd = buffer.indexOf(Buffer.from('\r\n\r\n'), processed);
      if (headerEnd === -1) break;
      
      // Parse the content length
      const header = buffer.slice(processed, headerEnd).toString();
      const match = /Content-Length: (\d+)/.exec(header);
      if (!match) {
        processed = headerEnd + 4;
        continue;
      }
      
      const contentLength = parseInt(match[1], 10);
      const messageStart = headerEnd + 4;
      const messageEnd = messageStart + contentLength;
      
      // Check if we have the full message
      if (buffer.length < messageEnd) break;
      
      // Extract and forward the JSON content
      const jsonContent = buffer.slice(messageStart, messageEnd).toString();
      try {
        ws.send(jsonContent);
      } catch (e) {
        console.error('Error sending message to WebSocket client:', e);
      }
      
      processed = messageEnd;
    }
    
    // Remove processed data from buffer
    if (processed > 0) {
      buffer = buffer.slice(processed);
    }
  });
  
  // Handle connection errors and cleanup
  socket.on('close', () => {
    console.log('LSP server connection closed');
    ws.close();
  });
  
  socket.on('error', (err) => {
    console.error('LSP server socket error:', err);
    ws.close();
  });
  
  ws.on('close', () => {
    console.log('WebSocket client disconnected');
    socket.end();
  });
  
  ws.on('error', (err) => {
    console.error('WebSocket error:', err);
    socket.end();
  });
});

// Add process termination handlers
process.on('SIGINT', () => {
  wss.close(() => {
    console.log('WebSocket server closed');
    process.exit(0);
  });
});