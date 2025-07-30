import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql
import os


# ---------- DB FUNCTIONS ----------

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        **{
            "host": os.environ["POSTGRES_HOST"],
            "port": os.environ["POSTGRES_PORT"],
            "dbname": os.environ["POSTGRES_DBNAME"],
            "user": os.environ["POSTGRES_USER"],
            "password": os.environ["POSTGRES_PASSWORD"],
        }
    )


def init_db_if_needed(conn):
    if not st.session_state.get("db_initialized", False):
        with conn.cursor() as cur:
            # Check if any user tables exist
            cur.execute("""
                SELECT COUNT(*) FROM pg_tables
                WHERE schemaname = 'public';
            """)
            table_count = cur.fetchone()[0]

            if table_count == 0:
                cur.execute("""
                    CREATE TABLE "3D_PRINTER_2" (
                        field_id TEXT,
                        field_name TEXT,
                        field_scalar FLOAT
                    );
                """)
                cur.executemany("""
                    INSERT INTO "3D_PRINTER_2" (field_id, field_name, field_scalar)
                    VALUES (%s, %s, %s);
                """, [
                    ("T001", "sensor_1", 1.0),
                    ("T002", "sensor_2", 1.0),
                ])
                conn.commit()

        st.session_state["db_initialized"] = True


def get_all_data(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public';
        """)
        tables = [row[0] for row in cur.fetchall()]

        all_rows = []
        for table in tables:
            cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table)))
            rows = cur.fetchall()
            for row in rows:
                all_rows.append({
                    "table_name": table,
                    "field_id": row[0],
                    "field_name": row[1],
                    "field_scalar": row[2]
                })
        return pd.DataFrame(all_rows)


def insert_row(conn, table_name, field_id, field_name, field_scalar):
    with conn.cursor() as cur:
        # Ensure table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM pg_tables WHERE schemaname='public' AND tablename=%s
            );
        """, (table_name,))
        exists = cur.fetchone()[0]

        if not exists:
            cur.execute(sql.SQL("""
                CREATE TABLE {} (
                    field_id TEXT,
                    field_name TEXT,
                    field_scalar FLOAT
                );
            """).format(sql.Identifier(table_name)))

        # Insert row
        cur.execute(sql.SQL("""
            INSERT INTO {} (field_id, field_name, field_scalar)
            VALUES (%s, %s, %s);
        """).format(sql.Identifier(table_name)),
        (field_id, field_name, field_scalar))

        conn.commit()


# ---------- STREAMLIT APP ----------


st.title("📊 PostgreSQL Configuration Interface")

# Connect to DB and init if needed
conn = get_conn()
init_db_if_needed(conn)

# Show combined data
st.subheader("🧾 Current Configurations")
df = get_all_data(conn)
st.dataframe(df, use_container_width=True)

# Add row form
st.subheader("➕ Add New Entry")
with st.form("add_row_form"):
    col1, col2 = st.columns(2)
    table_name = col1.text_input("Table Name", placeholder="3D_PRINTER_2")
    field_id = col2.text_input("Field ID", placeholder="ex: T003")

    col3, col4 = st.columns(2)
    field_name = col3.text_input("Field Name", placeholder="ex: sensor_3")
    field_scalar = col4.number_input("Field Scalar", step=0.1)

    submitted = st.form_submit_button("Submit")

    if submitted:
        try:
            insert_row(conn, table_name, field_id, field_name, field_scalar)
            st.success(f"Row added to `{table_name}`.")
            st.experimental_rerun()  # Refresh to show update
        except Exception as e:
            st.error(f"Error: {e}")
