# import streamlit as st
# import asyncio
# from src.state import AgentState
# from main import build_app
# from src.langflow_client import run_langflow

# # Page Config
# st.set_page_config(page_title="GenAI Mechanic", page_icon="🚗", layout="wide")

# st.title("🚗 AI Vehicle Diagnostic Assistant")
# st.markdown("---")

# # --- Sidebar: The "OBD-II Port" Simulator ---
# with st.sidebar:
#     st.header("🔌 OBD-II Simulator")
#     st.info("Simulate the data coming from the car's computer.")
    
#     # 1. DTC Selector
#     selected_dtcs = st.multiselect(
#         "Active Fault Codes (DTCs)",
#         ["P0300", "P0171", "P0420", "P0442", "OEM-991"],
#         default=[]
#     )
    
#     # 2. Sensor Sliders
#     st.subheader("Live Sensor Data")
#     rpm = st.slider("Engine RPM", 0, 8000, 850)
#     fuel_trim = st.slider("Fuel Trim (STFT %)", -25, 25, 0)
#     temp = st.slider("Coolant Temp (°F)", 0, 250, 195)
    
#     # Pack sensor data into a dict
#     sensor_snapshot = {
#         "rpm": rpm,
#         "fuel_trim": f"{fuel_trim}%",
#         "coolant_temp": f"{temp}°F"
#     }
    
#     st.write("### Current Car State:")
#     st.json({"codes": selected_dtcs, "sensors": sensor_snapshot})

# # --- Main Chat Interface ---

# # Initialize Session State
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "app" not in st.session_state:
#     st.session_state.app = build_app()

# # Display Chat History
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Handle User Input
# # if prompt := st.chat_input("Describe the problem (e.g., 'My car is shaking')..."):
# #     # 1. Display User Message
# #     st.session_state.messages.append({"role": "user", "content": prompt})
# #     with st.chat_message("user"):
# #         st.markdown(prompt)

# #     # 2. Prepare the State for the Agents
# #     # We inject the sidebar data so the agents can "read" the car
# #     initial_state = {
# #         "messages": [prompt],
# #         "user_complaint": prompt,
# #         "dtc_codes": selected_dtcs,
# #         "sensor_data": sensor_snapshot,
# #         # Initialize empty fields
# #         "root_causes": [],
# #         "repair_plan": {},
# #         "next_step": ""
# #     }

# #     # 3. Run the Agent Graph
# #     with st.chat_message("assistant"):
# #         message_placeholder = st.empty()
# #         full_response = ""
        
# #         # We use a status container to show the "Thinking" process
# #         with st.status("🤖 AI Agents working...", expanded=True) as status:
# #             app = st.session_state.app
            
# #             try:
# #                 # Stream events from LangGraph
# #                 for event in app.stream(initial_state):
# #                     for key, value in event.items():
                        
# #                         # Service Advisor Log
# #                         if key == "advisor":
# #                             if value.get("next_step") == "ask_user":
# #                                 status.write("❌ Advisor: Need more info.")
# #                                 full_response = value["messages"][0]
# #                             else:
# #                                 status.write("✅ Advisor: Data complete. Handing off to Diagnostics...")
                        
# #                         # Diagnostic Log
# #                         elif key == "diagnostic":
# #                             causes = value.get("root_causes", [])
# #                             if causes:
# #                                 top_cause = causes[0].get('root_cause', 'Unknown')
# #                                 status.write(f"🔧 Diagnostician: Identified root cause -> **{top_cause}**")
                        
# #                         # Repair Log
# #                         elif key == "repair":
# #                             status.write("🛠️ Technician: Drafting repair plan...")
# #                             full_response = value["messages"][0]

# #                 status.update(label="Response Ready!", state="complete", expanded=False)
                
# #                 # Show Final Output
# #                 message_placeholder.markdown(full_response)
# #                 st.session_state.messages.append({"role": "assistant", "content": full_response})
                
# #             except Exception as e:
# #                 st.error(f"An error occurred: {e}")

# # --- PASTE THIS NEW BLOCK ---
# if prompt := st.chat_input("Describe the problem..."):
#     # 1. Show User Message
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 2. Get Response from LangFlow
#     with st.chat_message("assistant"):
#         with st.spinner("🤖 Consulting LangFlow Agent..."):
            
#             # Combine the user prompt with the sidebar codes
#             full_context = f"{prompt}. (Active DTC Codes: {selected_dtcs})"
            
#             # Call our new function
#             ai_response = run_langflow(full_context)
            
#             st.markdown(ai_response)
#             st.session_state.messages.append({"role": "assistant", "content": ai_response})


# # import streamlit as st
# # from src.langflow_client import run_flow

# # # --- Page Config ---
# # st.set_page_config(
# #     page_title="AI Mechanic Pro",
# #     page_icon="🔧",
# #     layout="centered"
# # )

# # # --- Header ---
# # st.title("🔧 AI Mechanic: Powertrain Specialist")
# # st.markdown("Enter a **DTC Code** (e.g., P0010) to get a full diagnosis from the manual.")

