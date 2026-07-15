import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Brain, Sparkles, User, ShieldAlert, CheckCircle, XCircle, ArrowRight, Loader } from 'lucide-react';

export const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCust, setSelectedCust] = useState(null);
  const [custDetails, setCustDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [runningAction, setRunningAction] = useState(false);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const data = await api.customers.list();
      setCustomers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, []);

  const handleSelectCustomer = async (cust) => {
    setSelectedCust(cust);
    setCustDetails(null);
    try {
      const details = await api.customers.getDetails(cust.id);
      setCustDetails(details);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunDecisionEngine = async (cust) => {
    setRunningAction(true);
    try {
      await api.decisionEngine.recommend(cust.id);
      alert("Decision Intelligence completed. Next-best-action updated!");
      // Reload customer details
      if (selectedCust && selectedCust.id === cust.id) {
        const details = await api.customers.getDetails(cust.id);
        setCustDetails(details);
      }
      fetchCustomers();
    } catch (err) {
      alert("Failed: " + err.message);
    } finally {
      setRunningAction(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 min-h-screen flex flex-col items-center justify-center bg-dark-bg text-dark-text">
        <Loader size={36} className="animate-spin text-dark-accent mb-4" />
        <p className="text-sm text-dark-textMuted">Loading customer database...</p>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-dark-bg p-8 min-h-screen overflow-y-auto flex gap-8">
      {/* Customer List Section */}
      <div className={`transition-all duration-500 ${selectedCust ? 'w-2/3' : 'w-full'}`}>
        <header className="mb-6">
          <h2 className="text-2xl font-bold tracking-tight text-dark-text">Customer Retention Directory</h2>
          <p className="text-sm text-dark-textMuted mt-1">Review behavioral segments and run decision logs</p>
        </header>

        <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden shadow-lg">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-dark-bg border-b border-dark-border text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                <th className="px-6 py-4">Customer ID</th>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Spending</th>
                <th className="px-6 py-4">Churn Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border/50 text-sm text-dark-text">
              {customers.map((c) => {
                const isSelected = selectedCust?.id === c.id;
                return (
                  <tr 
                    key={c.id} 
                    className={`transition-colors duration-300 hover:bg-dark-border/20 cursor-pointer ${isSelected ? 'bg-dark-border/30' : ''}`}
                    onClick={() => handleSelectCustomer(c)}
                  >
                    <td className="px-6 py-4 font-mono font-semibold text-dark-accent">{c.id}</td>
                    <td className="px-6 py-4 font-medium">{c.name}</td>
                    <td className="px-6 py-4 text-dark-textMuted">{c.product_category || 'N/A'}</td>
                    <td className="px-6 py-4 font-semibold">${parseFloat(c.total_spending).toFixed(2)}</td>
                    <td className="px-6 py-4">
                      {c.churn === 1 ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-danger/10 text-danger border border-danger/20">
                          <ShieldAlert size={12} />
                          <span>At Risk</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-success/10 text-success border border-success/20">
                          <CheckCircle size={12} />
                          <span>Loyal</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => handleRunDecisionEngine(c)}
                        disabled={runningAction}
                        className="p-2 bg-dark-bg border border-dark-border rounded-lg text-dark-accent hover:bg-dark-accent hover:text-white transition-all duration-300 shadow-sm"
                        title="Run Decision Engine"
                      >
                        <Brain size={16} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Customer Detail Drawer Section */}
      {selectedCust && (
        <div className="w-1/3 bg-dark-card border border-dark-border rounded-2xl p-6 shadow-xl h-fit sticky top-8 animate-in slide-in-from-right duration-300">
          <div className="flex items-center justify-between pb-4 border-b border-dark-border mb-6">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 bg-dark-bg border border-dark-border rounded-lg text-dark-accent">
                <User size={18} />
              </div>
              <div>
                <h3 className="font-bold text-dark-text text-base">{selectedCust.name}</h3>
                <span className="text-xs text-dark-textMuted font-mono">{selectedCust.id}</span>
              </div>
            </div>
            <button 
              onClick={() => setSelectedCust(null)}
              className="text-dark-textMuted hover:text-dark-text text-sm font-semibold transition-colors duration-300"
            >
              Close
            </button>
          </div>

          {custDetails ? (
            <div className="space-y-6">
              {/* Demographics */}
              <div className="grid grid-cols-2 gap-4 bg-dark-bg p-4 rounded-xl border border-dark-border/40 text-xs">
                <div>
                  <p className="text-dark-textMuted font-medium">Gender / Age</p>
                  <p className="font-semibold text-dark-text mt-0.5">{custDetails.customer.gender || 'N/A'}, {custDetails.customer.age || 'N/A'} yrs</p>
                </div>
                <div>
                  <p className="text-dark-textMuted font-medium">Tenure (months)</p>
                  <p className="font-semibold text-dark-text mt-0.5">{custDetails.customer.tenure} months</p>
                </div>
                <div>
                  <p className="text-dark-textMuted font-medium">Satisfaction Score</p>
                  <p className="font-semibold text-dark-text mt-0.5">{custDetails.customer.satisfaction_score} / 5</p>
                </div>
                <div>
                  <p className="text-dark-textMuted font-medium">Cashback Amount</p>
                  <p className="font-semibold text-dark-text mt-0.5">${parseFloat(custDetails.customer.cashback_amount).toFixed(2)}</p>
                </div>
              </div>

              {/* Latest Recommendation plan */}
              <div>
                <h4 className="text-xs font-bold text-dark-textMuted uppercase tracking-wider mb-2">Next-Best-Action</h4>
                {custDetails.recommendations.length > 0 ? (
                  <div className="bg-dark-accent/10 border border-dark-accent/20 rounded-xl p-4 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-2 text-dark-accent/30">
                      <Sparkles size={24} />
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-dark-accent/20 text-dark-text capitalize">
                        {custDetails.recommendations[0].action_type}
                      </span>
                      <span className={`text-xs font-bold ${
                        custDetails.recommendations[0].priority === 'High' ? 'text-danger' : 
                        custDetails.recommendations[0].priority === 'Medium' ? 'text-warning' : 'text-success'
                      }`}>
                        {custDetails.recommendations[0].priority} Priority
                      </span>
                    </div>
                    <p className="text-xs text-dark-text leading-relaxed">
                      {custDetails.recommendations[0].recommendation_text}
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-4 bg-dark-bg/50 border border-dashed border-dark-border rounded-xl">
                    <p className="text-xs text-dark-textMuted mb-3">No recommendation generated yet</p>
                    <button
                      onClick={() => handleRunDecisionEngine(selectedCust)}
                      disabled={runningAction}
                      className="inline-flex items-center space-x-2 text-xs bg-dark-accent hover:bg-dark-accentHover text-white px-3 py-1.5 rounded-lg shadow-glow transition-all duration-300"
                    >
                      <Brain size={12} />
                      <span>Run Decision Engine</span>
                    </button>
                  </div>
                )}
              </div>

              {/* Predictions Log */}
              <div>
                <h4 className="text-xs font-bold text-dark-textMuted uppercase tracking-wider mb-2">Model Prediction History</h4>
                {custDetails.predictions.length > 0 ? (
                  <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                    {custDetails.predictions.slice(0, 3).map((p, idx) => (
                      <div key={idx} className="flex justify-between items-center text-xs p-2 bg-dark-bg/60 border border-dark-border/40 rounded-lg">
                        <span className="capitalize font-semibold text-dark-textMuted">{p.model_type} Model</span>
                        <span className="font-mono text-dark-text">{p.result_value}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-dark-textMuted italic">No predictions run on models yet.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader size={20} className="animate-spin text-dark-accent mb-2" />
              <p className="text-xs text-dark-textMuted">Loading profile data...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Customers;
