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



# import streamlit as st
# from dotenv import load_dotenv # IMPORT THIS
# load_dotenv()                 # LOAD THE ENV VARIABLES

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

# # 3. Initialize Session State
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())

# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I am your AI Mechanic. I remember our conversation. Tell me your car model first!"}
#     ]

# # 4. Sidebar & Tools
# with st.sidebar:
#     st.title("🚗 AI Mechanic")
#     st.markdown("---")
    
#     st.success("✅ System Online")
#     st.info("🧠 Brain: Gemini 2.5 Flash")
    
#     # --- Vision Diagnostics ---
#     st.markdown("### 📸 Vision Diagnostics")
#     uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    
#     # Logic to handle image upload and analysis
#     image_prompt = None
#     analyze_clicked = False
    
#     if uploaded_file:
#         save_dir = "data/uploaded_images"
#         if not os.path.exists(save_dir):
#             os.makedirs(save_dir)
            
#         # Save file locally
#         save_path = os.path.join(save_dir, uploaded_file.name)
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
            
#         # FIX: Normalize path to use forward slashes (prevents Windows errors)
#         ai_safe_path = save_path.replace("\\", "/")
            
#         st.image(uploaded_file, caption="Preview", use_container_width=True)
        
#         if st.button("🔍 Analyze Image"):
#             analyze_clicked = True
#             image_prompt = f"Analyze the image located at {ai_safe_path} and tell me what is wrong."

#     st.markdown("---")
#     if st.button("🗑️ Clear History"):
#         st.session_state.messages = []
#         st.session_state.session_id = str(uuid.uuid4()) # Reset Agent Memory
#         st.rerun()

# # 5. Initialize Agent (With Error Check)
# if "agent_executor" not in st.session_state:
#     with st.spinner("Initializing Mechanic Agent..."):
#         # The .env vars are now loaded, so this should work!
#         agent = build_advisor_agent()
        
#         if agent is None:
#             st.error("❌ Critical Error: The Agent failed to start.")
#             st.warning("Please check your .env file. Ensure there are NO spaces around the '=' sign (e.g., KEY=VALUE).")
#             st.stop()
            
#         st.session_state.agent_executor = agent

# # 6. Display Chat History
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # 7. Handle User Input (Text OR Image)
# user_input = st.chat_input("Describe the issue (e.g., 'What is code P0300?')...")

# # Determine if we have a prompt to process
# prompt_to_process = None

# if analyze_clicked and image_prompt:
#     prompt_to_process = image_prompt
# elif user_input:
#     prompt_to_process = user_input

# # Process the prompt if it exists
# if prompt_to_process:
#     # Append User Message
#     st.session_state.messages.append({"role": "user", "content": prompt_to_process})
#     with st.chat_message("user"):
#         st.markdown(prompt_to_process)

#     # Generate Response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("⚙️ *Thinking...*")
        
#         try:
#             # RETRY LOGIC for Rate Limits
#             max_retries = 3
#             success = False
            
#             for attempt in range(max_retries):
#                 try:
#                     # Invoke Agent with Session ID
#                     response = st.session_state.agent_executor.invoke(
#                         {"input": prompt_to_process},
#                         config={"configurable": {"session_id": st.session_state.session_id}}
#                     )
#                     full_response = response["output"]
                    
#                     message_placeholder.markdown(full_response)
#                     st.session_state.messages.append({"role": "assistant", "content": full_response})
#                     success = True
#                     break 
                    
#                 except ResourceExhausted:
#                     if attempt < max_retries - 1:
#                         wait_time = 5 * (attempt + 1)
#                         message_placeholder.warning(f"⚠️ High traffic. Retrying in {wait_time} seconds...")
#                         time.sleep(wait_time)
#                     else:
#                         message_placeholder.error("Error: Daily quota exceeded. Please try again tomorrow.")
#                 except Exception as e:
#                     # Catch other errors immediately
#                     message_placeholder.error(f"Error: {str(e)}")
#                     success = True # Stop retrying on non-quota errors
#                     break
            
#             if not success and not message_placeholder:
#                 message_placeholder.error("Failed to get a response after retries.")

#         except Exception as e:
#             message_placeholder.error(f"System Error: {str(e)}")
            
#     # Rerun to update state if it was an image analysis
#     if analyze_clicked:
#         st.rerun()





# import streamlit as st
# from dotenv import load_dotenv
# load_dotenv() # Load environment variables first

# import os
# import uuid
# import time
# import json  # Added json import for the fix
# from google.api_core.exceptions import ResourceExhausted

# # LangChain Imports for PDF Ingestion
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from src.rag.retriever import get_vectorstore
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

# # 3. Helper: Ingest PDF Function
# def ingest_pdf(file_path):
#     """Reads a PDF, splits it, and saves it to AstraDB."""
#     try:
#         # 1. Load PDF
#         loader = PyPDFLoader(file_path)
#         pages = loader.load()
        
#         # 2. Split Text
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = text_splitter.split_documents(pages)
        
#         # 3. Add to Vector Database
#         vstore = get_vectorstore()
#         if vstore:
#             vstore.add_documents(chunks)
#             return True, f"Successfully ingested {len(chunks)} chunks!"
#         else:
#             return False, "Database connection failed."
            
#     except Exception as e:
#         return False, str(e)

# # 4. Initialize Session
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())

# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Hello! I am your AI Mechanic. I remember our conversation. Tell me your car model first!"}
#     ]

# # 5. Sidebar & Tools
# with st.sidebar:
#     st.title("🚗 AI Mechanic")
#     st.markdown("---")
    
#     st.success("✅ System Online")
    
#     # --- SECTION A: Developer Controls (NEW) ---
#     st.markdown("### ⚙️ Output Controls")
#     json_mode = st.checkbox("💻 JSON Mode (Developer)", help="Force the AI to output structured JSON data instead of text.")

