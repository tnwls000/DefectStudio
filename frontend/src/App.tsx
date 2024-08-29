import { Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux'; 
import store from './store/store'; 
import Navbar from './components/common/Navbar';
import Home from './pages/Home';
import Generation from './pages/Generation';
import Training from './pages/Training';
import Model from './pages/Model';
import Settings from './pages/Settings';
import Docs from './pages/Docs';
import Login from './pages/Login';

function AppContent() {
  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/generation/*" element={<Generation />} />
        <Route path="/training" element={<Training />} />
        <Route path="/model" element={<Model />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/docs" element={<Docs />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

export default App;