# # # --- Sidebar ---
# # with st.sidebar:
# #     st.header("⚙️ Diagnostics Panel")
# #     st.info(
# #         "This agent is connected to a vector database containing "
# #         "hundreds of powertrain diagnostic codes."
# #     )
# #     if st.button("🗑️ Clear Chat History"):
# #         st.session_state.messages = []
# #         st.rerun()
    
# #     st.markdown("---")
# #     st.caption("Powered by LangFlow & Astra DB")

# # # --- Session State (Memory) ---
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []

# # # --- Display Chat History ---
# # for message in st.session_state.messages:
# #     with st.chat_message(message["role"]):
# #         st.markdown(message["content"])

# # # --- User Input ---
# # if prompt := st.chat_input("Enter a trouble code (e.g., P0010)..."):
# #     # 1. Display User Message
# #     with st.chat_message("user"):
# #         st.markdown(prompt)
# #     st.session_state.messages.append({"role": "user", "content": prompt})

# #     # 2. Get AI Response
# #     with st.chat_message("assistant"):
# #         message_placeholder = st.empty()
# #         message_placeholder.markdown("🔍 *Scanning technical manuals...*")
        
# #         try:
# #             # Call the backend
# #             response = run_flow(prompt)
            
# #             # Parse the response safely
# #             if "outputs" in response:
# #                 final_answer = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
# #             else:
# #                 final_answer = "⚠️ System Error: " + str(response)

# #             message_placeholder.markdown(final_answer)
# #             st.session_state.messages.append({"role": "assistant", "content": final_answer})
            
# #         except Exception as e:
# #             message_placeholder.error(f"⚠️ Connection Error: {e}")



# import streamlit as st
# import os
# from src.agents.advisor import build_advisor_agent

# # 1. Page Config
# st.set_page_config(
#     page_title="Vehicle Diagnostic AI",
#     page_icon="🚗",
#     layout="wide"
# )

# # 2. Title & Sidebar
# st.title("🚗 AI Mechanic Advisor")
# st.markdown("---")

# with st.sidebar:
#     st.header("🔧 Diagnostic Tools")
#     st.info("System Ready")
#     st.markdown("""
#     **Active Capabilities:**
#     - 🌍 **Web Search:** Recalls & Forums
#     - 📖 **RAG Manuals:** AstraDB Search
#     - 📂 **Local Files:** Service Log Reader
#     """)
    
#     if st.button("Clear Chat History"):
#         st.session_state.messages = []
#         st.rerun()

# # 3. Initialize Agent (Only once per session)
# if "agent_executor" not in st.session_state:
#     with st.spinner("Initializing AI Mechanic..."):
#         st.session_state.agent_executor = build_advisor_agent()

# # 4. Initialize Chat History
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # 5. Display Chat History
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # 6. Handle User Input
# if prompt := st.chat_input("Describe the issue (e.g., 'What is code P0300?')..."):
#     # Add User Message to UI
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Generate Response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("⚙️ *Analyzing...*")
        
#         try:
#             # Call the Agent
#             response = st.session_state.agent_executor.invoke({"input": prompt})
#             full_response = response["output"]
            
#             # Update UI
#             message_placeholder.markdown(full_response)
#             st.session_state.messages.append({"role": "assistant", "content": full_response})
        
#         except Exception as e:
#             message_placeholder.error(f"Error: {str(e)}")


# import streamlit as st
# import os
# import uuid
# import time
# from google.api_core.exceptions import ResourceExhausted
# from src.agents.advisor import build_advisor_agent

# # 1. Page Config
# st.set_page_config(page_title="Vehicle Diagnostic AI", page_icon="🚗", layout="wide")

# # 2. Styles
# st.markdown("""
# <style>
#     .stChatMessage { padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
#     .stButton button { width: 100%; border-radius: 5px; }
# </style>
# """, unsafe_allow_html=True)

# # 3. Sidebar
# with st.sidebar:
#     st.title("🚗 AI Mechanic")
#     st.markdown("---")
    
#     st.success("✅ System Online")
#     st.info("🧠 Brain: Gemini 2.5 Flash")
    
#     st.markdown("### 📸 Vision Diagnostics")
#     uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
#     analyze_clicked = False
    
#     if uploaded_file:
#         save_dir = "data/uploaded_images"
#         if not os.path.exists(save_dir):
#             os.makedirs(save_dir)
#         save_path = os.path.join(save_dir, uploaded_file.name)
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         st.image(uploaded_file, caption="Preview", use_container_width=True)
        
#         if st.button("🔍 Analyze Image"):
#             analyze_clicked = True
#             image_prompt = f"Analyze the image located at {save_path} and tell me what is wrong."

#     st.markdown("---")
#     if st.button("🗑️ Clear History"):
#         st.session_state.messages = []
#         st.session_state.session_id = str(uuid.uuid4()) # Reset Agent Memory
#         st.rerun()

# # 4. Initialize Session & Agent
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())

# if "agent_executor" not in st.session_state:
#     with st.spinner("Initializing Mechanic Agent..."):
#         st.session_state.agent_executor = build_advisor_agent()