#     # --- SECTION B: Sensor Data (NEW) ---
#     with st.expander("📊 Live Sensor Data"):
#         st.caption("Input Freeze Frame / Live Data")
#         rpm = st.number_input("Engine RPM", min_value=0, max_value=8000, value=0, step=100)
#         load = st.slider("Engine Load (%)", 0, 100, 0)
#         temp = st.number_input("Coolant Temp (°F)", value=190)
#         fuel_trim = st.number_input("Long Term Fuel Trim (%)", value=0.0)
        
#         sensor_context = f"""
#         [LIVE SENSOR DATA]
#         - RPM: {rpm}
#         - Load: {load}%
#         - Coolant Temp: {temp}°F
#         - Fuel Trim: {fuel_trim}%
#         """

#     # --- SECTION C: Knowledge Base ---
#     with st.expander("📚 Knowledge Base"):
#         st.caption("Upload Service Manuals (PDF)")
#         uploaded_manual = st.file_uploader("Upload Manual", type="pdf")
        
#         if uploaded_manual and st.button("📥 Ingest Manual"):
#             with st.spinner("Processing PDF..."):
#                 save_dir = "data/manuals"
#                 if not os.path.exists(save_dir):
#                     os.makedirs(save_dir)
#                 manual_path = os.path.join(save_dir, uploaded_manual.name)
                
#                 with open(manual_path, "wb") as f:
#                     f.write(uploaded_manual.getbuffer())
                
#                 success, msg = ingest_pdf(manual_path)
#                 if success:
#                     st.success(msg)
#                 else:
#                     st.error(f"Error: {msg}")

#     # --- SECTION D: Vision Diagnostics ---
#     st.markdown("### 📸 Vision Diagnostics")
#     uploaded_file = st.file_uploader("Upload Car Image", type=["jpg", "png", "jpeg"])
    
#     image_prompt = None
#     analyze_clicked = False
    
#     if uploaded_file:
#         img_dir = "data/uploaded_images"
#         if not os.path.exists(img_dir):
#             os.makedirs(img_dir)
#         save_path = os.path.join(img_dir, uploaded_file.name)
        
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
            
#         ai_safe_path = save_path.replace("\\", "/")
#         st.image(uploaded_file, caption="Preview", use_container_width=True)
        
#         if st.button("🔍 Analyze Image"):
#             analyze_clicked = True
#             image_prompt = f"Analyze the image located at {ai_safe_path} and tell me what is wrong."

#     st.markdown("---")
#     if st.button("🗑️ Clear History"):
#         st.session_state.messages = []
#         st.session_state.session_id = str(uuid.uuid4())
#         st.rerun()

# # 6. Initialize Agent
# if "agent_executor" not in st.session_state:
#     with st.spinner("Initializing Mechanic Agent..."):
#         agent = build_advisor_agent()
#         if agent is None:
#             st.error("❌ Critical Error: The Agent failed to start. Check .env file.")
#             st.stop()
#         st.session_state.agent_executor = agent

# # 7. Chat Interface
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         if isinstance(message["content"], (dict, list)):
#             st.json(message["content"]) # Render stored JSON history correctly
#         else:
#             st.markdown(message["content"])

# # 8. Handle Input
# user_input = st.chat_input("Describe the issue (e.g., 'P0300 code')...")

# # Determine prompt source
# prompt_to_process = image_prompt if (analyze_clicked and image_prompt) else user_input

# if prompt_to_process:
#     # Construct the final prompt with Context
#     full_prompt = f"{prompt_to_process}\n\n{sensor_context}"
    
#     if json_mode:
#         full_prompt += """
#         \n\nCRITICAL: Output your answer ONLY as a valid JSON object. 
#         Format:
#         {
#           "root_causes": [{"cause": "string", "confidence_score": 0.0-1.0}],
#           "recommended_fix": "string",
#           "estimated_labor_hours": float,
#           "parts_required": ["list", "of", "parts"]
#         }
#         """

#     # Display User Message (Clean version)
#     st.session_state.messages.append({"role": "user", "content": prompt_to_process})
#     with st.chat_message("user"):
#         st.markdown(prompt_to_process)
#         if rpm > 0 or load > 0: # Only show sensor data if it's not default
#             with st.expander("Attached Sensor Data"):
#                 st.code(sensor_context)

#     # Generate Response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("⚙️ *Thinking...*")
        
#         try:
#             # Auto-Retry Loop
#             max_retries = 3
#             success = False
#             for attempt in range(max_retries):
#                 try:
#                     response = st.session_state.agent_executor.invoke(
#                         {"input": full_prompt},
#                         config={"configurable": {"session_id": st.session_state.session_id}}
#                     )
#                     full_response = response["output"]
                    
#                     # --- JSON FIX START ---
#                     if json_mode:
#                         # Clean the markdown formatting (```json and ```) from the string
#                         cleaned_response = full_response.replace("```json", "").replace("```", "").strip()
                        
#                         try:
#                             # Parse the string into a real Python dictionary
#                             json_data = json.loads(cleaned_response)
#                             # Display it as a pretty interactive JSON object
#                             message_placeholder.json(json_data)
#                             # Save the OBJECT, not the string, to history
#                             st.session_state.messages.append({"role": "assistant", "content": json_data})
#                         except json.JSONDecodeError:
#                             # Fallback: If parsing fails, just show the raw code
#                             message_placeholder.code(full_response, language='json')
#                             st.error("⚠️ Agent returned invalid JSON. Raw output shown above.")
#                             st.session_state.messages.append({"role": "assistant", "content": full_response})
#                     # --- JSON FIX END ---
#                     else:
#                         message_placeholder.markdown(full_response)
#                         st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
#                     success = True
#                     break 
#                 except ResourceExhausted:
#                     wait_time = 5 * (attempt + 1)
#                     message_placeholder.warning(f"⚠️ High traffic. Retrying in {wait_time}s...")
#                     time.sleep(wait_time)
#                 except Exception as e:
#                     message_placeholder.error(f"Error: {str(e)}")
#                     success = True
#                     break
            
