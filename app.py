# import streamlit as st
# import time
# import os
# import sys
# import json
# import base64
# from PIL import Image
# from dotenv import load_dotenv

# # Langchain and Pydantic imports
# from langchain_core.exceptions import OutputParserException
# from langchain_core.messages import HumanMessage
# from langchain_core.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import BaseModel, Field
# from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

# # Dynamic Searchbox import
# try:
#     from streamlit_searchbox import st_searchbox
# except ImportError:
#     st.error("Please install the searchbox component: pip install streamlit-searchbox")
#     st.stop()

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# load_dotenv()

# try:
#     from src.agents.advisor import agent_executor, parser
# except ImportError as e:
#     st.error(f"❌ Critical Import Error: {e}\nMake sure your src.agents module is accessible.")
#     st.stop()

# # ==========================================
# # 0. INITIALIZE SESSION STATE (For Auto-Fill & Cache)
# # ==========================================
# if 'rpm_val' not in st.session_state: st.session_state.rpm_val = 2200
# if 'speed_val' not in st.session_state: st.session_state.speed_val = 40
# if 'load_val' not in st.session_state: st.session_state.load_val = 90
# if 'temp_val' not in st.session_state: st.session_state.temp_val = 90
# if 'dtc_val' not in st.session_state: st.session_state.dtc_val = ""

# if 'vehicle_db' not in st.session_state:
#     st.session_state.vehicle_db = set()

# # ==========================================
# # 1. SMART GATEKEEPER & LLM SETUP
# # ==========================================
# llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# class GatekeeperResponse(BaseModel):
#     is_valid: bool = Field(description="True if the prompt has enough technical detail OR is a direct request for a specific repair procedure. False if it's too generic.")
#     clarifying_questions: str = Field(description="If False, provide 2-3 specific technical questions. If True, write 'None'.")
#     ui_main_heading: str = Field(description="A 2-4 word contextual title for the main AI response based on what the user is asking. (e.g., 'Diagnostic Assessment', 'Repair Procedure', 'System Explanation')")
#     ui_steps_heading: str = Field(description="A 2-4 word contextual title for the bulleted list. (e.g., 'Troubleshooting Steps', 'Replacement Guide', 'Next Steps')")

# gatekeeper_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)

# gatekeeper_prompt = PromptTemplate(
#     template="""
#     You are a Master Technician Triage AI. A mechanic has submitted a diagnostic request. Evaluate the Combined Mechanic Input below.
#     1. If they provide generic symptoms with no data, reject it (`is_valid: False`) and ask specific technical questions.
#     2. If they provide specific data, DTCs, OR ask for a specific repair/explanation, accept it (`is_valid: True`).
#     3. Look at what the user is asking and generate appropriate UI headings. If they ask "how to fix", the heading should be about Repair/Procedures, not Diagnosis.

#     Combined Mechanic Input:
#     {input}

#     {format_instructions}
#     """,
#     input_variables=["input"],
#     partial_variables={"format_instructions": gatekeeper_parser.get_format_instructions()}
# )

# gatekeeper_chain = gatekeeper_prompt | llm_flash | StrOutputParser() | gatekeeper_parser

# # --- SMART CACHE VEHICLE SEARCH FUNCTION ---
# def search_vehicles(searchterm: str) -> list[str]:
#     """Smart Cache Autocomplete: Learns and caches vehicles dynamically from the AI."""
#     if not searchterm or len(searchterm) < 2: return []
#     searchterm_lower = searchterm.lower()

#     local_matches = [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()]
#     if len(local_matches) >= 5: return local_matches[:6]

#     try:
#         prompt = f"User is typing '{searchterm}' in a vehicle autocomplete box. Return a JSON array of exactly 15 real-world car Makes and Models that match or start with this text. Example: [\"{searchterm.title()} Model 1\"]. ONLY output the JSON array, no markdown."
#         response = llm_flash.invoke(prompt)
#         clean_response = response.content.replace('```json','').replace('```','').strip()
#         new_suggestions = json.loads(clean_response)

#         st.session_state.vehicle_db.update(new_suggestions)
#         updated_matches = [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()]
#         return updated_matches[:6] if updated_matches else new_suggestions[:6]
#     except Exception:
#         return local_matches[:6] if local_matches else [searchterm]


