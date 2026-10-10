import os
import streamlit as st
from groq import Groq

# Page layout and configuration
st.set_page_config(page_title="CodeScripter AI", page_icon="💻", layout="wide")

st.title("💻 CodeScripter AI Assistant")
st.write("Welcome to CodeScripter! Ask any coding question, generate scripts, or debug your code below.")

# Retrieve API key safely from Render Environment Variables or fallback to sidebar
groq_api_key = os.environ.get("GROQ_API_KEY") or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not groq_api_key:
    st.error("Please add GROQ_API_KEY to Render Environment Variables or enter it in the sidebar.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Fetch available models and filter out non-chat models (like Whisper and Guard models)
try:
    all_models = [m.id for m in client.models.list().data]
    chat_models = [
        m for m in all_models 
        if not any(excluded in m.lower() for excluded in ["whisper", "guard", "safetensors", "distil-whisper"])
    ]
    available_models = chat_models if chat_models else all_models
except Exception:
    available_models = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]

# Sidebar settings
st.sidebar.header("Settings")
model = st.sidebar.selectbox("Choose Model:", available_models)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process user input
if prompt := st.chat_input("What code or programming question do you need help with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are CodeScripter, an expert AI programming assistant."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                stream=True,
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred while connecting to Groq: {e}")

