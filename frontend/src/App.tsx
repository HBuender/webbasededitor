import React from 'react';
import MonacoEditorComponent from './components/SimplePythonEditor';
import './App.css';

function App() {
  return (
    <div className="app-container" style={{ width: '100%', height: '100vh', margin: 0, padding: 0 }}>
      <MonacoEditorComponent />
    </div>
  );
}

export default App;
