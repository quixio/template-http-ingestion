import streamlit as st
import pandas as pd
import psycopg2
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


def init_db_if_needed():
    if not st.session_state.get("db_initialized", False):
        conn = get_conn()
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

        st.session_state["db_initialized"] = True


def get_all_data():
    return pd.read_sql("SELECT * FROM printer_configs ORDER BY printer_id, field_id", get_conn())


def insert_row(printer_id, field_id, field_name, field_scalar):
    with get_conn().cursor() as cur:
        cur.execute("""
            INSERT INTO printer_configs (printer_id, field_id, field_name, field_scalar)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (printer_id, field_id)
            DO UPDATE SET
                field_name = EXCLUDED.field_name,
                field_scalar = EXCLUDED.field_scalar;
        """, (printer_id, field_id, field_name, field_scalar))
        conn.commit()


# init DB before any streamlit stuff
init_db_if_needed()

# ---------- STREAMLIT APP ----------


st.title("📊 HTTP Config Processor Viewer and Editor")
st.text("This shows the current configs used by `HTTP Config Processor`.")
st.text("Edits take <=30 seconds to reflect in the Processor due to its TTL setting.")

# Connect to DB and init if needed
conn = get_conn()

# Show combined data
st.subheader("🧾 Current Configurations")
df_container = st.container()

# Add row form
st.subheader("➕ Add or Update Entry")
with st.form("add_row_form"):
    col1, col2, col3, col4 = st.columns(4)
    printer_id = col1.text_input("Printer ID", placeholder="ex: 3D_PRINTER_2")
    field_id = col2.text_input("Field ID", placeholder="ex: T003")
    field_name = col3.text_input("Field Name", placeholder="ex: sensor_3")
    field_scalar = col4.number_input("Field Scalar", step=0.1)
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not printer_id or not field_id:
            st.error("Printer ID and Field ID are required.")
        try:
            # note: could append this to a cached dataframe, but reloading is simpler
            insert_row(printer_id, field_id, field_name, field_scalar)
            st.success(f"{printer_id} updated field_id '{field_id}'.")
        except Exception as e:
            st.error(f"Error: {e}")

with df_container:
    st.dataframe(get_all_data(), use_container_width=True)
