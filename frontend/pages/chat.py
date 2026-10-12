import streamlit as st

def render():
    st.title("💬 Customer Support Chat")
    st.markdown("Ask me about your orders, shipments, refunds, or any support issue.")
    st.markdown("---")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Hi! I'm your customer support assistant. How can I help you today?"
            }
        ]
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state["messages"].append({
            "role": "user",
            "content": user_input
        })
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking.."):
                response = f"I have received your message about: {user_input}"
                st.markdown(response)
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": response
            }
        )


        
        