#             if not success:
#                 message_placeholder.error("System busy. Please try again.")

#         except Exception as e:
#             message_placeholder.error(f"System Error: {str(e)}")
            
#     if analyze_clicked:
#         st.rerun()




# import streamlit as st
# import time
# from dotenv import load_dotenv
# import os
# import sys

# # Ensure src module is found
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Import the Agent Executor from your backend
# from src.agents.advisor import agent_executor

# # Load environment variables
# load_dotenv()

# # --- PAGE CONFIG ---
# st.set_page_config(
#     page_title="AI Vehicle Diagnostic Agent",
#     page_icon="🚗",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --- CUSTOM CSS ---
# st.markdown("""
# <style>
#     .stChatMessage { border-radius: 10px; padding: 10px; }
#     .stButton button { width: 100%; border-radius: 5px; }
#     .reportview-container { background: #f0f2f6; }
# </style>
# """, unsafe_allow_html=True)

# # --- SIDEBAR: SENSOR DATA SIMULATOR ---
# with st.sidebar:
#     st.image("https://cdn-icons-png.flaticon.com/512/3209/3209995.png", width=80)
#     st.title("🔌 OBD-II Simulator")
#     st.info("Adjust sensor values to simulate vehicle conditions.")

#     # Vehicle Selector
#     car_model = st.selectbox(
#         "Vehicle Model",
#         ["Tata Nexon", "Ford F-150", "Mahindra XUV700", "Hyundai Creta", "Chevy Silverado"]
#     )
    
#     st.divider()
    
#     # Sensor Sliders
#     rpm = st.slider("Engine RPM", 0, 8000, 2000, help="Normal idle is ~800. High RPM at idle suggests issues.")
#     speed = st.slider("Vehicle Speed (km/h)", 0, 220, 45)
#     load = st.slider("Engine Load (%)", 0, 100, 40, help="High load at low speed can trigger DPF issues.")
#     temp = st.slider("Coolant Temp (°C)", 50, 130, 90, help="Over 110°C is overheating.")
    
#     st.divider()
    
#     # Active DTCs
#     dtc_input = st.text_input("Active DTC Code (Optional)", placeholder="e.g. P2463")

# # --- MAIN CHAT INTERFACE ---
# st.title("🚗 AI Senior Diagnostic Judge")
# st.markdown(f"**Connected Vehicle:** {car_model} | **Status:** Connected")

# # Initialize Chat History
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display Chat History
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Chat Input
# if prompt := st.chat_input("Describe the symptoms (e.g., 'Black smoke and loss of power')..."):
    
#     # 1. User Message
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 2. Construct Full Context for Agent
#     # We combine the manual text input with the sidebar sensor data
#     full_context = f"""
#     Vehicle: {car_model}
#     Sensors: RPM={rpm}, Speed={speed}, Load={load}%, Temp={temp}C
#     Active DTC: {dtc_input if dtc_input else 'None'}
#     User Complaint: {prompt}
#     """

#     # 3. Agent Response
#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         message_placeholder.markdown("⚙️ *Analyzing sensor data and consulting manuals...*")
        
#         try:
#             # Call the Agent
#             start_time = time.time()
#             response = agent_executor.invoke({"input": full_context})
#             end_time = time.time()
            
#             # Extract Output
#             agent_output = response['output']
            
#             # Display Final Result
#             message_placeholder.markdown(agent_output)
            
#             # Add Metrics below the response
#             st.caption(f"⏱️ Analysis completed in {end_time - start_time:.2f}s")
            
#             # Save to History
#             st.session_state.messages.append({"role": "assistant", "content": agent_output})
            
#         except Exception as e:
#             message_placeholder.error(f"❌ System Error: {str(e)}")



# import streamlit as st
# import time
# import os
# import sys
# import json
# from dotenv import load_dotenv

# # Ensure we can import from src
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Import your Agent
# try:
#     from src.agents.advisor import agent_executor
# except ImportError as e:
#     st.error(f"❌ Critical Import Error: {e}")
#     st.stop()

# load_dotenv()
    
# # --- PAGE CONFIGURATION ---
# st.set_page_config(
#     page_title="AI Vehicle Diagnostic Judge",
#     page_icon="🚗",
#     layout="wide"
# )

# # Add this right after st.set_page_config...
# if st.sidebar.button("HARD RESET (Nuke Cache)"):
#     st.session_state.clear()
#     st.cache_data.clear()
#     st.rerun()

# # --- SIDEBAR: SENSOR INPUTS ---
# with st.sidebar:
#     st.title("🔌 OBD-II Simulator")
#     st.markdown("---")
    
#     # Context Inputs
#     car_model = st.selectbox("Car Model", ["Tata Nexon", "Ford F-150", "Mahindra XUV700", "Hyundai Creta", "Chevy Silverado"])
#     dtc_code = st.text_input("Active DTC (Optional)", value="P2463")
    
#     st.subheader("Live Sensor Data")
#     rpm = st.slider("Engine RPM", 0, 8000, 2200)
#     speed = st.slider("Speed (km/h)", 0, 220, 40)
#     load = st.slider("Engine Load (%)", 0, 100, 90)
#     temp = st.slider("Coolant Temp (°C)", 0, 130, 90)

#     # --- NEW: RESET BUTTON ---
#     st.markdown("---")
#     if st.button("🗑️ Clear Chat History", type="primary"):
#         st.session_state.messages = []
#         st.rerun()

