# # Added the Langgrpah graphical flow .
# import streamlit as st
# import time
# import os
# import sys
# import json
# import base64
# import streamlit.components.v1 as components
# from PIL import Image
# import io
# from dotenv import load_dotenv

# from langchain_core.messages import HumanMessage
# from langchain_core.prompts import PromptTemplate
# from langchain_google_genai import ChatGoogleGenerativeAI
# from pydantic import BaseModel, Field
# from langchain_core.output_parsers import PydanticOutputParser

# # --- CONFIG & IMPORTS ---
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# load_dotenv()

# try:
#     from src.agents.advisor import agent_executor, parser
# except ImportError as e:
#     st.error(f"❌ Critical Import Error: {e}")
#     st.stop()

# # ==========================================
# # 0. SESSION STATE INITIALIZATION
# # ==========================================
# if 'messages' not in st.session_state: 
#     st.session_state.messages = []
# if 'processed_images' not in st.session_state: 
#     st.session_state.processed_images = set()

# defaults = {
#     'rpm_val': 0, 'speed_val': 0, 'load_val': 0, 'temp_val': 0, 
#     'dtc_val': "", 'car_model_val': ""
# }

# for key, val in defaults.items():
#     if key not in st.session_state:
#         st.session_state[key] = val

# st.set_page_config(page_title="Master Vehicle Diagnostic Judge", page_icon="🚗", layout="wide")
# llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

# # ==========================================
# # 2. SIDEBAR: DATA EXTRACTION & ARCHITECTURE
# # ==========================================
# with st.sidebar:
#     st.title("🛠️ Mechanic Workshop Intake")
#     st.subheader("🧠 Live Agentic Flow")
#     try:
#         graph_mermaid_code = agent_executor.get_graph().draw_mermaid()
#         components.html(
#             f"""
#             <div class="mermaid" style="background-color: white; padding: 10px; border-radius: 5px;">
#                 {graph_mermaid_code}
#             </div>
#             <script type="module">
#                 import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
#                 mermaid.initialize({{ startOnLoad: true, theme: 'forest' }});
#             </script>
#             """, height=350, scrolling=True
#         )
#     except:
#         st.info("Visualizing Agent Logic...")

#     st.markdown("---")
#     st.subheader("📸 Scan Diagnostic Tool/Dashboard")
#     uploaded_image = st.file_uploader(
#         "Upload snap (Supports: JPG, PNG, WEBP, HEIC)", type=["jpg", "jpeg", "png", "webp", "heic", "tiff"]
#     )

#     if uploaded_image:
#         image_id = f"{uploaded_image.name}_{uploaded_image.size}"
        
#         if image_id not in st.session_state.processed_images:
#             print(f"\n{'='*20} VISION EXTRACTION START {'='*20}")
#             with st.spinner("🔍 First-time Image Extraction..."):
#                 try:
#                     img = Image.open(uploaded_image).convert("RGB")
#                     buffered = io.BytesIO()
#                     img.save(buffered, format="JPEG")
#                     encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')

#                     vision_prompt = """
#                     You are a specialist automotive technician. Look at this OBD-II scanner screenshot.
#                     Extract the following specific values to JSON. 
#                     IMPORTANT: Labels may be located BELOW the numeric values.
                    
#                     1. 'dtc': Look for a 5-character code starting with P, B, C, or U (e.g., P0100).
#                     2. 'rpm': Engine Revolutions Per Minute.
#                     3. 'speed': Vehicle speed. If in mph, convert to km/h (multiply by 1.6).
#                     4. 'temp': Coolant temperature. If in Fahrenheit (°F), convert to Celsius (°C) using (F-32)*5/9.
#                     5. 'load': Calculated Engine Load percentage.
                    
#                     Return ONLY raw JSON with keys: rpm, speed, load, temp, dtc. 
#                     If a value is missing, return null.
#                     """

#                     vision_msg = HumanMessage(content=[
#                         {"type": "text", "text": vision_prompt},
#                         {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
#                     ])
#                     v_res = llm_flash.invoke([vision_msg])
#                     v_data = json.loads(v_res.content.replace('```json','').replace('```','').strip())

#                     def safe_int(val):
#                         try:
#                             if val is None or val == "": return 0
#                             return int(float(val))
#                         except (ValueError, TypeError): return 0

#                     st.session_state.rpm_val = safe_int(v_data.get('rpm'))
#                     st.session_state.speed_val = safe_int(v_data.get('speed'))
#                     st.session_state.load_val = safe_int(v_data.get('load'))
#                     st.session_state.temp_val = safe_int(v_data.get('temp'))
#                     st.session_state.dtc_val = str(v_data.get('dtc') or "")

