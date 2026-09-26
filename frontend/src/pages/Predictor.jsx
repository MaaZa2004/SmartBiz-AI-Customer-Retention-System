import React, { useState } from 'react';
import { api } from '../services/api';
import { Brain, HelpCircle, ShieldAlert, Sparkles, Loader } from 'lucide-react';

export const Predictor = () => {
  // Simulator inputs matching the user screenshot
  const [tenure, setTenure] = useState(12);
  const [distance, setDistance] = useState(10);
  const [maritalStatus, setMaritalStatus] = useState('Single');
  const [addresses, setAddresses] = useState(1);
  const [category, setCategory] = useState('Laptop & Accessory');
  const [devices, setDevices] = useState(1);
  const [satisfaction, setSatisfaction] = useState(3);
  const [daysSinceOrder, setDaysSinceOrder] = useState(7);
  const [cashback, setCashback] = useState(50.00);
  const [complain, setComplain] = useState('No');

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Counter helpers
  const adjustCounter = (val, setter, min, max, delta) => {
    setter(prev => {
      const next = parseFloat((prev + delta).toFixed(2));
      if (next < min) return min;
      if (next > max) return max;
      return next;
    });
  };

  const handlePredict = async () => {
    setLoading(true);
    setResults(null);
    setError(null);
    try {
      const res = await api.predict.simulate({
        tenure: parseInt(tenure),
        warehouse_to_home: parseInt(distance),
        num_devices_registered: parseInt(devices),
        product_category: category,
        satisfaction_score: parseInt(satisfaction),
        marital_status: maritalStatus,
        num_addresses: parseInt(addresses),
        complain: complain === 'Yes' ? 1 : 0,
        days_since_last_order: parseInt(daysSinceOrder),
        cashback_amount: parseFloat(cashback),
      });

      setResults({
        churn: {
          churn_probability: res.churn_probability,
          risk_level: res.risk_level,
        },
        segment: {
          segment: res.segment,
          details: res.segment_details,
        },
        recommendation: {
          recommendation_text: res.recommendation_text,
          action_type: res.action_type,
          priority: res.priority,
        },
      });
    } catch (err) {
      setError(err.message || "Simulation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 bg-dark-bg p-8 min-h-screen overflow-y-auto">
      <header className="mb-8">
        <h2 className="text-2xl font-bold tracking-tight text-dark-text">Customer Churn Simulator</h2>
        <p className="text-sm text-dark-textMuted mt-1">Configure client behavior attributes and run risk models in real-time</p>
      </header>

      {error && (
        <div className="mb-6 bg-danger/10 border border-danger/30 text-danger rounded-xl p-4 flex items-start space-x-3">
          <ShieldAlert size={20} className="shrink-0 mt-0.5" />
          <div className="text-sm">
            <span className="font-semibold">Simulation Error: </span>
            <span>{error}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input Parameters panel */}
        <div className="lg:col-span-2 bg-dark-card border border-dark-border rounded-2xl p-6 space-y-6">
          <h3 className="text-lg font-bold text-dark-text flex items-center space-x-2 pb-3 border-b border-dark-border">
            <span>Customer Attributes</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tenure slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-dark-text">
                <span>Tenure (Months)</span>
                <span className="text-dark-accent font-bold">{tenure}</span>
              </div>
              <input
                type="range"
                min="0"
                max="60"
                value={tenure}
                onChange={(e) => setTenure(e.target.value)}
                className="w-full h-1 bg-dark-border rounded-lg appearance-none cursor-pointer accent-dark-accent"
              />
              <div className="flex justify-between text-[10px] text-dark-textMuted font-bold">
                <span>0</span>
                <span>60</span>
              </div>
            </div>

            {/* Warehouse to Home Distance */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-dark-text">
                <span>Warehouse to Home Distance (km)</span>
                <span className="text-dark-accent font-bold">{distance}</span>
              </div>
              <input
                type="range"
                min="1"
                max="50"
                value={distance}
                onChange={(e) => setDistance(e.target.value)}
                className="w-full h-1 bg-dark-border rounded-lg appearance-none cursor-pointer accent-dark-accent"
              />
              <div className="flex justify-between text-[10px] text-dark-textMuted font-bold">
                <span>1</span>
                <span>50</span>
              </div>
            </div>

            {/* Marital Status */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Marital Status
              </label>
              <select
                value={maritalStatus}
                onChange={(e) => setMaritalStatus(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-lg py-2 px-3 text-sm text-dark-text focus:outline-none focus:border-dark-accent transition-all duration-300"
              >
                <option value="Single">Single</option>
                <option value="Married">Married</option>
                <option value="Divorced">Divorced</option>
              </select>
            </div>

            {/* Number of Addresses */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Number of Addresses
              </label>
              <div className="flex items-center space-x-3 bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 justify-between">
                <span className="text-sm font-semibold text-dark-text">{addresses}</span>
                <div className="flex space-x-1">
                  <button onClick={() => adjustCounter(addresses, setAddresses, 1, 10, -1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">-</button>
                  <button onClick={() => adjustCounter(addresses, setAddresses, 1, 10, 1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">+</button>
                </div>
              </div>
            </div>

            {/* Preferred Order Category */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Preferred Order Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-lg py-2 px-3 text-sm text-dark-text focus:outline-none focus:border-dark-accent transition-all duration-300"
              >
                <option value="Laptop & Accessory">Laptop & Accessory</option>
                <option value="Mobile Phone">Mobile Phone</option>
                <option value="Fashion">Fashion</option>
                <option value="Grocery">Grocery</option>
                <option value="Others">Others</option>
              </select>
            </div>

            {/* Number of Devices Registered */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Number of Devices Registered
              </label>
              <div className="flex items-center space-x-3 bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 justify-between">
                <span className="text-sm font-semibold text-dark-text">{devices}</span>
                <div className="flex space-x-1">
                  <button onClick={() => adjustCounter(devices, setDevices, 1, 6, -1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">-</button>
                  <button onClick={() => adjustCounter(devices, setDevices, 1, 6, 1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">+</button>
                </div>
              </div>
            </div>

            {/* Satisfaction Score slider */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-dark-text">
                <span>Satisfaction Score</span>
                <span className="text-dark-accent font-bold">{satisfaction}</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                step="1"
                value={satisfaction > 5 ? 5 : satisfaction} // clamp mapping
                onChange={(e) => setSatisfaction(e.target.value)}
                className="w-full h-1 bg-dark-border rounded-lg appearance-none cursor-pointer accent-dark-accent"
              />
              <div className="flex justify-between text-[10px] text-dark-textMuted font-bold">
                <span>1</span>
                <span>5</span>
              </div>
            </div>

            {/* Days Since Last Order */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Days Since Last Order
              </label>
              <div className="flex items-center space-x-3 bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 justify-between">
                <span className="text-sm font-semibold text-dark-text">{daysSinceOrder}</span>
                <div className="flex space-x-1">
                  <button onClick={() => adjustCounter(daysSinceOrder, setDaysSinceOrder, 0, 30, -1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">-</button>
                  <button onClick={() => adjustCounter(daysSinceOrder, setDaysSinceOrder, 0, 30, 1)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">+</button>
                </div>
              </div>
            </div>

            {/* Cashback Amount */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Cashback Amount ($)
              </label>
              <div className="flex items-center space-x-3 bg-dark-bg border border-dark-border rounded-lg px-3 py-1.5 justify-between">
                <span className="text-sm font-semibold text-dark-text">${cashback.toFixed(2)}</span>
                <div className="flex space-x-1">
                  <button onClick={() => adjustCounter(cashback, setCashback, 0, 300, -10.00)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">-</button>
                  <button onClick={() => adjustCounter(cashback, setCashback, 0, 300, 10.00)} className="px-2 py-0.5 bg-dark-border text-dark-text text-sm rounded hover:bg-dark-accent hover:text-white transition-colors">+</button>
                </div>
              </div>
            </div>

            {/* Has Complained */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-dark-textMuted uppercase tracking-wider">
                Has Complained?
              </label>
              <select
                value={complain}
                onChange={(e) => setComplain(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-lg py-2 px-3 text-sm text-dark-text focus:outline-none focus:border-dark-accent transition-all duration-300"
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
            </div>
          </div>

          <div className="pt-4 border-t border-dark-border flex justify-end">
            <button
              onClick={handlePredict}
              disabled={loading}
              className="flex items-center space-x-2 px-6 py-3 rounded-lg text-sm font-bold text-white bg-dark-accent hover:bg-dark-accentHover shadow-glow transition-all duration-300 disabled:opacity-50"
            >
              {loading ? <Loader size={16} className="animate-spin" /> : <Brain size={16} />}
              <span>Predict Churn Probability</span>
            </button>
          </div>
        </div>

        {/* Prediction Results panel */}
        <div className="bg-dark-card border border-dark-border rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-dark-text pb-3 border-b border-dark-border mb-6">
              Intelligence Outputs
            </h3>
            
            {!results ? (
              <div className="text-center py-20 text-dark-textMuted space-y-3">
                <HelpCircle size={40} className="mx-auto text-dark-border" />
                <p className="text-sm font-medium">No simulation run yet</p>
                <p className="text-xs">Adjust attributes on the left and click predict to run model pipeline</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Churn Risk Output */}
                <div>
                  <h4 className="text-xs font-bold text-dark-textMuted uppercase tracking-wider mb-2">Churn Prediction Model</h4>
                  <div className="bg-dark-bg p-4 rounded-xl border border-dark-border/40 space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-dark-textMuted">Churn Probability:</span>
                      <span className="text-lg font-mono font-bold text-dark-text">
                        {(results.churn.churn_probability * 100).toFixed(2)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-dark-textMuted">Risk Classification:</span>
                      <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                        results.churn.risk_level === 'High' ? 'bg-danger/10 text-danger border border-danger/20' :
                        results.churn.risk_level === 'Medium' ? 'bg-warning/10 text-warning border border-warning/20' :
                        'bg-success/10 text-success border border-success/20'
                      }`}>
                        {results.churn.risk_level} Risk
                      </span>
                    </div>
                  </div>
                </div>

                {/* Behavioral Segmentation Output */}
                <div>
                  <h4 className="text-xs font-bold text-dark-textMuted uppercase tracking-wider mb-2">Behavior Segmentation Model</h4>
                  <div className="bg-dark-bg p-4 rounded-xl border border-dark-border/40">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-dark-textMuted">Assigned Segment:</span>
                      <span className="text-sm font-bold text-dark-accent">
                        {results.segment.segment} Customer
                      </span>
                    </div>
                  </div>
                </div>

                {/* Decision Recommendation Output */}
                <div>
                  <h4 className="text-xs font-bold text-dark-textMuted uppercase tracking-wider mb-2">Decision Intelligence Action</h4>
                  <div className="bg-dark-accent/15 border border-dark-accent/30 p-4 rounded-xl relative overflow-hidden space-y-2">
                    <div className="absolute top-0 right-0 p-2 text-dark-accent/25">
                      <Sparkles size={20} />
                    </div>
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold px-2 py-0.5 rounded bg-dark-accent/20 text-dark-text capitalize">
                        {results.recommendation.action_type}
                      </span>
                      <span className={`font-bold ${
                        results.recommendation.priority === 'High' ? 'text-danger' : 
                        results.recommendation.priority === 'Medium' ? 'text-warning' : 'text-success'
                      }`}>
                        {results.recommendation.priority} Priority
                      </span>
                    </div>
                    <p className="text-xs text-dark-text leading-relaxed">
                      {results.recommendation.recommendation_text}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Predictor;
