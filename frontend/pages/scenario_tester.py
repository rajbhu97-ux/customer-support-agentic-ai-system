import streamlit as st
import json
from pathlib import Path

DATA_DIR = str(Path(__file__).parent.parent.parent) + "/data/"

def load_scenarios():
    with open(DATA_DIR + "scenarios/failure_scenarios.json") as f:
        return json.load(f)

def render():
    st.title("🧪 Scenario Tester")
    st.markdown("Test the AI agent against known failure scenarios.")
    st.markdown("---")

    scenarios = load_scenarios()

    # --- Filters ---
    with st.expander("🔍 Filters", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            scenario_types = sorted(set(s["scenario_name"] for s in scenarios))
            selected_types = st.multiselect(
                "Scenario Type",
                scenario_types,
                default=scenario_types
            )

        with col2:
            consistency = st.selectbox(
                "Consistency",
                ["All", "Consistent", "Inconsistent"]
            )

    # Apply filters
    filtered = [s for s in scenarios if s["scenario_name"] in selected_types]
    if consistency == "Consistent":
        filtered = [s for s in filtered if s["is_consistent"]]
    elif consistency == "Inconsistent":
        filtered = [s for s in filtered if not s["is_consistent"]]

    # --- Summary metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scenarios", len(scenarios))
    col2.metric("Filtered", len(filtered))
    col3.metric("Scenario Types", len(scenario_types))

    st.markdown("---")

    # --- Scenario selector ---
    if not filtered:
        st.warning("No scenarios match your filters.")
        return

    scenario_options = {
        f"{s['scenario_id']} — {s['scenario_name']}": s for s in filtered
    }

    selected_label = st.selectbox("Select Scenario", list(scenario_options.keys()))
    scenario = scenario_options[selected_label]

    st.markdown("---")

    # --- Scenario detail ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader(f"📋 {scenario['scenario_name'].replace('_', ' ').title()}")
        st.markdown(f"**ID:** `{scenario['scenario_id']}`")
        st.markdown(f"**Description:** {scenario['description']}")
        st.markdown(f"**Created At:** {scenario['created_at']}")

        st.markdown("---")
        st.markdown("#### 🎯 Expected Agent Action")
        st.info(scenario["expected_agent_action"])

    with col_right:
        st.markdown("#### ⚠️ System State")
        state = scenario["system_state"]
        status_emoji = {
            "SUCCESS": "✅", "FAILED": "❌", "PENDING": "⏳",
            "NONE": "⬜", "NOT_CREATED": "🚫", "DELIVERED": "📦",
            "IN_TRANSIT": "🚚", "UNKNOWN": "❓", "APPROVED": "✅",
            "COMPLETED": "✅", "DISPUTED": "⚠️", "PARTIAL": "🔶"
        }
        for key, value in state.items():
            emoji = status_emoji.get(value, "•")
            st.markdown(f"**{key.replace('_', ' ').title()}:** {emoji} `{value}`")

        st.markdown("---")
        is_consistent = scenario["is_consistent"]
        if is_consistent:
            st.success("✅ Consistent State")
        else:
            st.error("❌ Inconsistent State")

    st.markdown("---")

    # --- Context detail ---
    st.subheader("🔬 Full Context")
    context = scenario["context"]

    tabs = st.tabs(["👤 Customer", "📦 Order", "💳 Payment", "🚚 Shipment", "💸 Refund"])

    with tabs[0]:
        c = context.get("customer", {})
        if c:
            col1, col2 = st.columns(2)
            col1.markdown(f"**Name:** {c.get('first_name')} {c.get('last_name')}")
            col1.markdown(f"**Email:** {c.get('email')}")
            col1.markdown(f"**Phone:** {c.get('phone')}")
            col1.markdown(f"**Tier:** `{c.get('tier')}`")
            col2.markdown(f"**Customer ID:** `{c.get('customer_id')}`")
            col2.markdown(f"**Total Orders:** {c.get('total_orders')}")
            col2.markdown(f"**Total Tickets:** {c.get('total_tickets')}")
            col2.markdown(f"**Lifetime Value:** ${c.get('lifetime_value_usd', 0):,.2f}")
            col2.markdown(f"**Active:** {'Yes' if c.get('is_active') else 'No'}")
        else:
            st.info("No customer data.")

    with tabs[1]:
        o = context.get("order", {})
        if o:
            col1, col2 = st.columns(2)
            col1.markdown(f"**Order ID:** `{o.get('order_id')}`")
            col1.markdown(f"**Status:** `{o.get('status')}`")
            col1.markdown(f"**Items:** {o.get('item_count')}")
            col1.markdown(f"**Created:** {o.get('created_at')}")
            col2.markdown(f"**Subtotal:** ${o.get('subtotal_usd', 0):,.2f}")
            col2.markdown(f"**Tax:** ${o.get('tax_usd', 0):,.2f}")
            col2.markdown(f"**Shipping:** ${o.get('shipping_fee_usd', 0):,.2f}")
            col2.markdown(f"**Total:** ${o.get('total_usd', 0):,.2f}")
            st.markdown("**Items:**")
            for item in o.get("items", []):
                st.markdown(f"- `{item['product_id']}` × {item['quantity']} @ ${item['unit_price_usd']} =${item['line_total_usd']}")
        else:
            st.info("No order data.")

    with tabs[2]:
        p = context.get("payment", {})
        if p:
            col1, col2 = st.columns(2)
            col1.markdown(f"**Payment ID:** `{p.get('payment_id')}`")
            col1.markdown(f"**Status:** `{p.get('status')}`")
            col1.markdown(f"**Method:** `{p.get('method')}`")
            col1.markdown(f"**Amount:** ${p.get('amount_usd', 0):,.2f}")
            col2.markdown(f"**Gateway:** `{p.get('gateway')}`")
            col2.markdown(f"**Card:** `{p.get('card_network')} ****{p.get('card_last4')}`")
            col2.markdown(f"**Retry Count:** {p.get('retry_count')}")
            col2.markdown(f"**Paid At:** {p.get('paid_at')}")
        else:
            st.info("No payment data.")

    with tabs[3]:
        sh = context.get("shipment", {})
        if sh:
            col1, col2 = st.columns(2)
            col1.markdown(f"**Shipment ID:** `{sh.get('shipment_id')}`")
            col1.markdown(f"**Status:** `{sh.get('status')}`")
            col1.markdown(f"**Carrier:** `{sh.get('carrier')}`")
            col1.markdown(f"**Method:** `{sh.get('shipping_method')}`")
            col2.markdown(f"**Tracking:** `{sh.get('tracking_number')}`")
            col2.markdown(f"**Estimated Delivery:** {sh.get('estimated_delivery')}")
            col2.markdown(f"**Actual Delivery:** {sh.get('actual_delivery', 'N/A')}")
            col2.markdown(f"**Weight:** {sh.get('weight_kg')} kg")
        else:
            st.info("No shipment data.")

    with tabs[4]:
        r = context.get("refund", {})
        if r:
            col1, col2 = st.columns(2)
            col1.markdown(f"**Refund ID:** `{r.get('refund_id')}`")
            col1.markdown(f"**Status:** `{r.get('status')}`")
            col1.markdown(f"**Requested:** ${r.get('requested_amount_usd', 0):,.2f}")
            col2.markdown(f"**Approved:** ${r.get('approved_amount_usd') or 0:,.2f}")
            col2.markdown(f"**Currency:** {r.get('currency')}")
        else:
            st.info("No refund data.")

    st.markdown("---")

    # --- Run scenario button (placeholder for agent integration) ---
    st.subheader("🤖 Run Against Agent")
    st.markdown("Send this scenario context to the AI agent and observe its response.")

    if st.button("▶️ Run Scenario", type="primary"):
        with st.spinner("Running scenario through agent..."):
            # Placeholder — wire to backend agent later
            st.warning("⚙️ Agent backend not connected yet. This will trigger the orchestrator once the backend is wired up.")
            st.json(scenario["system_state"])