# # 5. Initialize Chat History (UI)
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I am your AI Mechanic. I remember our conversation. Tell me your car model first!"}
#     ]

# # 6. Display Chat
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # 7. Handle Inputs
# user_input = st.chat_input("Describe the issue (e.g., 'What is code P0300?')...")

# if user_input or analyze_clicked:
#     prompt = image_prompt if analyze_clicked else user_input
    
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("⚙️ *Thinking...*")
        
#         try:
#             # RETRY LOGIC
#             max_retries = 3
#             for attempt in range(max_retries):
#                 try:
#                     # PASS SESSION ID TO AGENT
#                     response = st.session_state.agent_executor.invoke(
#                         {"input": prompt},
#                         config={"configurable": {"session_id": st.session_state.session_id}}
#                     )
#                     full_response = response["output"]
                    
#                     message_placeholder.markdown(full_response)
#                     st.session_state.messages.append({"role": "assistant", "content": full_response})
#                     break 
                    
#                 except ResourceExhausted:
#                     if attempt < max_retries - 1:
#                         wait_time = 10
#                         message_placeholder.warning(f"⚠️ High traffic. Retrying in {wait_time} seconds...")
#                         time.sleep(wait_time)
#                     else:
#                         message_placeholder.error("Error: Daily quota exceeded. Please try again tomorrow.")
                        
#         except Exception as e:
#             message_placeholder.error(f"Error: {str(e)}")
            
#     if analyze_clicked:
#         st.rerun()


import streamlit as st
from dotenv import load_dotenv # IMPORT THIS
load_dotenv()                 # LOAD THE ENV VARIABLES

import os
import uuid
import time
from google.api_core.exceptions import ResourceExhausted
from src.agents.advisor import build_advisor_agent

# 1. Page Config
st.set_page_config(page_title="Vehicle Diagnostic AI", page_icon="🚗", layout="wide")

# 2. Styles
st.markdown("""
<style>
    .stChatMessage { padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
    .stButton button { width: 100%; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# 3. Initialize Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Mechanic. I remember our conversation. Tell me your car model first!"}
    ]

# 4. Sidebar & Tools
with st.sidebar:
    st.title("🚗 AI Mechanic")
    st.markdown("---")
    
    st.success("✅ System Online")
    st.info("🧠 Brain: Gemini 2.5 Flash")
    
    # --- Vision Diagnostics ---
    st.markdown("### 📸 Vision Diagnostics")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
    # Logic to handle image upload and analysis
    image_prompt = None
    analyze_clicked = False
    
    if uploaded_file:
        save_dir = "data/uploaded_images"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Save file locally
        save_path = os.path.join(save_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # FIX: Normalize path to use forward slashes (prevents Windows errors)
        ai_safe_path = save_path.replace("\\", "/")
            
        st.image(uploaded_file, caption="Preview", use_container_width=True)
        
        if st.button("🔍 Analyze Image"):
            analyze_clicked = True
            image_prompt = f"Analyze the image located at {ai_safe_path} and tell me what is wrong."

    st.markdown("---")
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4()) # Reset Agent Memory
        st.rerun()

# 5. Initialize Agent (With Error Check)
if "agent_executor" not in st.session_state:
    with st.spinner("Initializing Mechanic Agent..."):
        # The .env vars are now loaded, so this should work!
        agent = build_advisor_agent()
        
        if agent is None:
            st.error("❌ Critical Error: The Agent failed to start.")
            st.warning("Please check your .env file. Ensure there are NO spaces around the '=' sign (e.g., KEY=VALUE).")
            st.stop()
            
        st.session_state.agent_executor = agent

# 6. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 7. Handle User Input (Text OR Image)
user_input = st.chat_input("Describe the issue (e.g., 'What is code P0300?')...")

# Determine if we have a prompt to process
prompt_to_process = None

if analyze_clicked and image_prompt:
    prompt_to_process = image_prompt
elif user_input:
    prompt_to_process = user_input

# Process the prompt if it exists
if prompt_to_process:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⚙️ *Thinking...*")
        
        try:
            # RETRY LOGIC for Rate Limits
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    # Invoke Agent with Session ID
                    response = st.session_state.agent_executor.invoke(
                        {"input": prompt_to_process},
                        config={"configurable": {"session_id": st.session_state.session_id}}
                    )
                    full_response = response["output"]
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    success = True
                    break 
                    
                except ResourceExhausted:
                    if attempt < max_retries - 1:
                        wait_time = 5 * (attempt + 1)
                        message_placeholder.warning(f"⚠️ High traffic. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        message_placeholder.error("Error: Daily quota exceeded. Please try again tomorrow.")
                except Exception as e:
                    # Catch other errors immediately
                    message_placeholder.error(f"Error: {str(e)}")
                    success = True # Stop retrying on non-quota errors
                    break
            
            if not success and not message_placeholder:
                message_placeholder.error("Failed to get a response after retries.")

        except Exception as e:
            message_placeholder.error(f"System Error: {str(e)}")
            
    # Rerun to update state if it was an image analysis
    if analyze_clicked:
        st.rerun()