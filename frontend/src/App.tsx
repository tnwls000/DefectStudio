import { Routes, Route } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Home from './pages/Home';
import Generation from './pages/Generation';
import Training from './pages/Training';
import Model from './pages/Model';
import Settings from './pages/Settings';
import Docs from './pages/Docs';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/generation/*" element={<Generation />} />
        <Route path="/training" element={<Training />} />
        <Route path="/model" element={<Model />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/docs" element={<Docs />} />
      </Routes>
    </>
  );
}

export default App;
