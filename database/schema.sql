-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'Admin', 'Business Analyst', 'Manager'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY, -- Alphanumeric Customer ID (e.g. C-10001)
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(20) DEFAULT NULL,
    age INT DEFAULT NULL,
    tenure INT DEFAULT NULL, -- in months
    satisfaction_score INT DEFAULT NULL,
    num_orders INT DEFAULT NULL,
    total_spending DECIMAL(12, 2) DEFAULT 0.00,
    last_purchase_date DATE DEFAULT NULL,
    product_category VARCHAR(100) DEFAULT NULL, -- Preferred order category
    warehouse_to_home INT DEFAULT NULL, -- distance in km
    marital_status VARCHAR(20) DEFAULT NULL, -- 'Single', 'Married', 'Divorced'
    num_addresses INT DEFAULT NULL,
    num_devices_registered INT DEFAULT NULL,
    days_since_last_order INT DEFAULT NULL,
    cashback_amount DECIMAL(10, 2) DEFAULT 0.00,
    complain INT DEFAULT 0, -- 0 = No, 1 = Yes
    churn INT DEFAULT 0, -- 0 = No, 1 = Yes (Target Label)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customers_category (product_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Sales Table
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    product_category VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_sales_customer_id (customer_id),
    INDEX idx_sales_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Transactions Table
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    sale_id INT DEFAULT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL, -- 'Success', 'Pending', 'Failed'
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL,
    INDEX idx_transactions_customer_id (customer_id),
    INDEX idx_transactions_date (transaction_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'churn', 'segment', 'forecast'
    result_value VARCHAR(255) NOT NULL, -- e.g. Churn risk (High/Medium/Low), Segment name, or Forecasted value
    confidence_score DECIMAL(5, 4) DEFAULT NULL, -- Probability/confidence level
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_predictions_customer_id (customer_id),
    INDEX idx_predictions_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    recommendation_text TEXT NOT NULL,
    action_type VARCHAR(100) NOT NULL, -- 'retention action', 'marketing suggestion', 'next-best-action'
    priority VARCHAR(20) NOT NULL, -- 'High', 'Medium', 'Low'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    INDEX idx_recommendations_customer_id (customer_id),
    INDEX idx_recommendations_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
