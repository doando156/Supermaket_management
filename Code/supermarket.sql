-- Check existing tables
SELECT name FROM sqlite_master WHERE type='table' OR type='view';

-- Creating tables if not exist
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    image_path TEXT,
    details TEXT,
    category TEXT,
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER DEFAULT 10
);

CREATE TABLE IF NOT EXISTS cashier_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cashier_username TEXT,
    login_time TEXT,
    logout_time TEXT,
    active_hours TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE,
    amount FLOAT
);

-- Insert sample data into products table
INSERT INTO products (name, category, price, image_path, details) VALUES 
('Vinamilk 100% Fresh Milk', 'Milk', 25.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\packshot.png', 'Vinamilk 100% fresh milk, rich in nutrients, good for health.'),
('TH True Milk Organic', 'Milk', 30.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\3.jpg', 'TH True Milk organic, natural and pure, suitable for all ages.'),
('Dutch Lady Fresh Milk', 'Milk', 22.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\R.jpg', 'Dutch Lady fresh milk, delicious and nutritious, great for breakfast.'),
('Mộc Châu Milk', 'Milk', 27.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\sua-tuoi-moc-chau-it-duong.jpg', 'Mộc Châu Milk, high quality milk from Mộc Châu highlands.'),
('Nutifood GrowPLUS+', 'Milk', 29.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\GrowPLUS--Nutifood--Effective-nutrition-for-malnourished-and-stunted-kids---400g--900g--1-5-kg--180-ml.jpg', 'Nutifood GrowPLUS+, specially formulated for children growth.'),
('Nestlé NAN Optipro', 'Milk', 35.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\R (1).jpg', 'Nestlé NAN Optipro, premium milk powder for infants and toddlers.'),
('Abbott Ensure Gold', 'Milk', 45.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\OIP.jpg', 'Abbott Ensure Gold, complete and balanced nutrition for adults.'),
('Dalat Milk', 'Milk', 28.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\OIP (1).jpg', 'Dalat Milk, pure fresh milk from Dalat farms.'),
('Meiji Milk', 'Milk', 32.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\29.-Meiji-100-Fresh-Milk-2L.jpg', 'Meiji Milk, high-quality milk imported from Japan.'),
('Enfamil A+', 'Milk', 40.0, 'C:\\Users\\Do Doan\\OneDrive\\Documents\\Visual studio Code\\Quản lí siêu thị ( Dự án cuối kì)\\img\\1092360-1.jpg', 'Enfamil A+, milk formula for brain development in infants.');
