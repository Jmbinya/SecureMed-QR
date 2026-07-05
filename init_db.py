# init_db.py
# Run this ONCE to create the patients and access_logs tables.
# Safe to re-run — uses CREATE TABLE IF NOT EXISTS.

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

CREATE_PATIENTS = """
CREATE TABLE IF NOT EXISTS patients (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    qr_id          VARCHAR(64)   NOT NULL UNIQUE,
    encrypted_data LONGBLOB      NOT NULL,
    iv             VARBINARY(16) NOT NULL,
    gcm_tag        VARBINARY(16) NOT NULL,
    data_hash      CHAR(64)      NOT NULL,
    salt           VARBINARY(32) NOT NULL,
    totp_secret    VARCHAR(64)   NOT NULL,
    password_hash  VARCHAR(255)  NOT NULL,
    created_at     DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_ACCESS_LOGS = """
CREATE TABLE IF NOT EXISTS access_logs (
    id             INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    patient_qr_id  VARCHAR(64)  NOT NULL,
    responder_ip   VARCHAR(45)  NOT NULL,
    accessed_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    success        TINYINT(1)   NOT NULL DEFAULT 0,
    failure_reason VARCHAR(128) DEFAULT NULL,
    INDEX idx_patient (patient_qr_id),
    INDEX idx_time    (accessed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

def init_db():
    print("\n--- SecureMed QR: Database Initialisation ---\n")
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "securemed"),
        )
        cursor = conn.cursor()

        print("Creating table: patients ...")
        cursor.execute(CREATE_PATIENTS)
        print("✅ patients — done")

        print("Creating table: access_logs ...")
        cursor.execute(CREATE_ACCESS_LOGS)
        print("✅ access_logs — done")

        conn.commit()

        # Verify
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n✅ Tables in database: {tables}")

        cursor.close()
        conn.close()
        print("\n✅ Initialisation complete. Run test_db_connection.py to verify.\n")

    except mysql.connector.Error as e:
        print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    init_db()