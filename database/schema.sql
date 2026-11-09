-- Active: 1763021133744@@mysql-5daf24d-alustudent-6fc0.f.aivencloud.com@17558
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS prescription_items;
DROP TABLE IF EXISTS item_stock;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS pharmacies;
DROP TABLE IF EXISTS pharmacists;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS grant_access;
DROP TABLE IF EXISTS prescriptions;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR     NOT NULL,
    email           VARCHAR     NOT NULL,
    phone           VARCHAR     NULL,
    password_hash   VARCHAR     NOT NULL,
    role            ENUM('admin', 'doctor', 'patient', 'pharmacist')    NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      uq_users_email  UNIQUE  (email)

) ENGINE=InnoDB;

CREATE TABLE patients (
    patient_id      INT AUTO_INREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    license_number  VARCHAR NOT NULL,
    speciality      VARCHAR NULL,
    facility        VARCHAR NULL,
    CONSTRAINT  uq_doctors_user UNIQUE (user_id),
    CONSTRAINT  uq_doctors_license UNIQUE (license_number),
    CONSTRAINT  fk_doctors_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE

);




