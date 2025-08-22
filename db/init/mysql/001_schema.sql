CREATE DATABASE IF NOT EXISTS hospitals_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospitals_db;

-- users: 角色包含 doctor, admin
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(64) NOT NULL UNIQUE,
  role VARCHAR(32) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS doctors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  department VARCHAR(64)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  age INT,
  gender VARCHAR(16)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS medical_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  doctor_id INT NOT NULL,
  diagnosis VARCHAR(255),
  visit_date DATE,
  FOREIGN KEY(patient_id) REFERENCES patients(id),
  FOREIGN KEY(doctor_id) REFERENCES doctors(id)
) ENGINE=InnoDB;

INSERT INTO users (username, role) VALUES
  ("alice", "doctor"),
  ("bob", "admin")
ON DUPLICATE KEY UPDATE role=VALUES(role);

INSERT INTO doctors (name, department) VALUES
  ("Dr. Zhang", "Cardiology"),
  ("Dr. Li", "Oncology");

INSERT INTO patients (name, age, gender) VALUES
  ("Wang Wei", 30, "M"),
  ("Li Na", 25, "F");

INSERT INTO medical_records (patient_id, doctor_id, diagnosis, visit_date) VALUES
  (1, 1, "Hypertension", '2024-01-10'),
  (2, 2, "Breast cancer screening", '2024-02-12');