# # --- MAIN CHAT INTERFACE ---
# st.title("🚗 AI Senior Diagnostic Judge")
# st.caption("Consensus Engine: XGBoost (ML) + AstraDB (RAG) + Tavily (Web)")

# # Initialize Chat History
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # Display History
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # Handle User Input
# if prompt := st.chat_input("Describe the issue (e.g., 'Limp mode active, black smoke')"):
    
#     # 1. Show User Message
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 2. Prepare Context for Agent
#     full_query = f"""
#     Vehicle: {car_model}
#     DTC: {dtc_code}
#     Sensors: RPM={rpm}, Speed={speed}, Load={load}%, Temp={temp}C.
#     User Complaint: {prompt}
#     """

#     # 3. Generate Response with Debugger
#     with st.chat_message("assistant"):
#         # Visual Debugger / Status Indicator
#         with st.status("🕵️ Agent is investigating...", expanded=True) as status:
#             try:
#                 st.write("📡 Running Tier 1: ML Root Cause Analysis...")
                
#                 start_time = time.time()
#                 # Run the Agent
#                 response = agent_executor.invoke({"input": full_query})
#                 duration = time.time() - start_time
                
#                 st.write("📖 Tier 2: Consulting Technical Manuals (RAG)...")
#                 st.write("🌐 Tier 2: Searching Web Forums & TSBs...")
#                 st.write("⚖️ Tier 3: Calculating Consensus Verdict...")
                
#                 status.update(label=f"✅ Analysis Complete ({duration:.2f}s)", state="complete", expanded=False)
                
#                 final_answer = response['output']
                
#                 # Display Final Result
#                 st.markdown(final_answer)
                
#                 # Save to History
#                 st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
#             except Exception as e:
#                 status.update(label="❌ Investigation Failed", state="error")
#                 st.error(f"**System Error:** {str(e)}")
#                 if "Name cannot be empty" in str(e):
#                     st.info("💡 **Fix Found:** Your `web_search.py` is returning a List. It MUST return a `json.dumps()` string.")






# import streamlit as st
# import time
# import os
# import sys
# from dotenv import load_dotenv

# # Langchain imports for Triage & Validation
# from langchain_core.exceptions import OutputParserException
# from langchain.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import BaseModel, Field
# from langchain.output_parsers import PydanticOutputParser

# # Ensure we can import from src
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# # Load environment variables FIRST
# load_dotenv()

# # Import the main Agent and the Parser
# try:
#     from src.agents.advisor import agent_executor, parser
# except ImportError as e:
#     st.error(f"❌ Critical Import Error: {e}")
#     st.stop()

# # ==========================================
# # 1. SMART GATEKEEPER (Context-Aware Triage)
# # ==========================================
# class GatekeeperResponse(BaseModel):
#     is_valid: bool = Field(description="True if the prompt has enough technical detail to diagnose. False if too generic.")
#     clarifying_questions: str = Field(description="If False, provide 2-3 specific technical questions related to the complaint. If True, write 'None'.")

# gatekeeper_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)

# gatekeeper_prompt = PromptTemplate(
#     template="""
#     You are a Master Technician Triage AI. A mechanic has submitted a diagnostic request.
#     This system is designed for COMPLEX tasks. 
    
#     If the mechanic's input is generic (e.g., "car shakes", "lacks power") without accompanying OBD-II data, DTCs, or deep mechanical context, you must reject it.
    
#     CRITICAL: If you reject it, DO NOT just ask for a DTC. You must deduce the possible systems involved and ask for SPECIFIC data parameters. 
#     (Example: For 'sluggish acceleration', ask for Differential Pressure, Fuel Trims, or active DTCs.)
    
#     Mechanic Input: {input}
    
#     {format_instructions}
#     """,
#     input_variables=["input"],
#     partial_variables={"format_instructions": gatekeeper_parser.get_format_instructions()}
# )

# # Using the requested gemini-2.5-flash for speed
# gatekeeper_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
# gatekeeper_chain = gatekeeper_prompt | gatekeeper_llm | gatekeeper_parser


# # ==========================================
# # 2. STREAMLIT UI SETUP 
# # ==========================================
# st.set_page_config(page_title="AI Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")

# # Updated Sidebar: Just Hard Reset
# with st.sidebar:
#     if st.button("🚨 HARD RESET (Nuke Cache)"):
#         st.session_state.clear()
#         st.cache_data.clear()
#         st.rerun()

# # --- MAIN CHAT INTERFACE ---
# st.title("🚗 AI Senior Diagnostic Judge")
# st.caption("Configured for Complex Diagnostics | ML + AstraDB (RAG) + Web Search")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ==========================================
# # 3. EXECUTION LOGIC
# # ==========================================
# if user_text := st.chat_input("Enter detailed mechanic notes here (Vehicle, DTCs, Symptoms)..."):
    
#     st.session_state.messages.append({"role": "user", "content": user_text})
#     with st.chat_message("user"):
#         st.markdown(user_text)

#     with st.chat_message("assistant"):
#         with st.status("🚦 Triage in progress...", expanded=True) as status:
#             try:
#                 # --- BACKEND LOGGING: TRIAGE START ---
#                 print("\n" + "="*60)
#                 print("🧠 [BACKEND LOG] GATEKEEPER TRIAGE INITIATED")
#                 print(f"📥 RAW INPUT: {user_text}")

#                 # Run Triage
#                 triage_result = gatekeeper_chain.invoke({"input": user_text})
                
#                 # --- BACKEND LOGGING: TRIAGE RESULTS ---
#                 print(f"🔎 IS VALID: {triage_result.is_valid}")
#                 if not triage_result.is_valid:
#                     print(f"⚠️ REASON/QUESTIONS GENERATED:\n{triage_result.clarifying_questions}")
#                 print("="*60 + "\n")

