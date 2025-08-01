import streamlit as st
from db_helpers import db_conn, insert_row, get_all_data


@st.cache_resource
def get_db_conn():
    return db_conn()


st.title("📊 HTTP Config Processor Viewer and Editor")
st.text("This shows the current configs used by `HTTP Config Processor`.")
st.text("Edits take <=30 seconds to reflect in the Processor due to its TTL setting.")

# Connect to DB and init if needed
conn = get_db_conn()

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
            insert_row(conn, printer_id, field_id, field_name, field_scalar)
            st.success(f"{printer_id} updated field_id '{field_id}'.")
        except Exception as e:
            st.error(f"Error: {e}")

with df_container:
    st.dataframe(get_all_data(conn), use_container_width=True)
