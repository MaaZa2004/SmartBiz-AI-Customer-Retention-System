import React from 'react';
import { LayoutDashboard, Users, Brain, LogOut, FileText } from 'lucide-react';
import { api } from '../services/api';

export const Sidebar = ({ activeTab, setActiveTab, onLogout }) => {
  const role = api.auth.getRole();

  const menuItems = [
    { id: 'dashboard', label: 'Analytics Dashboard', icon: LayoutDashboard },
    { id: 'customers', label: 'Customers Database', icon: Users },
    { id: 'simulator', label: 'Churn Simulator', icon: Brain },
  ];

  return (
    <aside className="w-64 bg-dark-card border-r border-dark-border flex flex-col justify-between h-screen sticky top-0">
      <div className="p-6">
        {/* Brand Logo matching the user's styling */}
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-dark-accent flex items-center justify-center font-bold text-white shadow-glow">
            S
          </div>
          <div>
            <h1 className="text-lg font-bold text-dark-text tracking-wider">SHOPWISE</h1>
            <span className="text-[10px] uppercase font-semibold text-dark-accent tracking-widest block -mt-1">
              SmartBiz AI
            </span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="mt-10 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-300 ${
                  isActive
                    ? 'bg-dark-accent text-white shadow-glow'
                    : 'text-dark-textMuted hover:bg-dark-border hover:text-dark-text'
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* User Information & Logout */}
      <div className="p-6 border-t border-dark-border">
        <div className="mb-4">
          <p className="text-xs text-dark-textMuted font-medium uppercase tracking-wider">Role Access</p>
          <p className="text-sm font-semibold text-dark-accent capitalize mt-0.5">{role || 'User'}</p>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium text-danger hover:bg-red-500/10 transition-all duration-300 border border-transparent hover:border-danger/20"
        >
          <LogOut size={18} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