#                 if not triage_result.is_valid:
#                     status.update(label="⚠️ Needs More Technical Context", state="complete", expanded=False)
#                     st.warning("This issue requires more specific data to diagnose accurately without guessing.")
#                     st.info(f"**Diagnostic Next Steps:**\n{triage_result.clarifying_questions}")
                    
#                     st.session_state.messages.append({
#                         "role": "assistant", 
#                         "content": f"Please gather this data so I can assist further:\n{triage_result.clarifying_questions}"
#                     })
#                     st.stop()
                
#                 # --- STEP B: RUN MAIN AGENT ---
#                 status.update(label="✅ Triage Passed. Initiating Deep Scan...", state="running")
#                 start_time = time.time()
                
#                 chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:]])
#                 full_query = f"Recent Chat Context:\n{chat_history}\n\nCurrent Input:\n{user_text}"
                
#                 st.write("📡 Running ML, RAG, and Web Tiers...")
#                 response = agent_executor.invoke({"input": full_query})
#                 raw_output = response['output']
                
#                 try:
#                     # Final Validation of the combined output
#                     validated_data = parser.parse(raw_output)
#                     duration = time.time() - start_time
#                     status.update(label=f"✅ Analysis Complete ({duration:.2f}s)", state="complete", expanded=False)
                    
#                     st.markdown(f"### 🛑 Complex Diagnosis: {validated_data.diagnosis}")
#                     st.markdown(f"**Consensus Confidence:** {validated_data.confidence_level}")
                    
#                     if validated_data.safety_warning.lower() != "none":
#                         st.error(f"⚠️ **Safety Warning:** {validated_data.safety_warning}")
                    
#                     with st.expander("📊 View AI Evidence Sourcing (RAG/Web/ML)"):
#                         st.write("**ML Tool Findings:**", validated_data.ml_evidence)
#                         st.write("**Official Manuals (RAG):**", validated_data.rag_evidence)
#                         st.write("**Web Forums & TSBs:**", validated_data.web_evidence)
                    
#                     st.markdown("### 🛠️ Advanced Action Plan")
#                     for i, step in enumerate(validated_data.action_plan, 1):
#                         st.markdown(f"{i}. {step}")
                    
#                     st.session_state.messages.append({"role": "assistant", "content": f"**Diagnosis:** {validated_data.diagnosis}\n\n*See UI for full advanced action plan.*"})

#                 except OutputParserException:
#                     status.update(label="⚠️ Formatting Error by AI", state="complete", expanded=False)
#                     st.warning("Validation failed. Displaying raw response.")
#                     st.code(raw_output, language="json")

#             except Exception as e:
#                  status.update(label="❌ Investigation Failed", state="error")
#                  st.error(f"System Error: {str(e)}")


# import streamlit as st
# import time
# import os
# import sys
# from dotenv import load_dotenv

# from langchain_core.exceptions import OutputParserException
# from langchain.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import BaseModel, Field
# from langchain.output_parsers import PydanticOutputParser

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# load_dotenv()

# try:
#     from src.agents.advisor import agent_executor, parser
# except ImportError as e:
#     st.error(f"❌ Critical Import Error: {e}")
#     st.stop()

# # ==========================================
# # 1. SMART GATEKEEPER (Context-Aware Triage)
# # ==========================================
# class GatekeeperResponse(BaseModel):
#     is_valid: bool = Field(description="True if the prompt has enough technical detail (DTCs, specific UI sensor data, or complex mechanical context) to diagnose. False if it's too generic.")
#     clarifying_questions: str = Field(description="If False, provide 2-3 highly specific technical questions related to their complaint. If True, write 'None'.")

# gatekeeper_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)

# gatekeeper_prompt = PromptTemplate(
#     template="""
#     You are a Master Technician Triage AI. A mechanic has submitted a diagnostic request.
#     This system is designed for COMPLEX tasks. 
    
#     Evaluate the Combined Mechanic Input below. 
#     If they provide NO DTCs, NO abnormal UI sensor data, AND the text is generic (e.g., "car shakes", "makes noise"), you must reject it (`is_valid: False`).
    
#     CRITICAL: If you reject it, deduce the possible systems involved and ask for SPECIFIC data parameters. Do NOT just say "give me a code."
    
#     Combined Mechanic Input:
#     {input}
    
#     {format_instructions}
#     """,
#     input_variables=["input"],
#     partial_variables={"format_instructions": gatekeeper_parser.get_format_instructions()}
# )

# gatekeeper_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
# gatekeeper_chain = gatekeeper_prompt | gatekeeper_llm | gatekeeper_parser

# # ==========================================
# # 2. STREAMLIT UI SETUP (Comprehensive Intake)
# # ==========================================
# st.set_page_config(page_title="AI Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")

# # --- SIDEBAR: COMPREHENSIVE MECHANIC INTAKE FORM ---
# with st.sidebar:
#     if st.button("🚨 HARD RESET (Nuke Cache)"):
#         st.session_state.clear()
#         st.cache_data.clear()
#         st.rerun()

#     st.title("📋 Diagnostic Intake")
#     st.markdown("Fill out available data to assist the AI.")
    
#     car_model = st.selectbox("Vehicle", ["Tata Nexon", "Ford F-150", "Mahindra XUV700", "Hyundai Creta", "Chevy Silverado"])
#     dtc_code = st.text_input("Active/Pending DTCs", value="")
    
#     st.subheader("Optional UI Selections")
#     primary_symptom = st.selectbox("Primary Symptom", ["None Selected", "Engine Misfire", "Transmission Slip", "Limp Mode / Loss of Power", "Fluid Leak", "Abnormal Smoke", "Overheating", "Vibration/Noise", "No Start"])
#     operating_condition = st.selectbox("Occurs When?", ["None Selected", "Constant", "Cold Start", "Engine Warm", "Under Heavy Load", "At Highway Speeds", "While Braking", "At Idle"])
    