#                     st.session_state.processed_images.add(image_id)
#                     print(f"📦 [VISION OUTPUT]:\n{json.dumps(v_data, indent=4)}")
#                     st.success("✅ Extraction Complete!")
#                     st.rerun() 
#                 except Exception as e:
#                     st.error(f"Image processing failed: {e}")
#     else:
#         st.session_state.processed_images.clear()

#     st.subheader("🚗 Vehicle Context")
    
#     # REPLACED: searchbox removed for faster loading. Standard text input used.
#     car_model = st.text_input("Vehicle Model", value=st.session_state.car_model_val, placeholder="e.g. Tata Nexon 1.2L")
#     st.session_state.car_model_val = car_model
    
#     dtc_code = st.text_input("Active DTCs", value=st.session_state.dtc_val)

#     col1, col2 = st.columns(2)
#     with col1:
#         rpm_in = st.number_input("RPM", value=int(st.session_state.rpm_val))
#         load_in = st.number_input("Load %", value=int(st.session_state.load_val))
#     with col2:
#         speed_in = st.number_input("Speed km/h", value=int(st.session_state.speed_val))
#         temp_in = st.number_input("Temp °C", value=int(st.session_state.temp_val))

#     primary_symptom = st.text_input("Symptom (e.g., Misfire)")
#     operating_condition = st.text_input("When? (e.g., Cold Start)")

# # ==========================================
# # 3. MAIN INTERFACE (CHAT PERSISTENCE)
# # ==========================================
# st.title("🚗 AI Senior Diagnostic Judge")
# st.markdown("---")

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         if msg["type"] == "structured":
#             data = msg["data"]
#             st.markdown(f"## 🔹 {data['main_heading']}")
#             st.write(data["diagnosis"])
#             with st.expander("📊 Evidence (RAG/Web/ML)"):
#                 st.write("**Analysis Sources:**", data["rag_evidence"])
#                 st.write("**Web Research:**", data["web_evidence"])
#             st.markdown(f"### 🛠️ {data['steps_heading']}")
#             for i, step in enumerate(data["action_plan"], 1):
#                 st.markdown(f"{i}. {step}")
#             if data["safety_warning"].lower() != "none":
#                 st.error(f"⚠️ **Safety Warning:** {data['safety_warning']}")
#         else:
#             st.markdown(msg["content"])

# if user_text := st.chat_input("Explain the issue or ask for a fix..."):
#     st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
#     with st.chat_message("user"):
#         st.markdown(user_text)

#     # Use 'car_model' from the text_input
#     full_input = (
#         f"Vehicle: {car_model if car_model else 'Not Specified'} | DTC: {dtc_code} | Symptom: {primary_symptom} | "
#         f"Condition: {operating_condition} | Sensors: RPM={rpm_in}, Speed={speed_in}, "
#         f"Load={load_in}%, Temp={temp_in}C | User Instruction: {user_text}"
#     )

#     with st.chat_message("assistant"):
#         with st.status("🕵️ Agentic Reasoning...", expanded=True) as status:
#             try:
#                 print(f"\n{'='*20} GATEKEEPER TRIAGE START {'='*20}")
#                 class GatekeeperResponse(BaseModel):
#                     is_valid: bool; clarifying_questions: str
#                     ui_main_heading: str; ui_steps_heading: str

#                 gk_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)
#                 gk_res = llm_flash.invoke(f"Set headings for intent '{user_text}': {gk_parser.get_format_instructions()}")
#                 triage = gk_parser.parse(gk_res.content.replace('```json','').replace('```','').strip())

#                 response = agent_executor.invoke({"input": full_input})
#                 raw_output = response.get('output', "")
#                 text_output = "".join([i.get("text", str(i)) if isinstance(i, dict) else str(i) for i in raw_output]) if isinstance(raw_output, list) else str(raw_output)
#                 validated = parser.parse(text_output.replace("```json", "").replace("```", "").strip())

#                 status.update(label="✅ Complete", state="complete", expanded=False)

#                 structured_data = {
#                     "main_heading": triage.ui_main_heading,
#                     "diagnosis": validated.diagnosis,
#                     "rag_evidence": validated.rag_evidence,
#                     "web_evidence": validated.web_evidence,
#                     "steps_heading": triage.ui_steps_heading,
#                     "action_plan": validated.action_plan,
#                     "safety_warning": validated.safety_warning,
#                     "confidence_level": validated.confidence_level
#                 }
                
