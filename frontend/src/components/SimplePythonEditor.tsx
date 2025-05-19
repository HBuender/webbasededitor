import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

// Simple implementation of an LSP connection
interface SimpleLSPConnection {
  isConnected: boolean;
  send: (message: any) => void;
  close: () => void;
}

const SimplePythonEditor: React.FC = () => {
  const [code, setCode] = useState('# Write your Python code here\nprint("Hello, World!")');
  const [output, setOutput] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [lspStatus, setLspStatus] = useState<'connected' | 'connecting' | 'disconnected'>('disconnected');
  
  const editorRef = useRef<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const completionProviderId = useRef<string | null>(null);
  
  // Connect to the LSP server
  const connectToLSP = () => {
    try {
      setLspStatus('connecting');
      console.log('Connecting to LSP server...');
      
      // Create WebSocket connection to the LSP proxy
      // This proxy should forward messages to your TCP LSP server on localhost:3000
      const ws = new WebSocket(`ws://${window.location.hostname}:3001/python-lsp`);
      wsRef.current = ws;
      
      ws.onopen = () => {
        console.log('Connected to LSP server');
        setLspStatus('connected');
        
        // Send initialize request
        const initializeRequest = {
          jsonrpc: '2.0',
          id: 1,
          method: 'initialize',
          params: {
            processId: null,
            rootUri: null,
            capabilities: {
              textDocument: {
                completion: {
                  dynamicRegistration: true,
                  completionItem: {
                    snippetSupport: true
                  }
                }
              }
            }
          }
        };
        ws.send(JSON.stringify(initializeRequest));
      };
      
      ws.onmessage = (event) => {
        console.log('Received from LSP server:', event.data);
        try {
          const message = JSON.parse(event.data);
          
          // Handle initialization response
          if (message.id === 1 && message.result) {
            console.log('LSP server initialized');
            
            // Send the initialized notification
            ws.send(JSON.stringify({
              jsonrpc: '2.0',
              method: 'initialized',
              params: {}
            }));
            
            // Notify LSP about the document
            ws.send(JSON.stringify({
              jsonrpc: '2.0',
              method: 'textDocument/didOpen',
              params: {
                textDocument: {
                  uri: 'file:///workspace/document.py',
                  languageId: 'python',
                  version: 1,
                  text: code
                }
              }
            }));
          }
        } catch (error) {
          console.error('Error parsing LSP message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('LSP connection error:', error);
        setLspStatus('disconnected');
      };
      
      ws.onclose = () => {
        console.log('LSP connection closed');
        setLspStatus('disconnected');
        
        // Try to reconnect after 5 seconds
        setTimeout(connectToLSP, 5000);
      };
      
      return {
        isConnected: true,
        send: (message: any) => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(message));
          }
        },
        close: () => ws.close()
      };
      
    } catch (error) {
      console.error('Error connecting to LSP server:', error);
      setLspStatus('disconnected');
      return null;
    }
  };
  
  // Set up editor on mount
  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Register completion provider
    if (completionProviderId.current === null) {
      completionProviderId.current = monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: async (model: any, position: any) => {
          if (wsRef.current?.readyState !== WebSocket.OPEN) {
            return { suggestions: [] };
          }
          
          return new Promise((resolve) => {
            const requestId = Date.now();
            
            // Send completion request to LSP
            wsRef.current?.send(JSON.stringify({
              jsonrpc: '2.0',
              id: requestId,
              method: 'textDocument/completion',
              params: {
                textDocument: { uri: 'file:///workspace/document.py' },
                position: {
                  line: position.lineNumber - 1,
                  character: position.column - 1
                }
              }
            }));
            
            // Handler for completion response
            const messageHandler = (event: MessageEvent) => {
              try {
                const response = JSON.parse(event.data);
                
                if (response.id === requestId) {
                  wsRef.current?.removeEventListener('message', messageHandler);
                  
                  if (response.result) {
                    const items = Array.isArray(response.result) 
                      ? response.result 
                      : (response.result.items || []);
                    
                    const suggestions = items.map((item: any) => ({
                      label: item.label,
                      kind: item.kind || monaco.languages.CompletionItemKind.Text,
                      insertText: item.insertText || item.label,
                      documentation: item.documentation?.value || item.documentation || '',
                      range: {
                        startLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endLineNumber: position.lineNumber,
                        endColumn: position.column
                      }
                    }));
                    
                    resolve({ suggestions });
                  } else {
                    resolve({ suggestions: [] });
                  }
                }
              } catch (error) {
                console.error('Error handling completion response:', error);
                resolve({ suggestions: [] });
              }
            };
            
            wsRef.current?.addEventListener('message', messageHandler);
            
            // Timeout to avoid hanging
            setTimeout(() => {
              wsRef.current?.removeEventListener('message', messageHandler);
              resolve({ suggestions: [] });
            }, 3000);
          });
        }
      });
    }
    
    // Connect to LSP
    connectToLSP();
  };
  
  // Update LSP when code changes
  const handleEditorChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        jsonrpc: '2.0',
        method: 'textDocument/didChange',
        params: {
          textDocument: {
            uri: 'file:///workspace/document.py',
            version: 2
          },
          contentChanges: [{ text: newCode }]
        }
      }));
    }
  };
  
  // Run the Python code
  const runCode = async () => {
    setIsRunning(true);
    try {
      const response = await axios.post('/api/run-code', { code });
      if (typeof response.data === 'string') {
        setOutput(response.data);
      } else if (response.data.output) {
        setOutput(response.data.output);
      } else if (response.data.errors) {
        setOutput(`Error: ${response.data.errors}`);
      } else {
        setOutput(JSON.stringify(response.data, null, 2));
      }
    } catch (error: any) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };
  
  // Clean up on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);
  
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#1e1e1e', 
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <h1 style={{ margin: 0 }}>Simple Python Editor</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center',
            fontSize: '14px'
          }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              marginRight: '6px',
              backgroundColor: lspStatus === 'connected' ? '#4caf50' : 
                              lspStatus === 'connecting' ? '#ff9800' : '#f44336'
            }}></div>
            <span>LSP: {lspStatus}</span>
          </div>
          <button 
            onClick={runCode}
            disabled={isRunning}
            style={{
              backgroundColor: '#0078d4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: isRunning ? 'wait' : 'pointer'
            }}
          >
            {isRunning ? 'Running...' : 'Run Code'}
          </button>
        </div>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <div style={{ height: '60%', borderBottom: '4px solid #333' }}>
          <Editor
            defaultLanguage="python"
            value={code}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: true },
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 4
            }}
          />
        </div>
        
        <div style={{ 
          height: '40%', 
          backgroundColor: '#1e1e1e',
          color: '#ddd',
          padding: '10px',
          overflow: 'auto'
        }}>
          <h2 style={{ margin: '0 0 10px 0', color: '#eee' }}>Output</h2>
          <pre style={{ 
            margin: 0, 
            whiteSpace: 'pre-wrap',
            fontFamily: 'monospace'
          }}>
            {output || 'Run your code to see output here'}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default SimplePythonEditor;