#     st.subheader("Live Freeze Frame Data")
#     rpm = st.slider("Engine RPM", 0, 8000, 2200)
#     speed = st.slider("Speed (km/h)", 0, 220, 40)
#     load = st.slider("Engine Load (%)", 0, 100, 90)
#     temp = st.slider("Coolant Temp (°C)", 0, 130, 90)

# # --- MAIN CHAT INTERFACE ---
# st.title("🚗 AI Senior Diagnostic Judge")
# st.caption("Configured for Complex Diagnostics | UI Routing + ML + RAG + Web")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ==========================================
# # 3. EXECUTION LOGIC
# # ==========================================
# if user_text := st.chat_input("Enter detailed mechanic notes here..."):
    
#     st.session_state.messages.append({"role": "user", "content": user_text})
#     with st.chat_message("user"):
#         st.markdown(user_text)

#     # ---> THIS IS WHERE UI AND TEXT MERGE <---
#     full_mechanic_input = f"""
#     Vehicle: {car_model}
#     DTCs: {dtc_code if dtc_code else 'None Provided'}
#     UI Selected Symptom: {primary_symptom}
#     Occurs During: {operating_condition}
#     Sensor Data: RPM={rpm}, Speed={speed}, Load={load}%, Temp={temp}C
#     Mechanic Notes: {user_text}
#     """

#     with st.chat_message("assistant"):
#         with st.status("🚦 Triage in progress...", expanded=True) as status:
#             try:
#                 # --- BACKEND LOGGING ---
#                 print("\n" + "="*60)
#                 print("🧠 [BACKEND LOG] GATEKEEPER INGESTION BLOCK:")
#                 print(full_mechanic_input)

#                 # --- STEP A: RUN SMART GATEKEEPER ---
#                 triage_result = gatekeeper_chain.invoke({"input": full_mechanic_input})
                
#                 print(f"🔎 IS VALID: {triage_result.is_valid}")
#                 if not triage_result.is_valid:
#                     print(f"⚠️ QUESTIONS GENERATED:\n{triage_result.clarifying_questions}")
#                 print("="*60 + "\n")

#                 if not triage_result.is_valid:
#                     status.update(label="⚠️ Needs More Technical Context", state="complete", expanded=False)
#                     st.warning("This issue requires more specific data to diagnose accurately without guessing.")
#                     st.info(f"**Diagnostic Next Steps:**\n{triage_result.clarifying_questions}")
                    
#                     st.session_state.messages.append({
#                         "role": "assistant", 
#                         "content": f"Please gather this data so I can assist further:\n{triage_result.clarifying_questions}"
#                     })
#                     st.stop() # THE FALLBACK - Stops execution
                
#                 # --- STEP B: RUN MAIN AGENT ---
#                 status.update(label="✅ Triage Passed. Initiating Deep Scan...", state="running")
#                 start_time = time.time()
                
#                 chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:]])
#                 full_query = f"Recent Chat Context:\n{chat_history}\n\nCurrent Input:\n{full_mechanic_input}"
                
#                 st.write("📡 Running ML, RAG, and Web Tiers...")
#                 response = agent_executor.invoke({"input": full_query})
#                 raw_output = response['output']
                
#                 try:
#                     # Final Validation Fallback
#                     validated_data = parser.parse(raw_output)
#                     duration = time.time() - start_time
#                     status.update(label=f"✅ Analysis Complete ({duration:.2f}s)", state="complete", expanded=False)
                    
#                     st.markdown(f"### 🛑 Complex Diagnosis: {validated_data.diagnosis}")
#                     st.markdown(f"**Consensus Confidence:** {validated_data.confidence_level}")
                    
#                     if validated_data.safety_warning.lower() != "none":
#                         st.error(f"⚠️ **Safety Warning:** {validated_data.safety_warning}")
                    
#                     with st.expander("📊 View AI Evidence Sourcing (RAG/Web/ML)"):
#                         st.write("**ML Tool Findings:**", validated_data.ml_evidence)
#                         st.write("**Official Manuals (RAG):**", validated_data.rag_evidence)
#                         st.write("**Web Forums & TSBs:**", validated_data.web_evidence)
                    
#                     st.markdown("### 🛠️ Advanced Action Plan")
#                     for i, step in enumerate(validated_data.action_plan, 1):
#                         st.markdown(f"{i}. {step}")
                    
#                     st.session_state.messages.append({"role": "assistant", "content": f"**Diagnosis:** {validated_data.diagnosis}\n\n*See UI for full advanced action plan.*"})

#                 except OutputParserException as e:
#                     status.update(label="⚠️ Formatting Error by AI", state="complete", expanded=False)
#                     st.warning("Validation failed. Displaying raw response.")
#                     st.code(raw_output, language="json")
#                     st.session_state.messages.append({"role": "assistant", "content": "⚠️ Formatting Failed."})

#             except Exception as e:
#                  status.update(label="❌ Investigation Failed", state="error")
#                  st.error(f"System Error: {str(e)}")


import streamlit as st
import time
import os
import sys
import json
import base64
from PIL import Image
from dotenv import load_dotenv

# Langchain and Pydantic imports
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

# Dynamic Searchbox import
try:
    from streamlit_searchbox import st_searchbox
except ImportError:
    st.error("Please install the searchbox component: pip install streamlit-searchbox")
    st.stop()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

try:
    from src.agents.advisor import agent_executor, parser
except ImportError as e:
    st.error(f"❌ Critical Import Error: {e}\nMake sure your src.agents module is accessible.")
    st.stop()

# ==========================================
# 0. INITIALIZE SESSION STATE (For Auto-Fill & Cache)
# ==========================================
if 'rpm_val' not in st.session_state: st.session_state.rpm_val = 2200
if 'speed_val' not in st.session_state: st.session_state.speed_val = 40
if 'load_val' not in st.session_state: st.session_state.load_val = 90
if 'temp_val' not in st.session_state: st.session_state.temp_val = 90
if 'dtc_val' not in st.session_state: st.session_state.dtc_val = ""

