import os

import pandas as pd
import psycopg2


def db_conn():
    return psycopg2.connect(
        **{
            "host": os.environ["POSTGRES_HOST"],
            "port": os.environ["POSTGRES_PORT"],
            "dbname": os.environ["POSTGRES_DBNAME"],
            "user": os.environ["POSTGRES_USER"],
            "password": os.environ["POSTGRES_PASSWORD"],
        }
    )


def init_db():
    conn = db_conn()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS printer_configs (
                printer_id TEXT NOT NULL,
                field_id TEXT NOT NULL,
                field_name TEXT,
                field_scalar FLOAT,
                PRIMARY KEY (printer_id, field_id)
            );
        """)
        conn.commit()

    # Add initial data if table is empty
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM printer_configs;")
        if cur.fetchone()[0] == 0:
            cur.executemany("""
                INSERT INTO printer_configs (printer_id, field_id, field_name, field_scalar)
                VALUES (%s, %s, %s, %s)
            """, [
                ("3D_PRINTER_2", "T001", "sensor_1", 1.0),
                ("3D_PRINTER_2", "T002", "sensor_2", 1.0)
            ])
            conn.commit()


def get_all_data(conn):
    return pd.read_sql("SELECT * FROM printer_configs ORDER BY printer_id, field_id", conn)


def insert_row(conn, printer_id, field_id, field_name, field_scalar):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO printer_configs (printer_id, field_id, field_name, field_scalar)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (printer_id, field_id)
            DO UPDATE SET
                field_name = EXCLUDED.field_name,
                field_scalar = EXCLUDED.field_scalar;
        """, (printer_id, field_id, field_name, field_scalar))
        conn.commit()


if __name__ == '__main__':
    init_db()