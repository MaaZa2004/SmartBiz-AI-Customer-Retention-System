const API_BASE_URL = "http://localhost:8000/api";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  const headers = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Authentication
  auth: {
    login: async (email, password) => {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Login failed");
      }
      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("role", data.role);
      return data;
    },
    
    register: async (name, email, password, role) => {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Registration failed");
      }
      return await response.json();
    },
    
    getMe: async () => {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: getHeaders(),
      });
      if (!response.ok) throw new Error("Failed to fetch profile");
      return await response.json();
    },
    
    logout: () => {
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("role");
    },
    
    isAuthenticated: () => {
      return !!localStorage.getItem("token");
    },
    
    getRole: () => {
      return localStorage.getItem("role") || "";
    }
  },

  // Customer Management
  customers: {
    list: async (category = "", churnOnly = null) => {
      let url = `${API_BASE_URL}/customers/?limit=100`;
      if (category) url += `&product_category=${encodeURIComponent(category)}`;
      if (churnOnly !== null) url += `&churn_only=${churnOnly}`;
      
      const response = await fetch(url, { headers: getHeaders() });
      if (!response.ok) throw new Error("Failed to fetch customers");
      return await response.json();
    },
    
    getDetails: async (id) => {
      const response = await fetch(`${API_BASE_URL}/customers/${id}`, {
        headers: getHeaders(),
      });
      if (!response.ok) throw new Error("Failed to fetch customer details");
      return await response.json();
    },
    
    create: async (customerData) => {
      const response = await fetch(`${API_BASE_URL}/customers/`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(customerData),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to create customer");
      }
      return await response.json();
    },
    
    seed: async (records = 200) => {
      const response = await fetch(`${API_BASE_URL}/customers/seed?records=${records}`, {
        method: "POST",
        headers: getHeaders(),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to seed database");
      }
      return await response.json();
    }
  },

  // ML Predictions
  predict: {
    churn: async (customerId) => {
      const response = await fetch(`${API_BASE_URL}/predict/churn`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ customer_id: customerId }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Churn prediction failed");
      }
      return await response.json();
    },
    
    segment: async (customerId) => {
      const response = await fetch(`${API_BASE_URL}/predict/segment`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ customer_id: customerId }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Segmentation failed");
      }
      return await response.json();
    },
    
    forecast: async (category, days = 30) => {
      const response = await fetch(`${API_BASE_URL}/predict/forecast`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ product_category: category, forecast_days: days }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Sales forecasting failed");
      }
      return await response.json();
    }
  },

  // Decision Engine
  decisionEngine: {
    recommend: async (customerId) => {
      const response = await fetch(`${API_BASE_URL}/decision-engine/recommend`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ customer_id: customerId }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Decision engine recommendations failed");
      }
      return await response.json();
    }
  },

  // Reports
  reports: {
    export: async (format = "excel") => {
      const response = await fetch(`${API_BASE_URL}/reports/export?format=${format}`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });
      if (!response.ok) throw new Error("Failed to export report");
      return await response.blob();
    }
  }
};
