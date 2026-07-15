import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Dashboard } from './pages/Dashboard';
import { Customers } from './pages/Customers';
import { Predictor } from './pages/Predictor';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { api } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(api.auth.isAuthenticated());
  const [authView, setAuthView] = useState('login'); // 'login' or 'register'
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'customers', 'simulator'

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    api.auth.logout();
    setIsAuthenticated(false);
    setAuthView('login');
  };

  // Render Authentication screens if not logged in
  if (!isAuthenticated) {
    if (authView === 'register') {
      return (
        <Register 
          onRegisterSuccess={() => setAuthView('login')} 
          switchToLogin={() => setAuthView('login')} 
        />
      );
    }
    return (
      <Login 
        onLoginSuccess={handleLoginSuccess} 
        switchToRegister={() => setAuthView('register')} 
      />
    );
  }

  // Render Main Application with Sidebar
  return (
    <div className="flex bg-dark-bg min-h-screen">
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onLogout={handleLogout} 
      />
      
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'customers' && <Customers />}
        {activeTab === 'simulator' && <Predictor />}
      </main>
    </div>
  );
}

export default App;