# NEW: Create an empty memory bank for vehicles to ensure zero-latency search
if 'vehicle_db' not in st.session_state: st.session_state.vehicle_db = set() 

# ==========================================
# 1. SMART GATEKEEPER & LLM SETUP
# ==========================================
llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

class GatekeeperResponse(BaseModel):
    is_valid: bool = Field(description="True if the prompt has enough technical detail OR is a direct request for a specific repair procedure. False if it's too generic.")
    clarifying_questions: str = Field(description="If False, provide 2-3 specific technical questions. If True, write 'None'.")
    ui_main_heading: str = Field(description="A 2-4 word contextual title for the main AI response based on what the user is asking. (e.g., 'Diagnostic Assessment', 'Repair Procedure', 'System Explanation')")
    ui_steps_heading: str = Field(description="A 2-4 word contextual title for the bulleted list. (e.g., 'Troubleshooting Steps', 'Replacement Guide', 'Next Steps')")

gatekeeper_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)

gatekeeper_prompt = PromptTemplate(
    template="""
    You are a Master Technician Triage AI. A mechanic has submitted a diagnostic request.
    
    Evaluate the Combined Mechanic Input below. 
    1. If they provide generic symptoms with no data, reject it (`is_valid: False`) and ask specific technical questions.
    2. If they provide specific data, DTCs, OR ask for a specific repair/explanation, accept it (`is_valid: True`).
    3. Look at what the user is asking and generate appropriate UI headings. If they ask "how to fix", the heading should be about Repair/Procedures, not Diagnosis.
    
    Combined Mechanic Input:
    {input}
    
    {format_instructions}
    """,
    input_variables=["input"],
    partial_variables={"format_instructions": gatekeeper_parser.get_format_instructions()}
)

gatekeeper_chain = gatekeeper_prompt | llm_flash | gatekeeper_parser

# --- SMART CACHE VEHICLE SEARCH FUNCTION ---
def search_vehicles(searchterm: str) -> list[str]:
    """Smart Cache Autocomplete: Learns and caches vehicles dynamically from the AI."""
    if not searchterm or len(searchterm) < 2:
        return []
        
    searchterm_lower = searchterm.lower()
    
    # 1. INSTANT MEMORY SEARCH: Check if we already fetched matching cars
    local_matches = [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()]
    
    # If we have matches in memory, return them instantly! (Zero latency)
    if len(local_matches) >= 5:
        return local_matches[:6] 
        
    # 2. DYNAMIC EXPANSION: If not in memory, ask the AI to fetch a large batch
    try:
        prompt = f"User is typing '{searchterm}' in a vehicle autocomplete box. Return a JSON array of exactly 15 real-world car Makes and Models that match or start with this text. Example: [\"{searchterm.title()} Model 1\"]. ONLY output the JSON array, no markdown."
        response = llm_flash.invoke(prompt)
        clean_response = response.content.replace('```json','').replace('```','').strip()
        new_suggestions = json.loads(clean_response)
        
        # Add these newly discovered cars to our session memory bank!
        st.session_state.vehicle_db.update(new_suggestions)
        
        # Re-filter memory to ensure exact matches
        updated_matches = [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()]
        
        return updated_matches[:6] if updated_matches else new_suggestions[:6]
    except Exception:
        return local_matches[:6] if local_matches else [searchterm]

# ==========================================
# 2. STREAMLIT UI SETUP 
# ==========================================
st.set_page_config(page_title="AI Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")

