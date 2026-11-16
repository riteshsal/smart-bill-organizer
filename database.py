import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id SERIAL PRIMARY KEY,
            provider VARCHAR(100),
            bill_type VARCHAR(50),
            customer_name VARCHAR(150),
            bill_number VARCHAR(100),
            account_number VARCHAR(100),
            amount NUMERIC(10, 2),
            due_date DATE,
            billing_period VARCHAR(50),
            notification_email VARCHAR(255),
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def insert_bill(bill_data):
    conn = get_connection()
    cursor = conn.cursor()

    due_date = datetime.strptime(
        bill_data["due_date"],
        "%d-%m-%Y"
    ).date()

    # Check if the bill already exists
    cursor.execute("""
        SELECT id
        FROM bills
        WHERE provider = %s
        AND bill_type = %s
        AND customer_name = %s
        AND bill_number = %s
        AND account_number = %s
        AND amount = %s
        AND due_date = %s
        AND billing_period = %s
        AND notification_email = %s
    """, (
        bill_data["provider"],
        bill_data["bill_type"],
        bill_data["customer_name"],
        bill_data["bill_number"],
        bill_data["account_number"],
        bill_data["amount"],
        due_date,
        bill_data["billing_period"],
        bill_data["user_email"]
    ))

    existing_bill = cursor.fetchone()

    if existing_bill:
        cursor.close()
        conn.close()
        return False

    # Insert new bill
    cursor.execute("""
        INSERT INTO bills (
            provider,
            bill_type,
            customer_name,
            bill_number,
            account_number,
            amount,
            due_date,
            billing_period,
            notification_email,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        bill_data["provider"],
        bill_data["bill_type"],
        bill_data["customer_name"],
        bill_data["bill_number"],
        bill_data["account_number"],
        bill_data["amount"],
        due_date,
        bill_data["billing_period"],
        bill_data["user_email"],
        "pending"
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return True


def get_bills(user_email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            provider,
            bill_type,
            amount,
            due_date,
            notification_email,
            status,
            created_at
        FROM bills
        WHERE notification_email = %s
        ORDER BY due_date ASC
    """, (user_email,))

    bills = cursor.fetchall()

    cursor.close()
    conn.close()

    return bills

def get_bills_due_tomorrow():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            provider,
            bill_type,
            amount,
            due_date,
            notification_email
        FROM bills
        WHERE due_date = CURRENT_DATE + INTERVAL '1 day'
    """)

    bills = cursor.fetchall()

    cursor.close()
    conn.close()

    return bills


if __name__ == "__main__":
    create_table()
    print("Bills table created successfully!")