# # ==========================================
# # 2. STREAMLIT UI SETUP
# # ==========================================
# st.set_page_config(page_title="AI Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")

# # ==========================================
# # LEFT SIDEBAR (Intake Forms)
# # ==========================================
# with st.sidebar:
#     if st.button("🚨 HARD RESET (Nuke Cache)"):
#         st.session_state.clear()
#         st.cache_data.clear()
#         st.rerun()

#     st.title("📋 Diagnostic Intake")

#     # --- VISION AUTO-FILL ---
#     st.subheader("📸 Auto-Fill from Image")
#     uploaded_image = st.file_uploader("Upload Scanner/Dashboard Photo", type=["jpg", "jpeg", "png"])

#     if uploaded_image is not None:
#         with st.spinner("Extracting data with Gemini Vision..."):
#             try:
#                 image_bytes = uploaded_image.getvalue()
#                 encoded_image = base64.b64encode(image_bytes).decode('utf-8')

#                 vision_msg = HumanMessage(
#                     content=[
#                         {"type": "text", "text": "Analyze this car dashboard or OBD-II scanner image. Extract the following values if visible: RPM, Speed (km/h), Engine Load (%), Coolant Temp (C), and any DTC codes (e.g., P0171). Output ONLY a raw JSON object with keys: 'rpm' (int), 'speed' (int), 'load' (int), 'temp' (int), 'dtc' (string). Use -1 for numbers if not visible, and empty string for dtc if not visible. No markdown formatting."},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
#                     ]
#                 )
#                 vision_response = llm_flash.invoke([vision_msg])
#                 extracted_data = json.loads(vision_response.content.replace('```json','').replace('```','').strip())

#                 if extracted_data.get('rpm') != -1: st.session_state.rpm_val = extracted_data['rpm']
#                 if extracted_data.get('speed') != -1: st.session_state.speed_val = extracted_data['speed']
#                 if extracted_data.get('load') != -1: st.session_state.load_val = extracted_data['load']
#                 if extracted_data.get('temp') != -1: st.session_state.temp_val = extracted_data['temp']
#                 if extracted_data.get('dtc'): st.session_state.dtc_val = extracted_data['dtc']

#                 st.success("✅ Data extracted successfully!")

#             except Exception as e:
#                 st.warning("Could not auto-extract data. Please enter manually.")

#     st.markdown("---")

#     # --- VEHICLE & DTC ---
#     st.subheader("Vehicle Information")
#     selected_vehicle = st_searchbox(
#         search_vehicles,
#         key="vehicle_searchbox",
#         label="Type Vehicle Name (e.g., Ford F-150)"
#     )
#     car_model = selected_vehicle if selected_vehicle else "Not Specified"

#     dtc_code = st.text_input("Active/Pending DTCs", value=st.session_state.dtc_val, placeholder="e.g., P0300, C0034")

#     # --- FREE TEXT SYMPTOMS ---
#     st.subheader("Symptoms & Conditions")
#     primary_symptom = st.text_input("Primary Symptom", placeholder="e.g., Power loss, Grinding noise")
#     operating_condition = st.text_input("Occurs When?", placeholder="e.g., Cold start, Uphill 3rd gear")

#     # --- NUMBER INPUT BOXES ---
#     st.subheader("Live Freeze Frame Data")
#     rpm = st.number_input("Engine RPM", min_value=0, max_value=10000, value=int(st.session_state.rpm_val), step=100)
#     speed = st.number_input("Speed (km/h)", min_value=0, max_value=300, value=int(st.session_state.speed_val), step=5)
#     load = st.number_input("Engine Load (%)", min_value=0, max_value=100, value=int(st.session_state.load_val), step=1)
#     temp = st.number_input("Coolant Temp (°C)", min_value=-40, max_value=150, value=int(st.session_state.temp_val), step=1)


# # ==========================================
# # MAIN PAGE (Chat Interface)
# # ==========================================
# st.title("🚗 AI Senior Diagnostic Judge")
# st.caption("Flow: UI/Vision Ingestion ➔ Dynamic Context Gatekeeper ➔ ML + RAG + Web Execution")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ==========================================
# # 3. EXECUTION LOGIC
# # ==========================================
# if user_text := st.chat_input("Enter detailed mechanic notes, or ask for repair steps..."):
#     st.session_state.messages.append({"role": "user", "content": user_text})
#     with st.chat_message("user"):
#         st.markdown(user_text)

