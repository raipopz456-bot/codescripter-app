import os
import streamlit as st
from groq import Groq

# Page layout and browser configuration
st.set_page_config(
    page_title="CodeScripter AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme with electric blue accents and grid lines
st.markdown("""
<style>
    /* Dark background with subtle grid lines */
    .stApp {
        background-color: #0b0f17;
        background-image: 
            linear-gradient(to right, rgba(0, 136, 255, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 136, 255, 0.05) 1px, transparent 1px);
        background-size: 30px 30px;
    }

    /* Custom Blue Accents for Input Fields & Sidebar Selectboxes */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        border: 1.5px solid #0088ff !important;
        box-shadow: 0 0 10px rgba(0, 136, 255, 0.2) !important;
        border-radius: 8px !important;
    }

    /* Centered Header & Logo Layout */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 25px;
    }

    .logo-img {
        width: 150px;
        height: 150px;
        margin-bottom: 15px;
        filter: drop-shadow(0px 0px 20px rgba(0, 136, 255, 0.8));
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }

    .sub-title {
        font-size: 1.05rem;
        color: #8b949e;
        margin-bottom: 15px;
    }

    /* Glowing Blue Chat Input Box */
    .stChatInput > div {
        border: 2px solid #0088ff !important;
        box-shadow: 0 0 15px rgba(0, 136, 255, 0.3) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Centered Custom Logo matching exact blue ring bracket design
st.markdown("""
<div class="header-container">
    <svg class="logo-img" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <!-- Outer Glowing Blue Circle -->
        <circle cx="50" cy="50" r="42" fill="none" stroke="#0088ff" stroke-width="4.5"/>
        <!-- Left Bracket (Green/Blue Gradient Accent) -->
        <path d="M 38 32 L 28 32 L 28 68 L 38 68" fill="none" stroke="#00e676" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Right Bracket (Green/Blue Gradient Accent) -->
        <path d="M 62 32 L 72 32 L 72 68 L 62 68" fill="none" stroke="#00e676" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
        <!-- Centered Blue Checkmark -->
        <path d="M 38 52 L 48 62 L 68 38" fill="none" stroke="#0088ff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <div class="main-title">CodeScripter AI Assistant</div>
    <div class="sub-title">Multi-language code generator, debugger, and scripting tool.</div>
</div>
""", unsafe_allow_html=True)

# API Key Retrieval
groq_api_key = os.environ.get("GROQ_API_KEY") or st.sidebar.text_input("Enter Groq API Key:", type="password")

if not groq_api_key:
    st.error("Please set GROQ_API_KEY in Render Environment Variables or enter it in the sidebar.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Dynamic Model Filtering (Excludes Audio, Orpheus, Safeguard, and Speech models)
try:
    raw_models = [m.id for m in client.models.list().data]
    chat_models = [
        m for m in raw_models 
        if not any(excluded in m.lower() for excluded in [
            "whisper", "guard", "orpheus", "safetensors", "distil", "audio", "allam"
        ])
    ]
    available_models = chat_models if chat_models else ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
except Exception:
    available_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

# Sidebar Settings
st.sidebar.header("Settings")
selected_model = st.sidebar.selectbox("Choose Model:", available_models)

# Assistant Persona Selection
system_mode = st.sidebar.selectbox(
    "Assistant Mode:",
    ["Expert Developer", "Beginner Code Tutor", "Bug Hunter & Tester"]
)

system_prompts = {
    "Expert Developer": "You are CodeScripter, an expert software developer. Provide clean, efficient, and well-commented code across any programming language requested.",
    "Beginner Code Tutor": "You are CodeScripter, a patient coding tutor. Explain concepts simply, step-by-step, with clear beginner-friendly examples.",
    "Bug Hunter & Tester": "You are CodeScripter, a QA and security specialist. Focus on analyzing code for bugs, edge cases, performance issues, and unit test coverage."
}

# Clear Session Utility
if st.sidebar.button("Clear Chat Session"):
    st.session_state.messages = []
    st.rerun()

# Isolated User Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Processing
if prompt := st.chat_input("Ask a coding question or paste code to debug..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            completion = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompts[system_mode]},
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
        st.error(f"Error connecting to Groq: {e}")
