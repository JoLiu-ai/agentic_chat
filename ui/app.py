import streamlit as st
import requests
import uuid

# Page Config
st.set_page_config(
    page_title="Agentic Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #f0f2f6;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #e8f0fe;
    }
    h1 {
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar
with st.sidebar:
    st.title("🤖 Agent Control")
    st.markdown("---")
    st.write("Configure your agent session here.")
    
    model_option = st.selectbox(
        "Select Model",
        ("GPT-4o", "Claude 3.5 Sonnet")
    )
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main Chat Interface
st.title("Agentic Chat")
st.markdown("Welcome to the **Agentic Chat** interface. Ask me anything!")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What is your task?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # API Call
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/chat",
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                    "user_id": "default_user"  # In a real app, this would come from auth
                }
            )
            if response.status_code == 200:
                full_response = response.json()["response"]
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Connection Error: {str(e)}")