#     symp_val = primary_symptom if primary_symptom else 'Not Specified'
#     occ_val = operating_condition if operating_condition else 'Not Specified'

#     # ---> THE MASTER PROMPT <---
#     full_mechanic_input = f"""
#     Vehicle: {car_model}
#     DTCs: {dtc_code if dtc_code else 'None Provided'}
#     UI Selected Symptom: {symp_val}
#     Occurs During: {occ_val}
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
#                 st.write("Evaluating intent and context...")
#                 triage_result = gatekeeper_chain.invoke({"input": full_mechanic_input})

#                 print(f"🔎 IS VALID: {triage_result.is_valid}")
#                 if not triage_result.is_valid:
#                     print(f"⚠️ QUESTIONS GENERATED:\n{triage_result.clarifying_questions}")
#                 else:
#                     print(f"✅ GENERATED HEADINGS: '{triage_result.ui_main_heading}' | '{triage_result.ui_steps_heading}'")
#                 print("="*60 + "\n")

#                 if not triage_result.is_valid:
#                     status.update(label="⚠️ Triage Failed: Insufficient Context", state="complete", expanded=True)
#                     st.warning("Request Halted. Cannot proceed without guessing.")
#                     st.info(f"**Required Next Steps:**\n{triage_result.clarifying_questions}")
#                     st.session_state.messages.append({"role": "assistant", "content": f"Please provide more context:\n{triage_result.clarifying_questions}"})
#                     st.stop()

#                 # --- STEP B: RUN MAIN AGENT ---
#                 status.update(label="✅ Triage Passed. Executing Deep Scan...", state="running")
#                 start_time = time.time()

#                 chat_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages[-4:]])
#                 full_query = f"Recent Chat Context:\n{chat_history}\n\nCurrent Input:\n{full_mechanic_input}"

#                 st.write("📡 Running Data Retrieval & Analysis...")
#                 time.sleep(0.5)
#                 st.write("📚 Searching RAG Database & Web...")

#                 response = agent_executor.invoke({"input": full_query})
#                 raw_output = response['output']

#                 try:
#                     st.write("⚙️ Parsing AI output...")
                    
#                     # --- STRING PARSING FIX IMPLEMENTED HERE ---
#                     if isinstance(raw_output, list):
#                         text_parts = []
#                         for item in raw_output:
#                             if isinstance(item, dict) and "text" in item:
#                                 text_parts.append(item["text"])
#                             elif isinstance(item, str):
#                                 text_parts.append(item)
#                         text_output = "".join(text_parts)
#                     else:
#                         text_output = str(raw_output)
                        
#                     text_output = text_output.replace("```json", "").replace("```", "").strip()
                        
#                     validated_data = parser.parse(text_output)
                    
#                     duration = time.time() - start_time
#                     status.update(label=f"✅ Analysis Complete ({duration:.2f}s)", state="complete", expanded=False)

#                     # --- DYNAMIC RENDERING FROM GATEKEEPER HEADINGS ---
#                     st.markdown(f"### 🔹 {triage_result.ui_main_heading}")
#                     st.markdown(validated_data.diagnosis)

#                     # Only show confidence if it's a diagnostic scenario
#                     if "diagnos" in triage_result.ui_main_heading.lower():
#                         st.markdown(f"**Consensus Confidence:** {validated_data.confidence_level}")

#                     if validated_data.safety_warning.lower() != "none":
#                         st.error(f"⚠️ **Safety Warning:** {validated_data.safety_warning}")

#                     with st.expander("📊 View AI Evidence Sourcing (RAG/Web/ML)"):
#                         st.write("**ML Tool Findings:**", validated_data.ml_evidence)
#                         st.write("**Official Manuals (RAG):**", validated_data.rag_evidence)
#                         st.write("**Web Forums & TSBs:**", validated_data.web_evidence)

#                     st.markdown(f"### 🛠️ {triage_result.ui_steps_heading}")
#                     for i, step in enumerate(validated_data.action_plan, 1):
#                         st.markdown(f"{i}. {step}")

#                     st.session_state.messages.append({"role": "assistant", "content": f"**{triage_result.ui_main_heading}:**\n{validated_data.diagnosis}"})

