"""
db.py — MySQL connection and database operations for SecureMed QR.

Tables:
  patients     — encrypted medical records, one row per patient
  access_logs  — every scan attempt (success or failure) for audit trail
"""

import mysql.connector
from mysql.connector import pooling
from flask import current_app, g
import os


# ---------------------------------------------------------------------------
# Connection pool — created once when the app starts
# ---------------------------------------------------------------------------

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="securemed_pool",
            pool_size=5,
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "securemed"),
            autocommit=False,
        )
    return _pool


# ---------------------------------------------------------------------------
# Per-request connection (stored on Flask's g object)
# ---------------------------------------------------------------------------

def get_db():
    """Return a MySQL connection for the current request."""
    if "db" not in g:
        g.db = get_pool().get_connection()
    return g.db


def close_db(e=None):
    """Release the connection back to the pool at end of request."""
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

CREATE_PATIENTS = """
CREATE TABLE IF NOT EXISTS patients (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    qr_id         VARCHAR(64)  NOT NULL UNIQUE,   -- public ID embedded in QR
    encrypted_data LONGBLOB    NOT NULL,           -- AES-256-GCM ciphertext
    iv            VARBINARY(16) NOT NULL,          -- GCM initialisation vector
    gcm_tag       VARBINARY(16) NOT NULL,          -- GCM authentication tag
    data_hash     CHAR(64)     NOT NULL,           -- SHA-256 of plaintext
    salt          VARBINARY(32) NOT NULL,          -- PBKDF2 salt for key derivation
    totp_secret   VARCHAR(64)  NOT NULL,           -- base32 TOTP secret
    password_hash VARCHAR(255) NOT NULL,           -- bcrypt hash of patient password
    created_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_ACCESS_LOGS = """
CREATE TABLE IF NOT EXISTS access_logs (
    id            INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_qr_id VARCHAR(64)  NOT NULL,           -- which patient was accessed
    responder_ip  VARCHAR(45)  NOT NULL,           -- IPv4 or IPv6
    accessed_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
    success       TINYINT(1)   NOT NULL DEFAULT 0, -- 1 = OTP verified, 0 = failed
    failure_reason VARCHAR(128) DEFAULT NULL,      -- e.g. 'invalid_otp', 'expired'
    INDEX idx_patient (patient_qr_id),
    INDEX idx_time    (accessed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def init_db():
    """
    Create the securemed database and both tables if they don't exist.
    Called once from create_app() on startup.
    """
    # Connect without specifying a database first so we can CREATE it
    conn = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
    )
    cursor = conn.cursor()
    db_name = os.environ.get("DB_NAME", "securemed")
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    )
    cursor.execute(f"USE `{db_name}`;")
    cursor.execute(CREATE_PATIENTS)
    cursor.execute(CREATE_ACCESS_LOGS)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[db] Database `{db_name}` and tables ready.")


# ---------------------------------------------------------------------------
# Patient helpers
# ---------------------------------------------------------------------------

def insert_patient(qr_id, encrypted_data, iv, gcm_tag,
                   data_hash, salt, totp_secret, password_hash):
    """
    Insert a newly registered patient record.
    All binary values (iv, gcm_tag, salt, encrypted_data) must be bytes.
    """
    sql = """
        INSERT INTO patients
            (qr_id, encrypted_data, iv, gcm_tag, data_hash, salt, totp_secret, password_hash)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (
        qr_id, encrypted_data, iv, gcm_tag,
        data_hash, salt, totp_secret, password_hash
    ))
    conn.commit()
    cursor.close()


def get_patient(qr_id):
    """
    Fetch a patient row by QR ID.
    Returns a dict or None if not found.
    """
    sql = """
        SELECT qr_id, encrypted_data, iv, gcm_tag,
               data_hash, salt, totp_secret, password_hash
        FROM patients
        WHERE qr_id = %s
        LIMIT 1
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (qr_id,))
    row = cursor.fetchone()
    cursor.close()
    return row


def update_patient(qr_id, encrypted_data, iv, gcm_tag, data_hash):
    """Update encrypted record after a patient edits their profile."""
    sql = """
        UPDATE patients
        SET encrypted_data = %s, iv = %s, gcm_tag = %s, data_hash = %s
        WHERE qr_id = %s
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (encrypted_data, iv, gcm_tag, data_hash, qr_id))
    conn.commit()
    cursor.close()


# ---------------------------------------------------------------------------
# Access log helpers
# ---------------------------------------------------------------------------

def log_access(patient_qr_id, responder_ip, success, failure_reason=None):
    """
    Write one row to access_logs.
    Call this for every scan attempt — successful or not.
    """
    sql = """
        INSERT INTO access_logs (patient_qr_id, responder_ip, success, failure_reason)
        VALUES (%s, %s, %s, %s)
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(sql, (patient_qr_id, responder_ip, int(success), failure_reason))
    conn.commit()
    cursor.close()


def get_access_logs(patient_qr_id, limit=20):
    """Return the most recent access attempts for a patient (for their dashboard)."""
    sql = """
        SELECT responder_ip, accessed_at, success, failure_reason
        FROM access_logs
        WHERE patient_qr_id = %s
        ORDER BY accessed_at DESC
        LIMIT %s
    """
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (patient_qr_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    return rows