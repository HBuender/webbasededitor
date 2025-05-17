import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const MonacoEditorComponent: React.FC = () => {
  const [code, setCode] = useState('# Write your Python code here');
  const [output, setOutput] = useState<{ output?: string; errors?: string; execution_time?: number } | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const handleEditorChange = (value: string | undefined) => {
    setCode(value || '');
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    try {
      const response = await axios.post('/api/run-code', { code });
      setOutput(response.data);
    } catch (error: any) {
      setOutput({ output: '', errors: error.response?.data?.detail || error.message });
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div 
      style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        height: '100vh', 
        width: '100vw', // Use viewport width
        maxWidth: '100%', // Ensure it doesn't overflow
        margin: 0, 
        padding: 0,
        overflow: 'hidden' // Prevent scrollbars on the container
      }}
      role="application"
      aria-label="Python code editor environment"
    >
      <header 
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#1e1e1e', 
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Web-Based Python Editor</h1>
        <button 
          onClick={handleRunCode} 
          disabled={isRunning}
          style={{ 
            padding: '8px 16px',
            backgroundColor: '#0078d4',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            fontSize: '1rem',
            cursor: isRunning ? 'wait' : 'pointer'
          }}
          aria-busy={isRunning}
          aria-label="Run Python code"
        >
          {isRunning ? 'Running...' : 'Run'}
        </button>
      </header>

      <main style={{ 
        flex: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        width: '100%',
        overflow: 'hidden' // Prevent scrollbars on the main element
      }}>
        <div 
          style={{ 
            flex: 3, 
            width: '100%', 
            minHeight: '200px',
            position: 'relative' // Add this for better Monaco editor rendering
          }}
          aria-label="Code editor"
          role="region"
        >
          <Editor
            height="100%"
            width="100%"
            defaultLanguage="python"
            value={code}
            onChange={handleEditorChange}
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: true },
              lineNumbers: "on",
              folding: true,
              wordWrap: "on",
              automaticLayout: true,
              tabSize: 4,
              scrollBeyondLastLine: false,
              accessibilitySupport: "auto"
            }}
            aria-label="Python code editor"
          />
        </div>

        <div 
          style={{ 
            flex: 2, 
            backgroundColor: '#f5f5f5', 
            padding: '15px 20px', 
            overflow: 'auto',
            borderTop: '3px solid #ddd',
            width: '100%',
            color: '#333'
          }}
          aria-live="polite"
          aria-label="Code execution output"
          role="region"
        >
          <h2 style={{ margin: '0 0 10px 0', fontSize: '1.2rem' }}>Output</h2>
          {output && (
            <div aria-label={output.errors ? "Execution results with errors" : "Execution results"}>
              {output.output && (
                <div>
                  <h3 style={{ margin: '10px 0 5px 0', fontSize: '1rem' }}>Standard Output:</h3>
                  <pre 
                    style={{ 
                      margin: '0', 
                      padding: '10px', 
                      backgroundColor: '#fff', 
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      overflow: 'auto',
                      maxWidth: '100%'
                    }}
                  >{output.output}</pre>
                </div>
              )}
              
              {output.errors && (
                <div>
                  <h3 style={{ margin: '15px 0 5px 0', fontSize: '1rem', color: '#d32f2f' }}>Errors:</h3>
                  <pre 
                    style={{ 
                      margin: '0', 
                      padding: '10px', 
                      backgroundColor: '#fff', 
                      border: '1px solid #ffcdd2',
                      borderRadius: '4px',
                      color: '#d32f2f',
                      overflow: 'auto',
                      maxWidth: '100%'
                    }}
                  >{output.errors}</pre>
                </div>
              )}
              
              {output.execution_time !== undefined && (
                <div 
                  style={{ marginTop: '10px', fontSize: '0.9rem', color: '#666' }}
                  aria-label={`Execution completed in ${output.execution_time} seconds`}
                >
                  <strong>Execution Time:</strong> {output.execution_time}s
                </div>
              )}
            </div>
          )}
          
          {!output && (
            <p style={{ color: '#666', fontStyle: 'italic' }}>
              Click the Run button to execute your code and see the output here.
            </p>
          )}
        </div>
      </main>
    </div>
  );
};

export default MonacoEditorComponent;