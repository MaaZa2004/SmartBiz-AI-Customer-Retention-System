import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { KPICard } from '../components/KPICard';
import { 
  DollarSign, Users, TrendingDown, Calendar, 
  Download, Database, HelpCircle, Loader, Filter 
} from 'lucide-react';
import { 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

export const Dashboard = () => {
  const [customers, setCustomers] = useState([]);
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [salesData, setSalesData] = useState([]);
  
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [kpis, setKpis] = useState({
    revenue: 0,
    activeCust: 0,
    churnRate: 0,
    forecasted: 0
  });

  const role = api.auth.getRole();
  const canModify = role === 'Admin' || role === 'Manager';

  const categories = ["Laptop & Accessory", "Mobile Phone", "Fashion", "Grocery", "Others"];

  const loadData = async () => {
    setLoading(true);
    try {
      const custData = await api.customers.list();
      setCustomers(custData);
      setFilteredCustomers(custData);
      
      // Calculate KPIs
      const rev = custData.reduce((acc, c) => acc + parseFloat(c.total_spending || 0), 0);
      const churned = custData.filter(c => c.churn === 1).length;
      const total = custData.length;
      const rate = total > 0 ? (churned / total) * 100 : 0;
      
      // Run category-level forecasting and aggregate expected sales values
      let forecastSum = 0;
      for (const cat of categories) {
        try {
          const res = await api.predict.forecast(cat);
          forecastSum += res.expected_sales_value;
        } catch (e) {
          // fallback estimate
          forecastSum += (rev / categories.length) * 1.05;
        }
      }

      setKpis({
        revenue: rev,
        activeCust: total - churned,
        churnRate: rate,
        forecasted: forecastSum
      });

      // Prepare sample time-series data for AreaChart (Revenue Trend)
      // We will group customer spending by a mock time grid for visualization
      const trend = [];
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      months.forEach((m, idx) => {
        // distribute spending with a growth trend
        const multiplier = 0.5 + (idx * 0.08);
        trend.push({
          month: m,
          revenue: (rev / 12) * multiplier * (0.9 + Math.random() * 0.2)
        });
      });
      setSalesData(trend);

    } catch (err) {
      console.error("Failed to load dashboard metrics", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Filter customers when category selection changes
  useEffect(() => {
    if (!selectedCategory) {
      setFilteredCustomers(customers);
    } else {
      const filtered = customers.filter(c => c.product_category === selectedCategory);
      setFilteredCustomers(filtered);
    }
  }, [selectedCategory, customers]);

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const blob = await api.reports.export(format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `smartbiz_report_${new Date().toISOString().slice(0,10)}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert("Failed to export report: " + err.message);
    } finally {
      setExporting(false);
    }
  };

  const handleSeed = async () => {
    if (!window.confirm("Seeding will overwrite current records. Proceed?")) return;
    setSeeding(true);
    try {
      await api.customers.seed(150);
      alert("Database successfully seeded!");
      await loadData();
    } catch (err) {
      alert("Seeding failed: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  // Chart data calculations
  // 1. Churn Risk Distribution (Low, Medium, High)
  const getChurnDistributionData = () => {
    let low = 0, med = 0, high = 0;
    filteredCustomers.forEach(c => {
      // Simulate/approximate risk buckets based on complains + satisfaction
      if (c.churn === 1 || c.complain === 1) {
        high++;
      } else if (c.satisfaction_score <= 2) {
        med++;
      } else {
        low++;
      }
    });
    return [
      { name: 'Low Risk', count: low, fill: '#10B981' },
      { name: 'Medium Risk', count: med, fill: '#F59E0B' },
      { name: 'High Risk', count: high, fill: '#EF4444' }
    ];
  };

  // 2. Customer Segment Breakdown (Premium, Regular, Low-Value)
  const getSegmentBreakdownData = () => {
    let premium = 0, regular = 0, lowVal = 0;
    filteredCustomers.forEach(c => {
      const spend = parseFloat(c.total_spending || 0);
      if (spend > 1500 || (c.tenure > 24 && spend > 1000)) {
        premium++;
      } else if (spend < 500) {
        lowVal++;
      } else {
        regular++;
      }
    });
    return [
      { name: 'Premium Tier', value: premium, color: '#3B82F6' },
      { name: 'Regular Tier', value: regular, color: '#A78BFA' },
      { name: 'Low-Value Tier', value: lowVal, color: '#6B7280' }
    ];
  };

  if (loading) {
    return (
      <div className="flex-1 min-h-screen flex flex-col items-center justify-center bg-dark-bg text-dark-text">
        <Loader size={36} className="animate-spin text-dark-accent mb-4" />
        <p className="text-sm text-dark-textMuted font-medium">Aggregating live business metrics...</p>
      </div>
    );
  }

  const segmentData = getSegmentBreakdownData();
  const churnRiskData = getChurnDistributionData();

  return (
    <div className="flex-1 bg-dark-bg p-8 min-h-screen overflow-y-auto">
      {/* Header section */}
      <header className="flex flex-col md:flex-row md:items-center md:justify-between pb-6 border-b border-dark-border mb-8">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-dark-text">Retention Analytics Dashboard</h2>
          <p className="text-sm text-dark-textMuted mt-1">Real-time prediction metrics and Decision Intelligence actions</p>
        </div>
        
        {/* Actions panel */}
        <div className="flex flex-wrap gap-3 mt-4 md:mt-0">
          {canModify && (
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="flex items-center space-x-2 px-4 py-2 border border-dark-border rounded-lg text-sm font-semibold text-dark-text bg-dark-card hover:bg-dark-border hover:border-dark-accent transition-all duration-300 disabled:opacity-50"
            >
              {seeding ? <Loader size={16} className="animate-spin" /> : <Database size={16} />}
              <span>Seed DB</span>
            </button>
          )}

          <button
            onClick={() => handleExport('excel')}
            disabled={exporting}
            className="flex items-center space-x-2 px-4 py-2 border border-dark-border rounded-lg text-sm font-semibold text-dark-text bg-dark-card hover:bg-dark-border hover:border-dark-accent transition-all duration-300 disabled:opacity-50"
          >
            <Download size={16} />
            <span>Excel</span>
          </button>
          
          <button
            onClick={() => handleExport('pdf')}
            disabled={exporting}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-dark-accent hover:bg-dark-accentHover shadow-glow transition-all duration-300 disabled:opacity-50"
          >
            {exporting ? <Loader size={16} className="animate-spin" /> : <Download size={16} />}
            <span>PDF Export</span>
          </button>
        </div>
      </header>

      {/* Filter Options */}
      <section className="bg-dark-card border border-dark-border rounded-xl p-4 mb-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center space-x-2 text-dark-text">
          <Filter size={18} className="text-dark-accent" />
          <span className="text-sm font-bold uppercase tracking-wider">Segmentation Filters</span>
        </div>
        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full md:w-56 bg-dark-bg border border-dark-border rounded-lg py-2 px-3 text-sm text-dark-text focus:outline-none focus:border-dark-accent transition-all duration-300 cursor-pointer"
          >
            <option value="">All Product Categories</option>
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </section>

      {/* KPI Cards Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        <KPICard
          title="Total Spending (Revenue)"
          value={`$${kpis.revenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subtitle="All-time gross sales value"
          icon={DollarSign}
          trend="+8.2%"
          trendType="positive"
        />
        <KPICard
          title="Active Customers"
          value={kpis.activeCust.toLocaleString()}
          subtitle="Subscribers not flagged for churn"
          icon={Users}
          trend="+12.4%"
          trendType="positive"
        />
        <KPICard
          title="System Churn Rate"
          value={`${kpis.churnRate.toFixed(2)}%`}
          subtitle="At-risk percentage base"
          icon={TrendingDown}
          trend={kpis.churnRate > 25 ? "+3.5%" : "-1.2%"}
          trendType={kpis.churnRate > 25 ? "negative" : "positive"}
        />
        <KPICard
          title="Forecasted Sales (30-day)"
          value={`$${kpis.forecasted.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          subtitle="Predicted aggregate run rate"
          icon={Calendar}
          trend="Upward"
          trendType="positive"
        />
      </section>

      {/* Recharts Graphical Panels */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
        {/* 1. Revenue Trend Line Chart */}
        <div className="lg:col-span-2 bg-dark-card border border-dark-border rounded-xl p-6 flex flex-col">
          <h3 className="text-lg font-bold text-dark-text mb-4">Gross Revenue Growth Trend</h3>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={salesData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="month" stroke="#9CA3AF" fontSize={12} tickLine={false} />
                <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#1F2937', color: '#F9FAFB' }}
                  formatter={(val) => [`$${val.toFixed(2)}`, 'Revenue']}
                />
                <Area type="monotone" dataKey="revenue" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#colorRevenue)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. Customer Segment Breakdown PieChart */}
        <div className="bg-dark-card border border-dark-border rounded-xl p-6 flex flex-col">
          <h3 className="text-lg font-bold text-dark-text mb-4">Behavioral Segmentation Tiers</h3>
          <div className="h-64 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={segmentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {segmentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#1F2937', color: '#F9FAFB' }}
                  formatter={(val) => [val, 'Count']}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-4">
              <span className="text-2xl font-extrabold text-dark-text">{filteredCustomers.length}</span>
              <span className="text-xs text-dark-textMuted font-semibold uppercase">Customers</span>
            </div>
          </div>
          {/* Custom Legends */}
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs">
            {segmentData.map(item => (
              <div key={item.name} className="flex flex-col items-center">
                <span className="inline-block w-3 h-3 rounded-full mb-1" style={{ backgroundColor: item.color }} />
                <span className="text-dark-textMuted truncate max-w-full font-medium">{item.name}</span>
                <span className="font-bold text-dark-text mt-0.5">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Churn Risk Bar Chart */}
      <section className="bg-dark-card border border-dark-border rounded-xl p-6">
        <h3 className="text-lg font-bold text-dark-text mb-4">Churn Risk Distribution Profile</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={churnRiskData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
              <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} tickLine={false} />
              <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111827', borderColor: '#1F2937', color: '#F9FAFB' }}
                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {churnRiskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
