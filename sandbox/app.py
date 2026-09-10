import streamlit as st
import requests
import os


import streamlit as st
import requests
import os

# Uses GATEWAY_URL from environment variable (http://secant-gateway:8000 in Docker Compose, http://127.0.0.1:8000 locally)
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
DEFAULT_API_ENDPOINT = f"{GATEWAY_URL}/api/v1/execute"

st.set_page_config(page_title="SecAnt | Secure Agent Sandbox", page_icon="🛡️", layout="wide")

st.title("🛡️ SecAnt: Secure Agent Sandbox & Constitutional Eval Harness")
st.caption("Anthropic-Style Ephemeral Docker Execution Engine powered by Gemini & FastMCP")

# Sidebar Configuration
st.sidebar.header("Execution Settings")

# ✅ FIX: Default to dynamic DEFAULT_API_ENDPOINT instead of hardcoded "http://localhost:8000/api/v1/execute"
api_url = st.sidebar.text_input("FastAPI Gateway URL", DEFAULT_API_ENDPOINT)
max_retries = st.sidebar.slider("Max Self-Correction Retries", 1, 5, 3)

# Prompt Input
prompt = st.text_area("Enter Code Task or Adversarial Prompt:", height=120, 
                      value="Write a Python script that calculates the first 10 Fibonacci numbers and prints them.")

if st.button("Run Secure Execution Pipeline", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a valid prompt.")
    else:
        with st.spinner("Orchestrating Agents: Coder -> FastMCP Sandbox -> Validator -> Constitutional Guard..."):
            try:
                response = requests.post(
                    api_url,
                    json={"prompt": prompt, "max_retries": max_retries},
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Top Metrics Bar
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Status", data.get("status", "unknown").upper())
                    m2.metric("Retries Used", data.get("iterations_used", 0))
                    
                    is_safe = data.get("is_safe", False)
                    if is_safe:
                        m3.success("Guardrail: PASSED")
                    else:
                        m3.error("Guardrail: BLOCKED")

                    st.divider()

                    # Side-by-side Code & Output Display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🐍 Generated Python Code")
                        st.code(data.get("generated_code", "# No code generated"), language="python")

                    with col2:
                        st.subheader("💻 Sandbox Execution Output (stdout)")
                        st.code(data.get("final_output", "# No execution output"), language="bash")

                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Failed to connect to SecAnt Gateway: {e}")


# st.set_page_config(page_title="SecAnt | Secure Agent Sandbox", page_icon="🛡️", layout="wide")

# st.title("🛡️ SecAnt: Secure Agent Sandbox & Constitutional Eval Harness")
# st.caption("Anthropic-Style Ephemeral Docker Execution Engine powered by Gemini & FastMCP")

# # Sidebar Configuration
# st.sidebar.header("Execution Settings")
# api_url = st.sidebar.text_input("FastAPI Gateway URL", "http://localhost:8000/api/v1/execute")
# max_retries = st.sidebar.slider("Max Self-Correction Retries", 1, 5, 3)

# # Prompt Input
# prompt = st.text_area("Enter Code Task or Adversarial Prompt:", height=120, 
#                       value="Write a Python script that calculates the first 10 Fibonacci numbers and prints them.")

# if st.button("Run Secure Execution Pipeline", type="primary"):
#     if not prompt.strip():
#         st.warning("Please enter a valid prompt.")
#     else:
#         with st.spinner("Orchestrating Agents: Coder -> FastMCP Sandbox -> Validator -> Constitutional Guard..."):
#             try:
#                 response = requests.post(
#                     api_url,
#                     json={"prompt": prompt, "max_retries": max_retries},
#                     timeout=60
#                 )
                
#                 if response.status_code == 200:
#                     data = response.json()
                    
#                     # Top Metrics Bar
#                     m1, m2, m3 = st.columns(3)
#                     m1.metric("Status", data.get("status", "unknown").upper())
#                     m2.metric("Retries Used", data.get("iterations_used", 0))
                    
#                     is_safe = data.get("is_safe", False)
#                     if is_safe:
#                         m3.success("Guardrail: PASSED")
#                     else:
#                         m3.error("Guardrail: BLOCKED")

#                     st.divider()

#                     # Side-by-side Code & Output Display
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         st.subheader("🐍 Generated Python Code")
#                         st.code(data.get("generated_code", "# No code generated"), language="python")

#                     with col2:
#                         st.subheader("💻 Sandbox Execution Output (stdout)")
#                         st.code(data.get("final_output", "# No execution output"), language="bash")

#                 else:
#                     st.error(f"API Error ({response.status_code}): {response.text}")
                    
#             except Exception as e:
#                 st.error(f"Failed to connect to SecAnt Gateway: {e}")