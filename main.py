import streamlit as st
import requests

# Page UI ki basic settings
st.set_page_config(page_title="TailorTalk AI Agent", page_icon="🤖", layout="centered")
st.title("🤖 TailorTalk Drive Agent")

# Sidebar: System ki status dikhane ke liye
with st.sidebar:
    st.header("System Status")
    st.success("Gemini 1.5 Flash: Active")
    st.info("Drive Search Scope: Assignment Folder")
    st.markdown("---")
    st.write("Author: **Sumit Patel**")

# Chat history ko save rakhne ke liye session state ka use
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chats ko screen par dikhana
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input field
if prompt := st.chat_input("E.g., Find my Daily Reports..."):
    # 1. User ka message screen par dikhana
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Assistant (AI) ka response handle karna
    with st.chat_message("assistant"):
        try:
            # Backend API (FastAPI) ko request bhejna
            res = requests.get(f"http://127.0.0.1:8001/chat?user_query={prompt}").json()
            
            # [CONVERSATIONAL NATURE] - Gemini ka friendly message dikhana
            bot_msg = res.get("message", "Processing your request...")
            st.markdown(f"**AI:** {bot_msg}")
            
            # Agar backend se success status aata hai
            if res["status"] == "success":
                # AI Logic dikhana (Recruiter ko technical depth dikhane ke liye)
                with st.expander("Show AI Query Logic"):
                    st.code(res.get('ai_logic', 'N/A'))

                if res.get("files"):
                    st.write("### 📂 Found Files:")
                    files_history = ""
                    for f in res["files"]:
                        # [DISCOVERABILITY] - Clickable Link (webViewLink) add kiya hai
                        file_link = f"📄 [{f['name']}]({f.get('webViewLink', '#')})"
                        st.markdown(file_link)
                        files_history += file_link + "\n"
                    
                    # Chat history mein save karna
                    st.session_state.messages.append({"role": "assistant", "content": f"{bot_msg}\n\n{files_history}"})
                else:
                    st.info("No files found matching that criteria.")
                    st.session_state.messages.append({"role": "assistant", "content": bot_msg})
            
            elif res["status"] == "chat":
                # Sirf normal baat-cheet (is_query: false wala case)
                st.session_state.messages.append({"role": "assistant", "content": bot_msg})
                
        except Exception as e:
            st.error("Backend connection failed! Please check if FastAPI is running on port 8001.")