with st.sidebar:
    if st.button("🚨 HARD RESET (Nuke Cache)"):
        st.session_state.clear()
        st.cache_data.clear()
        st.rerun()

    st.title("📋 Diagnostic Intake")
    
    # --- VISION AUTO-FILL ---
    st.subheader("📸 Auto-Fill from Image")
    uploaded_image = st.file_uploader("Upload Scanner/Dashboard Photo", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        with st.spinner("Extracting data with Gemini Vision..."):
            try:
                image_bytes = uploaded_image.getvalue()
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                
                vision_msg = HumanMessage(
                    content=[
                        {"type": "text", "text": "Analyze this car dashboard or OBD-II scanner image. Extract the following values if visible: RPM, Speed (km/h), Engine Load (%), Coolant Temp (C), and any DTC codes (e.g., P0171). Output ONLY a raw JSON object with keys: 'rpm' (int), 'speed' (int), 'load' (int), 'temp' (int), 'dtc' (string). Use -1 for numbers if not visible, and empty string for dtc if not visible. No markdown formatting."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]
                )
                
                vision_response = llm_flash.invoke([vision_msg])
                extracted_data = json.loads(vision_response.content.replace('```json','').replace('```','').strip())
                
                if extracted_data.get('rpm') != -1: st.session_state.rpm_val = extracted_data['rpm']
                if extracted_data.get('speed') != -1: st.session_state.speed_val = extracted_data['speed']
                if extracted_data.get('load') != -1: st.session_state.load_val = extracted_data['load']
                if extracted_data.get('temp') != -1: st.session_state.temp_val = extracted_data['temp']
                if extracted_data.get('dtc'): st.session_state.dtc_val = extracted_data['dtc']
                
                st.success("✅ Data extracted successfully!")
            except Exception as e:
                st.warning("Could not auto-extract data. Please enter manually.")

    st.markdown("---")
    
    # --- VEHICLE & DTC ---
    st.subheader("Vehicle Information")
    selected_vehicle = st_searchbox(
        search_vehicles,
        key="vehicle_searchbox",
        label="Type Vehicle Name (e.g., Ford F-150)"
    )
    car_model = selected_vehicle if selected_vehicle else "Not Specified"
    dtc_code = st.text_input("Active/Pending DTCs", value=st.session_state.dtc_val, placeholder="e.g., P0300, C0034")
    
    # --- FREE TEXT SYMPTOMS ---
    st.subheader("Symptoms & Conditions")
    primary_symptom = st.text_input("Primary Symptom", placeholder="e.g., Power loss, Grinding noise")
    operating_condition = st.text_input("Occurs When?", placeholder="e.g., Cold start, Uphill 3rd gear")

    # --- NUMBER INPUT BOXES ---
    st.subheader("Live Freeze Frame Data")
    rpm = st.number_input("Engine RPM", min_value=0, max_value=10000, value=int(st.session_state.rpm_val), step=100)
    speed = st.number_input("Speed (km/h)", min_value=0, max_value=300, value=int(st.session_state.speed_val), step=5)
    load = st.number_input("Engine Load (%)", min_value=0, max_value=100, value=int(st.session_state.load_val), step=1)
    temp = st.number_input("Coolant Temp (°C)", min_value=-40, max_value=150, value=int(st.session_state.temp_val), step=1)

# --- MAIN CHAT INTERFACE ---
st.title("🚗 AI Senior Diagnostic Judge")
st.caption("Flow: UI/Vision Ingestion ➔ Dynamic Context Gatekeeper ➔ ML + RAG + Web Execution")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==========================================
# 3. EXECUTION LOGIC
# ==========================================
if user_text := st.chat_input("Enter detailed mechanic notes, or ask for repair steps..."):
    
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    symp_val = primary_symptom if primary_symptom else 'Not Specified'
    occ_val = operating_condition if operating_condition else 'Not Specified'

    # ---> THE MASTER PROMPT <---
    full_mechanic_input = f"""
    Vehicle: {car_model}
    DTCs: {dtc_code if dtc_code else 'None Provided'}
    UI Selected Symptom: {symp_val}
    Occurs During: {occ_val}
    Sensor Data: RPM={rpm}, Speed={speed}, Load={load}%, Temp={temp}C
    Mechanic Notes: {user_text}
    """

    with st.chat_message("assistant"):
        with st.status("🚦 Triage in progress...", expanded=True) as status:
            try:
                # --- BACKEND LOGGING ---
                print("\n" + "="*60)
                print("🧠 [BACKEND LOG] GATEKEEPER INGESTION BLOCK:")
                print(full_mechanic_input)

                # --- STEP A: RUN SMART GATEKEEPER ---
                st.write("Evaluating intent and context...")
                triage_result = gatekeeper_chain.invoke({"input": full_mechanic_input})
                
                print(f"🔎 IS VALID: {triage_result.is_valid}")
                if not triage_result.is_valid:
                    print(f"⚠️ QUESTIONS GENERATED:\n{triage_result.clarifying_questions}")
                else:
                    print(f"✅ GENERATED HEADINGS: '{triage_result.ui_main_heading}' | '{triage_result.ui_steps_heading}'")
                print("="*60 + "\n")

                if not triage_result.is_valid:
                    status.update(label="⚠️ Triage Failed: Insufficient Context", state="complete", expanded=True)
                    st.warning("Request Halted. Cannot proceed without guessing.")
                    st.info(f"**Required Next Steps:**\n{triage_result.clarifying_questions}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": f"Please provide more context:\n{triage_result.clarifying_questions}"})
                    st.stop()
                
                # --- STEP B: RUN MAIN AGENT ---
                status.update(label="✅ Triage Passed. Executing Deep Scan...", state="running")
                start_time = time.time()
                
                chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:]])
                full_query = f"Recent Chat Context:\n{chat_history}\n\nCurrent Input:\n{full_mechanic_input}"
                
                st.write("📡 Running Data Retrieval & Analysis...")
                time.sleep(0.5)
                st.write("📚 Searching RAG Database & Web...")
                
                response = agent_executor.invoke({"input": full_query})
                raw_output = response['output']
                
                try:
                    st.write("⚙️ Parsing AI output...")
                    validated_data = parser.parse(raw_output)
                    duration = time.time() - start_time
                    status.update(label=f"✅ Analysis Complete ({duration:.2f}s)", state="complete", expanded=False)
                    
                    # --- DYNAMIC RENDERING FROM GATEKEEPER HEADINGS ---
                    st.markdown(f"### 🔹 {triage_result.ui_main_heading}")
                    st.markdown(validated_data.diagnosis)
                    
                    # Only show confidence if it's a diagnostic scenario
                    if "diagnos" in triage_result.ui_main_heading.lower():
                        st.markdown(f"**Consensus Confidence:** {validated_data.confidence_level}")
                    
                    if validated_data.safety_warning.lower() != "none":
                        st.error(f"⚠️ **Safety Warning:** {validated_data.safety_warning}")
                    
                    with st.expander("📊 View AI Evidence Sourcing (RAG/Web/ML)"):
                        st.write("**ML Tool Findings:**", validated_data.ml_evidence)
                        st.write("**Official Manuals (RAG):**", validated_data.rag_evidence)
                        st.write("**Web Forums & TSBs:**", validated_data.web_evidence)
                    
                    st.markdown(f"### 🛠️ {triage_result.ui_steps_heading}")
                    for i, step in enumerate(validated_data.action_plan, 1):
                        st.markdown(f"{i}. {step}")
                    
                    st.session_state.messages.append({"role": "assistant", "content": f"**{triage_result.ui_main_heading}:**\n{validated_data.diagnosis}"})

                except OutputParserException:
                    status.update(label="⚠️ Formatting Error by AI", state="complete", expanded=False)
                    st.warning("Validation failed. Displaying raw response for review.")
                    st.code(raw_output, language="json")

            except Exception as e:
                 status.update(label="❌ System Error", state="error")
                 st.error(f"System Error: {str(e)}")