import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const MonacoEditorComponent: React.FC = () => {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState<{ output?: string; errors?: string; execution_time?: number } | null>(null);

  const handleEditorChange = (value: string | undefined) => {
    setCode(value || '');
  };

  const handleRunCode = async () => {
    try {
      const response = await axios.post('/api/run-code', { code });
      setOutput(response.data);
    } catch (error: any) {
      setOutput({ output: '', errors: error.response?.data?.detail || error.message });
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', margin: 0 }}>
      <div style={{ flex: 1 }}>
        <Editor
          height="100%"
          width="100%"
          defaultLanguage="python"
          defaultValue="# Write your Python code here"
          onChange={handleEditorChange}
          theme="vs-dark"
        />
      </div>
      <button onClick={handleRunCode} style={{ margin: '10px', padding: '10px' }}>
        Run
      </button>
      <div style={{ flex: 1, backgroundColor: '#f4f4f4', padding: '10px', overflow: 'auto' }}>
        {output && (
          <div>
            <strong>Output:</strong>
            <pre>{output.output}</pre>
            {output.errors && (
              <>
                <strong>Errors:</strong>
                <pre style={{ color: 'red' }}>{output.errors}</pre>
              </>
            )}
            {output.execution_time !== undefined && (
              <div>
                <strong>Execution Time:</strong> {output.execution_time}s
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MonacoEditorComponent;