import streamlit as st
import json
from pathlib import Path
import pandas as pd

print(Path(__file__).parent.parent.parent)
DATA_DIR = str(Path(__file__).parent.parent.parent) + "/data/raw/"

def load_json(file_name):
    with open(DATA_DIR + file_name) as f:
        return json.load(f)


def render():
    st.title("📊 Support Dashboard")
    st.markdown("Live metrics from the customer support system.")
    st.markdown("---")

    refunds = load_json("refunds.json")
    orders = load_json("orders.json")
    tickets = load_json("tickets.json")
    customers = load_json("customers.json")

    col1, col2, col3, col4 = st.columns(4)

    total_tickets = len(tickets)
    open_tickets = sum(1 for t in tickets if t["status"] == "OPEN")
    total_refunds = len(refunds)
    total_customers = len(customers)

    col1.metric("🎫 Total Tickets", total_tickets)
    col2.metric("🔓 Open Tickets", open_tickets)
    col3.metric("💸 Total Refunds", total_refunds)
    col4.metric("👥 Total Customers", total_customers)

    st.markdown("---")

    # --- Middle row: Charts ---
    col_left, col_right = st.columns(2)

    df_tickets = pd.DataFrame(tickets)

    with col_left:
        st.subheader("Tickets by Status")
        if "status" in df_tickets.columns:
            status_counts = df_tickets["status"].value_counts()
            st.bar_chart(status_counts)
        else:
            st.info("No status data available.")

    with col_right:
        st.subheader("Tickets by Category")
        if "category" in df_tickets.columns:
            category_counts = df_tickets["category"].value_counts()
            st.bar_chart(category_counts)
        else:
            st.info("No category data available.")

    st.markdown("---")

    # --- Bottom row: Recent tickets table ---
    st.subheader("🕐 Recent Tickets")
    columns_to_show = ["ticket_id", "status", "priority", "category", "created_at"]
    available_columns = [c for c in columns_to_show if c in df_tickets.columns]
    st.dataframe(
        df_tickets[available_columns].head(10),
        use_container_width=True
    )
