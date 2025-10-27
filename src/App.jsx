import { Outlet } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <Outlet /> {/* Renderiza las rutas hijas */}
    </div>
  );
}

export default App;