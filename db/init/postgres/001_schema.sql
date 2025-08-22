CREATE DATABASE warehouse_db;
\connect warehouse_db;

-- users: 角色包含 manager, staff
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  role VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  price NUMERIC(10,2),
  cost NUMERIC(10,2)
);

CREATE TABLE IF NOT EXISTS inventory (
  id SERIAL PRIMARY KEY,
  product_id INT NOT NULL REFERENCES products(id),
  location_id INT NOT NULL REFERENCES locations(id),
  quantity INT NOT NULL DEFAULT 0
);

INSERT INTO users (username, role) VALUES
  ('charlie', 'manager'),
  ('diana', 'staff')
ON CONFLICT (username) DO UPDATE SET role=EXCLUDED.role;

INSERT INTO locations (name) VALUES ('WH-1'), ('WH-2')
ON CONFLICT DO NOTHING;

INSERT INTO products (name, price, cost) VALUES
  ('Widget A', 99.90, 60.00),
  ('Widget B', 149.00, 90.00)
ON CONFLICT DO NOTHING;

INSERT INTO inventory (product_id, location_id, quantity) VALUES
  (1, 1, 120),
  (2, 1, 45),
  (1, 2, 30);
