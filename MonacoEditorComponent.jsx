import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const MonacoEditorComponent = () => {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');

  const handleEditorChange = (value) => {
    setCode(value);
  };

  const handleRunCode = async () => {
    try {
      const response = await axios.post('/api/run-code', { code });
      setOutput(response.data);
    } catch (error) {
      setOutput(`Error: ${error.response?.data || error.message}`);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{ flex: 1 }}>
        <Editor
          height="90%"
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
        <pre>{output}</pre>
      </div>
    </div>
  );
};

export default MonacoEditorComponent;