#                 except OutputParserException:
#                     status.update(label="⚠️ Formatting Error by AI", state="complete", expanded=False)
#                     st.warning("Validation failed. Displaying raw response for review.")
#                     st.code(raw_output, language="json")

#             except Exception as e:
#                 status.update(label="❌ System Error", state="error")
#                 st.error(f"System Error: {str(e)}")


# Added the Langgrpah graphical flow .
import streamlit as st
import time
import os
import sys
import json
import base64
import streamlit.components.v1 as components
from PIL import Image
import io
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# --- CONFIG & IMPORTS ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

try:
    from src.agents.advisor import agent_executor, parser
except ImportError as e:
    st.error(f"❌ Critical Import Error: {e}")
    st.stop()

try:
    from streamlit_searchbox import st_searchbox
except ImportError:
    st.error("Please install: pip install streamlit-searchbox")
    st.stop()

# ==========================================
# 0. SESSION STATE INITIALIZATION
# ==========================================
if 'messages' not in st.session_state: 
    st.session_state.messages = []
if 'processed_images' not in st.session_state: 
    st.session_state.processed_images = set() # Track unique IDs of finished images

defaults = {
    'rpm_val': 0, 'speed_val': 0, 'load_val': 0, 'temp_val': 0, 
    'dtc_val': "", 'vehicle_db': set()
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

st.set_page_config(page_title="Master Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")
llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# ==========================================
# 1. VEHICLE AUTOCOMPLETE
# ==========================================
def search_vehicles(searchterm: str) -> list[str]:
    if not searchterm or len(searchterm) < 2: return []
    searchterm_lower = searchterm.lower()
    local_matches = [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()]
    if len(local_matches) >= 5: return local_matches[:6]
    try:
        res = llm_flash.invoke(f"Return JSON array of 15 real cars matching '{searchterm}'. JSON only.")
        new_suggestions = json.loads(res.content.replace('```json','').replace('```','').strip())
        st.session_state.vehicle_db.update(new_suggestions)
        return [car for car in st.session_state.vehicle_db if searchterm_lower in car.lower()][:6]
    except:
        return local_matches[:6] if local_matches else [searchterm]

# ==========================================
# 2. SIDEBAR: DATA EXTRACTION & ARCHITECTURE
# ==========================================
with st.sidebar:
    st.title("🛠️ Mechanic Workshop Intake")
    st.subheader("🧠 Live Agentic Flow")
    try:
        graph_mermaid_code = agent_executor.get_graph().draw_mermaid()
        components.html(
            f"""
            <div class="mermaid" style="background-color: white; padding: 10px; border-radius: 5px;">
                {graph_mermaid_code}
            </div>
            <script type="module">
                import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                mermaid.initialize({{ startOnLoad: true, theme: 'forest' }});
            </script>
            """, height=350, scrolling=True
        )
    except:
        st.info("Visualizing Agent Logic...")

    st.markdown("---")
    st.subheader("📸 Scan Diagnostic Tool/Dashboard")
    uploaded_image = st.file_uploader(
        "Upload snap (Supports: JPG, PNG, WEBP, HEIC)", type=["jpg", "jpeg", "png", "webp", "heic", "tiff"]
    )

    # --- ONE-TIME VISION LOGIC ---
    if uploaded_image:
        image_id = f"{uploaded_image.name}_{uploaded_image.size}"
        
        if image_id not in st.session_state.processed_images:
            print(f"\n{'='*20} VISION EXTRACTION START {'='*20}")
            with st.spinner("🔍 First-time Image Extraction..."):
                try:
                    img = Image.open(uploaded_image).convert("RGB")
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')

                    vision_msg = HumanMessage(content=[
                        {"type": "text", "text": "Extract sensor data to JSON: rpm, speed, load, temp, dtc. Return ONLY raw JSON."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                    ])
                    v_res = llm_flash.invoke([vision_msg])
                    v_data = json.loads(v_res.content.replace('```json','').replace('```','').strip())

                    def safe_int(val):
                        try:
                            if val is None or val == "": return 0
                            return int(float(val))
                        except (ValueError, TypeError): return 0

                    st.session_state.rpm_val = safe_int(v_data.get('rpm'))
                    st.session_state.speed_val = safe_int(v_data.get('speed'))
                    st.session_state.load_val = safe_int(v_data.get('load'))
                    st.session_state.temp_val = safe_int(v_data.get('temp'))
                    st.session_state.dtc_val = str(v_data.get('dtc') or "")

                    # Mark this specific image as FINISHED
                    st.session_state.processed_images.add(image_id)
                    st.success("✅ Extraction Complete!")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Image processing failed: {e}")
    else:
        # If user removes the image, clear the set so they can re-upload if needed
        st.session_state.processed_images.clear()

    st.subheader("🚗 Vehicle Context")
    selected_vehicle = st_searchbox(search_vehicles, key="v_search", label="Select Vehicle")
    car_model = selected_vehicle if selected_vehicle else "Not Specified"
    dtc_code = st.text_input("Active DTCs", value=st.session_state.dtc_val)

    col1, col2 = st.columns(2)
    with col1:
        rpm_in = st.number_input("RPM", value=int(st.session_state.rpm_val))
        load_in = st.number_input("Load %", value=int(st.session_state.load_val))
    with col2:
        speed_in = st.number_input("Speed km/h", value=int(st.session_state.speed_val))
        temp_in = st.number_input("Temp °C", value=int(st.session_state.temp_val))

    primary_symptom = st.text_input("Symptom (e.g., Misfire)")
    operating_condition = st.text_input("When? (e.g., Cold Start)")

# ==========================================
# 3. MAIN INTERFACE (CHAT PERSISTENCE)
# ==========================================
st.title("🚗 AI Senior Diagnostic Judge")
st.markdown("---")

# RENDER HISTORY FIRST (Fixes the "vanishing" issue)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["type"] == "structured":
            data = msg["data"]
            st.markdown(f"## 🔹 {data['main_heading']}")
            st.write(data["diagnosis"])
            with st.expander("📊 Evidence (RAG/Web/ML)"):
                st.write("**Analysis Sources:**", data["rag_evidence"])
                st.write("**Web Research:**", data["web_evidence"])
            st.markdown(f"### 🛠️ {data['steps_heading']}")
            for i, step in enumerate(data["action_plan"], 1):
                st.markdown(f"{i}. {step}")
            if data["safety_warning"].lower() != "none":
                st.error(f"⚠️ **Safety Warning:** {data['safety_warning']}")
        else:
            st.markdown(msg["content"])

if user_text := st.chat_input("Explain the issue or ask for a fix..."):
    # Store user message immediately and render it
    st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
    with st.chat_message("user"):
        st.markdown(user_text)

    full_input = (
        f"Vehicle: {car_model} | DTC: {dtc_code} | Symptom: {primary_symptom} | "
        f"Condition: {operating_condition} | Sensors: RPM={rpm_in}, Speed={speed_in}, "
        f"Load={load_in}%, Temp={temp_in}C | User Instruction: {user_text}"
    )

    with st.chat_message("assistant"):
        with st.status("🕵️ Agentic Reasoning...", expanded=True) as status:
            try:
                print(f"\n{'='*20} GATEKEEPER TRIAGE START {'='*20}")
                class GatekeeperResponse(BaseModel):
                    is_valid: bool; clarifying_questions: str
                    ui_main_heading: str; ui_steps_heading: str

                gk_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)
                gk_res = llm_flash.invoke(f"Set headings for intent '{user_text}': {gk_parser.get_format_instructions()}")
                triage = gk_parser.parse(gk_res.content.replace('```json','').replace('```','').strip())

                response = agent_executor.invoke({"input": full_input})
                raw_output = response.get('output', "")
                text_output = "".join([i.get("text", str(i)) if isinstance(i, dict) else str(i) for i in raw_output]) if isinstance(raw_output, list) else str(raw_output)
                validated = parser.parse(text_output.replace("```json", "").replace("```", "").strip())

                status.update(label="✅ Complete", state="complete", expanded=False)

                structured_data = {
                    "main_heading": triage.ui_main_heading,
                    "diagnosis": validated.diagnosis,
                    "rag_evidence": validated.rag_evidence,
                    "web_evidence": validated.web_evidence,
                    "steps_heading": triage.ui_steps_heading,
                    "action_plan": validated.action_plan,
                    "safety_warning": validated.safety_warning,
                    "confidence_level": validated.confidence_level
                }
                
                # Commit to history BEFORE rerun
                st.session_state.messages.append({"role": "assistant", "type": "structured", "data": structured_data})
                st.rerun()

            except Exception as e:
                st.error(f"Execution Error: {e}")