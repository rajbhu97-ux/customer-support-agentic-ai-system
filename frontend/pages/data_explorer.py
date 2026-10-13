import streamlit as st
import json
import pandas as pd
from pathlib import Path

DATA_DIR = str(Path(__file__).parent.parent.parent) + "/data/raw/"

def load_json(file_name):
    with open(DATA_DIR + file_name) as f:
        return json.load(f)

def render():
    st.title("🗂️ Data Explorer")
    st.markdown("Browse, filter, and inspect all datasets.")
    st.markdown("---")

    dataset = st.selectbox(
        "Select Dataset",
        ["Tickets", "Orders", "Customers", "Refunds", "Shipments", "Payments", "Products", "Knowledge Base", "Policies"]
    )

    file_map = {
        "Tickets": "tickets.json",
        "Orders": "orders.json",
        "Customers": "customers.json",
        "Refunds": "refunds.json",
        "Shipments": "shipments.json",
        "Payments": "payments.json",
        "Products": "products.json",
        "Knowledge Base": "knowledge_base.json",
        "Policies": "policies.json",
    }

    data = load_json(file_map[dataset])

    # --- Knowledge Base & Policies: card view ---
    if dataset in ["Knowledge Base", "Policies"]:
        st.subheader(f"{dataset} ({len(data)} records)")
        if dataset == "Knowledge Base":
            categories = list(set(item["category"] for item in data))
            selected_cats = st.multiselect("Filter by Category", categories, default=categories)
            filtered = [item for item in data if item["category"] in selected_cats]
            for item in filtered:
                with st.expander(f"📄 {item['title']} — {item['category']}"):
                    st.markdown(f"**Tags:** {', '.join(item.get('tags', []))}")
                    st.markdown("---")
                    st.markdown(item["body"])
        else:
            tiers = list(set(t for item in data for t in item.get("applies_to_tiers", [])))
            selected_tiers = st.multiselect("Filter by Tier", tiers, default=tiers)
            filtered = [item for item in data if any(t in selected_tiers for t in item.get("applies_to_tiers", []))]
            for item in filtered:
                with st.expander(f"📋 {item['name']} — v{item['version']}"):
                    st.markdown(f"**Category:** {item['category']}")
                    st.markdown(f"**Summary:** {item['summary']}")
                    st.markdown(f"**Applies to tiers:** {', '.join(item.get('applies_to_tiers', []))}")
                    st.markdown(f"**Auto-approve below:** ${item.get('auto_approve_below_usd', 'N/A')}")
                    st.markdown("**Rules:**")
                    for rule in item.get("rules", []):
                        st.markdown(f"- {rule}")
        return

    # --- Tabular datasets ---
    df = pd.DataFrame(data)

    with st.expander("🔍 Filters", expanded=True):
        if dataset == "Tickets":
            statuses = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
            priorities = st.multiselect("Priority", df["priority"].unique().tolist(), default=df["priority"].unique().tolist())
            categories = st.multiselect("Category", df["category"].unique().tolist(), default=df["category"].unique().tolist())
            escalated = st.selectbox("Escalated", ["All", "Yes", "No"])
            df = df[df["status"].isin(statuses) & df["priority"].isin(priorities) & df["category"].isin(categories)]
            if escalated == "Yes":
                df = df[df["escalated"] == True]
            elif escalated == "No":
                df = df[df["escalated"] == False]

        elif dataset == "Orders":
            statuses = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
            min_val, max_val = float(df["total_usd"].min()), float(df["total_usd"].max())
            price_range = st.slider("Total (USD)", min_val, max_val, (min_val, max_val))
            df = df[df["status"].isin(statuses) & df["total_usd"].between(price_range[0], price_range[1])]

        elif dataset == "Customers":
            tiers = st.multiselect("Tier", df["tier"].unique().tolist(), default=df["tier"].unique().tolist())
            is_active = st.selectbox("Active", ["All", "Yes", "No"])
            df = df[df["tier"].isin(tiers)]
            if is_active == "Yes":
                df = df[df["is_active"] == True]
            elif is_active == "No":
                df = df[df["is_active"] == False]

        elif dataset == "Refunds":
            statuses = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
            reasons = st.multiselect("Reason", df["reason"].unique().tolist(), default=df["reason"].unique().tolist())
            is_partial = st.selectbox("Partial Refund", ["All", "Yes", "No"])
            df = df[df["status"].isin(statuses) & df["reason"].isin(reasons)]
            if is_partial == "Yes":
                df = df[df["is_partial"] == True]
            elif is_partial == "No":
                df = df[df["is_partial"] == False]

        elif dataset == "Shipments":
            statuses = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
            carriers = st.multiselect("Carrier", df["carrier"].unique().tolist(), default=df["carrier"].unique().tolist())
            methods = st.multiselect("Shipping Method", df["shipping_method"].unique().tolist(),
                default=df["shipping_method"].unique().tolist())
            df = df[df["status"].isin(statuses) & df["carrier"].isin(carriers) & df["shipping_method"].isin(methods)]

        elif dataset == "Payments":
            statuses = st.multiselect("Status", df["status"].unique().tolist(), default=df["status"].unique().tolist())
            methods = st.multiselect("Method", df["method"].unique().tolist(), default=df["method"].unique().tolist())
            networks = st.multiselect("Card Network", df["card_network"].dropna().unique().tolist(),
                default=df["card_network"].dropna().unique().tolist())
            df = df[df["status"].isin(statuses) & df["method"].isin(methods) & df["card_network"].isin(networks)]

        elif dataset == "Products":
            categories = st.multiselect("Category", df["category"].unique().tolist(), default=df["category"].unique().tolist())
            in_stock = st.selectbox("In Stock", ["All", "Yes", "No"])
            is_refundable = st.selectbox("Refundable", ["All", "Yes", "No"])
            df = df[df["category"].isin(categories)]
            if in_stock == "Yes":
                df = df[df["is_in_stock"] == True]
            elif in_stock == "No":
                df = df[df["is_in_stock"] == False]
            if is_refundable == "Yes":
                df = df[df["is_refundable"] == True]
            elif is_refundable == "No":
                df = df[df["is_refundable"] == False]

    # --- Summary metrics ---
    st.markdown(f"**{len(df)} records found**")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    if dataset == "Tickets":
        col1.metric("Open", int((df["status"] == "OPEN").sum()))
        col2.metric("Escalated", int(df["escalated"].sum()))
        col3.metric("Total", len(df))
    elif dataset == "Orders":
        col1.metric("Total Value", f"${df['total_usd'].sum():,.2f}")
        col2.metric("Avg Order Value", f"${df['total_usd'].mean():,.2f}")
        col3.metric("Total Orders", len(df))
    elif dataset == "Refunds":
        col1.metric("Total Approved", f"${df['approved_amount_usd'].sum():,.2f}")
        col2.metric("Partial Refunds", int(df["is_partial"].sum()))
        col3.metric("Total Refunds", len(df))
    elif dataset == "Products":
        col1.metric("Out of Stock", int((df["is_in_stock"] == False).sum()))
        col2.metric("Avg Rating", f"{df['rating'].mean():.2f}")
        col3.metric("Total Products", len(df))
    elif dataset == "Customers":
        col1.metric("Active", int(df["is_active"].sum()))
        col2.metric("Avg Lifetime Value", f"${df['lifetime_value_usd'].mean():,.2f}")
        col3.metric("Total Customers", len(df))

    # --- Data table ---
    st.markdown("---")
    n_rows = st.slider("Rows to display", 5, 100, 20)
    st.dataframe(df.head(n_rows), use_container_width=True)

    # --- Record detail ---
    st.markdown("---")
    st.subheader("🔎 Record Detail")
    id_col_map = {
        "Tickets": "ticket_id", "Orders": "order_id", "Customers": "customer_id",
        "Refunds": "refund_id", "Shipments": "shipment_id", "Payments": "payment_id",
        "Products": "product_id"
    }
    id_col = id_col_map.get(dataset)
    if id_col and id_col in df.columns:
        record_ids = df[id_col].tolist()
        selected_id = st.selectbox(f"Select {id_col}", record_ids)
        record = df[df[id_col] == selected_id].iloc[0].to_dict()
        st.json(record)