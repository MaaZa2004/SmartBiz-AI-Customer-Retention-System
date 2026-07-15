import React, { useState } from 'react';
import { api } from '../services/api';
import { Mail, Lock, Loader } from 'lucide-react';

export const Login = ({ onLoginSuccess, switchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.auth.login(email, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || 'Incorrect email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background glow effects for premium styling */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-dark-accent/10 rounded-full blur-[100px]" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[100px]" />

      <div className="w-full max-w-md bg-dark-card border border-dark-border rounded-2xl p-8 relative z-10 shadow-xl hover:border-dark-accent/30 transition-all duration-500">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-dark-accent flex items-center justify-center font-bold text-xl text-white shadow-glow mx-auto mb-4">
            S
          </div>
          <h2 className="text-2xl font-bold text-dark-text tracking-wide">Welcome Back</h2>
          <p className="text-sm text-dark-textMuted mt-2">Sign in to Shopwise SmartBiz AI Dashboard</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-danger/10 border border-danger/25 text-danger text-sm rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-dark-textMuted">
                <Mail size={16} />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@shopwise.com"
                className="w-full bg-dark-bg border border-dark-border rounded-lg py-2.5 pl-10 pr-4 text-sm text-dark-text placeholder-dark-textMuted/50 focus:outline-none focus:border-dark-accent focus:ring-1 focus:ring-dark-accent transition-all duration-300"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-dark-textMuted">
                <Lock size={16} />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-dark-bg border border-dark-border rounded-lg py-2.5 pl-10 pr-4 text-sm text-dark-text placeholder-dark-textMuted/50 focus:outline-none focus:border-dark-accent focus:ring-1 focus:ring-dark-accent transition-all duration-300"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-dark-accent text-white py-3 rounded-lg font-semibold text-sm transition-all duration-300 hover:bg-dark-accentHover focus:outline-none flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-glow"
          >
            {loading ? (
              <Loader size={18} className="animate-spin" />
            ) : (
              <span>Sign In</span>
            )}
          </button>
        </form>

        <div className="text-center mt-6">
          <p className="text-sm text-dark-textMuted">
            Don't have an account?{' '}
            <button
              onClick={switchToRegister}
              className="text-dark-accent font-semibold hover:underline"
            >
              Sign Up
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