#                 st.session_state.messages.append({"role": "assistant", "type": "structured", "data": structured_data})
#                 st.rerun()

#             except Exception as e:
#                 st.error(f"Execution Error: {e}")



# New UI with agentic flow visualization in the sidebar and a more professional report card style for the assistant's structured responses. 

import streamlit as st
import time
import os
import sys
import json
import base64
import re
import streamlit.components.v1 as components
from PIL import Image
import io
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# --- CONFIG & SYSTEM SETUP ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

try:
    from src.agents.advisor import agent_executor, parser
except ImportError as e:
    st.error(f"Critical System Error: {e}")
    st.stop()

# ==========================================
# 0. UI CONFIG & ENTERPRISE THEME
# ==========================================
st.set_page_config(
    page_title="Tata Technologies | Smart Diagnostic Platform",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal, non-breaking CSS for compact metrics
st.markdown("""
    <style>
    /* Compact Metric Styling */
    div[data-testid="stMetric"] { background-color: transparent; padding: 0px; }
    [data-testid="stMetricValue"] { font-size: 1.4rem; font-weight: bold; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; opacity: 0.8; }
    
    /* Clean Action Plan Lists */
    .action-step { margin-bottom: 8px; font-size: 1.05rem; }
    
    /* Buttons */
    .stButton>button { border-radius: 6px; font-weight: 600; width: 100%; border: 1px solid #4A90E2; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 0. SESSION STATE INITIALIZATION
# ==========================================
if 'messages' not in st.session_state: 
    st.session_state.messages = []
if 'processed_images' not in st.session_state: 
    st.session_state.processed_images = set()

defaults = {'rpm_val': 0, 'speed_val': 0, 'load_val': 0, 'temp_val': 0, 'dtc_val': "", 'car_model_val': ""}
for key, val in defaults.items():
    if key not in st.session_state: 
        st.session_state[key] = val

llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

def clean_step_text(text):
    """Strips ugly leading numbers/symbols from LLM steps for clean rendering"""
    return re.sub(r'^[\d\s\.\)\-\*]+', '', text).strip()

# ==========================================
# 1. SIDEBAR: DATA INGESTION
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/8e/Tata_logo.svg", width=120)
    st.subheader("Engineering Console", divider="blue")
    
    with st.expander("📸 Automated Data Intake (Vision)", expanded=True):
        uploaded_image = st.file_uploader("Upload Scanner / Dashboard Image", type=["jpg", "jpeg", "png", "webp"])
        
        if uploaded_image:
            image_id = f"{uploaded_image.name}_{uploaded_image.size}"
            if image_id not in st.session_state.processed_images:
                with st.spinner("Processing Telemetry..."):
                    try:
                        img = Image.open(uploaded_image).convert("RGB")
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG")
                        encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')

                        vision_prompt = """Extract sensor data to JSON: rpm, speed, load, temp, dtc. Convert units: F to C, mph to kmh. Return ONLY raw JSON."""
                        vision_msg = HumanMessage(content=[
                            {"type": "text", "text": vision_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded}"}}
                        ])
                        v_res = llm_flash.invoke([vision_msg])
                        v_data = json.loads(v_res.content.replace('```json','').replace('```','').strip())

                        # BULLETPROOF EXTRACTION FUNCTION (Unchanged)
                        def safe_int(val):
                            if val is None: return 0
                            if isinstance(val, dict): 
                                val = val.get('value', val.get('rpm', val.get('temp', 0)))
                            val_str = str(val)
                            nums = re.findall(r'-?\d+\.?\d*', val_str) 
                            if nums:
                                try: return int(float(nums[0]))
                                except: return 0
                            return 0

                        st.session_state.rpm_val = safe_int(v_data.get('rpm'))
                        st.session_state.speed_val = safe_int(v_data.get('speed'))
                        st.session_state.load_val = safe_int(v_data.get('load'))
                        st.session_state.temp_val = safe_int(v_data.get('temp'))
                        st.session_state.dtc_val = str(v_data.get('dtc') or "")
                        st.session_state.processed_images.add(image_id)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Telemetry Extraction Error: {e}")
        else:
            st.session_state.processed_images.clear()

    with st.expander("📝 Manual Context", expanded=True):
        car_model = st.text_input("Vehicle Model", value=st.session_state.car_model_val, placeholder="e.g., Tata Safari")
        st.session_state.car_model_val = car_model
        dtc_code = st.text_input("Active Fault Codes", value=st.session_state.dtc_val)
        primary_symptom = st.text_input("Symptom Description")
        operating_condition = st.text_input("Operating Condition")

    with st.expander("📊 Live Sensor Overrides", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            rpm_in = st.number_input("Engine RPM", value=int(st.session_state.rpm_val))
            load_in = st.number_input("Load %", value=int(st.session_state.load_val))
        with col2:
            speed_in = st.number_input("Speed km/h", value=int(st.session_state.speed_val))
            temp_in = st.number_input("Temp °C", value=int(st.session_state.temp_val))

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Clear Diagnostic Session"):
        st.session_state.messages = []
        st.session_state.processed_images = set()
        st.rerun()

# ==========================================
# 2. MAIN DASHBOARD
# ==========================================

# SPACE-SAVING COMPACT HEADER: Banner + Metrics merged into one block
with st.container(border=True):
    col_logo, col_m1, col_m2, col_m3, col_m4 = st.columns([2, 1, 1, 1, 1])
    
    with col_logo:
        st.markdown("<h2 style='margin:0; padding:0;'>Tata Technologies</h2>", unsafe_allow_html=True)
        st.caption("Smart Diagnostic Intelligence")
        
    with col_m1: st.metric("RPM", f"{rpm_in}")
    with col_m2: st.metric("Speed", f"{speed_in} km/h")
    with col_m3: st.metric("Load", f"{load_in} %")
    with col_m4: st.metric("Temp", f"{temp_in} °C")

# 1. RENDER CHAT HISTORY
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**Query:** {msg['content']}")
    
    elif msg["role"] == "assistant":
        if msg["type"] == "structured":
            d = msg["data"]
            with st.chat_message("assistant"):
                with st.container(border=True):
                    # Native Streamlit headers (theme-aware, fixes the invisible color issue)
                    st.subheader(f"📝 {d['main_heading']}", divider="gray")
                    st.markdown(f"**Diagnosis:** {d['diagnosis']}")
                    
                    with st.expander("🔍 View Technical Evidence (RAG & Web)"):
                        st.markdown("**Internal Manual Database:**")
                        st.caption(d["rag_evidence"])
                        st.markdown("**Live Field Data / TSBs:**")
                        st.caption(d["web_evidence"])
                    
                    st.subheader(f"🛠️ {d['steps_heading']}")
                    for i, step in enumerate(d["action_plan"], 1):
                        clean_text = clean_step_text(step)
                        st.markdown(f"<div class='action-step'><b>Step {i}:</b> {clean_text}</div>", unsafe_allow_html=True)
                    
                    if d["safety_warning"].lower() != "none":
                        st.error(f"**SAFETY CRITICAL ALERT:** {d['safety_warning']}", icon="🚨")

# 2. CHAT INPUT LOGIC 
if user_text := st.chat_input("Enter diagnostic query or request procedure..."):
    st.session_state.messages.append({"role": "user", "content": user_text, "type": "text"})
    with st.chat_message("user"):
        st.markdown(f"**Query:** {user_text}")

    full_input = (
        f"Vehicle: {car_model} | DTC: {dtc_code} | Symptom: {primary_symptom} | "
        f"Condition: {operating_condition} | Sensors: RPM={rpm_in}, Speed={speed_in}, "
        f"Load={load_in}%, Temp={temp_in}C | User Instruction: {user_text}"
    )

    with st.chat_message("assistant"):
        with st.spinner("Processing through Agentic Framework..."):
            try:
                # Triage
                class GatekeeperResponse(BaseModel):
                    is_valid: bool; clarifying_questions: str; ui_main_heading: str; ui_steps_heading: str
                
                gk_parser = PydanticOutputParser(pydantic_object=GatekeeperResponse)
                gk_res = llm_flash.invoke(f"Set headings for intent '{user_text}': {gk_parser.get_format_instructions()}")
                triage = gk_parser.parse(gk_res.content.replace('```json','').replace('```','').strip())

                # Reasoner
                response = agent_executor.invoke({"input": full_input})
                raw_output = response.get('output', "")
                text_output = "".join([i.get("text", str(i)) if isinstance(i, dict) else str(i) for i in raw_output]) if isinstance(raw_output, list) else str(raw_output)
                validated = parser.parse(text_output.replace("```json", "").replace("```", "").strip())

                # Formatting
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
                
                # Append & Rerun
                st.session_state.messages.append({"role": "assistant", "type": "structured", "data": structured_data})
                st.rerun()

            except Exception as e:
                st.error(f"System Error: {e}")