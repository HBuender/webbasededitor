import MonacoEditorComponent from './components/Editor';

function App() {
  return (
    <div className="App">
      <header style={{ padding: '10px', backgroundColor: '#282c34', color: 'white' }}>
        <h1>Web-Based Editor</h1>
      </header>
      <main style={{ flex: 1 }}>
        <MonacoEditorComponent />
      </main>
    </div>
  );
}

export default App;
