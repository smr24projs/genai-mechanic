import os
import json
import base64
import re
import time
from datetime import datetime
from io import BytesIO
import io
from PIL import Image

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser

# Import util modules
from src.utils import (
    CONFIG, setup_logging, validate_sensor_value,
    VisionExtractionError, AgentExecutionError, DataValidationError,
    diagnostic_history, perf_logger
)
from src.agents.advisor import langgraph_app, parser

logger = setup_logging()
logger.info("FastAPI backend started")

# Initialize LLM for vision and triage
llm_flash = ChatGoogleGenerativeAI(model=CONFIG.model_name, temperature=CONFIG.temperature)

app = FastAPI(title="Smart Diagnostics API")

# Standard CORS for standard React dev setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== Re-used Functions from app_enhanced.py ========

def clean_industry_text(text):
    return re.sub(r'^[\d\.\s\-*]+', '', text).strip()

def extract_and_validate_vision_data(v_data: dict) -> dict:
    try:
        validated_data = {
            'rpm': validate_sensor_value('rpm', v_data.get('rpm', 0)),
            'speed': validate_sensor_value('speed', v_data.get('speed', 0)),
            'load': validate_sensor_value('load', v_data.get('load', 0)),
            'temp': validate_sensor_value('temp', v_data.get('temp', 0)),
            'dtc': str(v_data.get('dtc') or ""),
        }
        if logger: logger.info(f"Vision data validated: {validated_data}")
        return validated_data
    except Exception as e:
        logger.warning(f"Validation error, using defaults: {str(e)}")
        return {'rpm': 0, 'speed': 0, 'load': 0, 'temp': 0, 'dtc': ""}

def call_vision_api(encoded_image: str):
    vision_prompt = """You MUST extract automotive sensor data from the image and return ONLY valid JSON.
    Extract exactly these values:
    - rpm: Engine RPM (integer, 0-8000)
    - speed: Vehicle speed (integer, km/h, 0-300)
    - load: Engine load (integer, 0-100%)
    - temp: Coolant temperature (integer, Celsius, -40 to 130)
    - dtc: Diagnostic code (string like P0100 or null)
    
    CONVERSION RULES:
    - mph to km/h: multiply by 1.609
    - Fahrenheit to Celsius: (F-32) × 5/9
    - Return null for missing values
    - Numbers ONLY, no units
    
    RESPOND WITH ONLY THIS JSON FORMAT:
    {"rpm": number, "speed": number, "load": number, "temp": number, "dtc": null or string}"""
    
    res = llm_flash.invoke([HumanMessage(content=[
        {"type": "text", "text": vision_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
    ])])
    return res

# ======== API Models ========

class ChatRequest(BaseModel):
    user_text: str
    car_model_val: str
    dtc_val: str
    symptom_val: str
    condition_val: str
    rpm_val: Any = ""
    speed_val: Any = ""
    load_val: Any = ""
    temp_val: Any = ""
    session_id: str
    history_context: Optional[str] = "No previous diagnosis."

# ======== API Endpoints ========

@app.post("/api/vision")
async def vision_endpoint(file: UploadFile = File(...)):
    try:
        start_time = time.time()
        contents = await file.read()
        try:
            img = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as ie:
            raise HTTPException(status_code=400, detail=f"Cannot read image: {str(ie)[:50]}")
        
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        img_bytes = buffered.getvalue()
        
        encoded = base64.b64encode(img_bytes).decode('utf-8')
        v_res = call_vision_api(encoded)
        duration_ms = (time.time() - start_time) * 1000
        
        if not v_res or not v_res.content:
            raise HTTPException(status_code=500, detail="API returned no response")
            
        clean_json = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', v_res.content, re.DOTALL)
        if clean_json:
            try:
                v_data = json.loads(clean_json.group())
                validated = extract_and_validate_vision_data(v_data)
                
                if logger: 
                    perf_logger.log_execution_time("Vision_Extraction", duration_ms)
                
                return {
                    "data": validated,
                    "duration_ms": duration_ms
                }
            except json.JSONDecodeError as je:
                raise HTTPException(status_code=500, detail=f"Bad JSON: {str(je)[:80]}")
        else:
            raise HTTPException(status_code=500, detail="No JSON detected in vision response.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        start_time = time.time()
        class Triage(BaseModel):
            is_diagnostic: bool = Field(description="True ONLY if user reports a NEW vehicle issue.")
            is_follow_up: bool = Field(description="True if user asks a follow-up question.")
            is_sufficient: bool = Field(description="True ONLY if enough specific technical info is provided.")
            response: str = Field(description="If is_diagnostic is False, OR if is_sufficient is False, put your conversational answer or clarifying question here.")
            missing: list = Field(default=[], description="List of specific missing data points.")
            ui_main_heading: str = Field(default="", description="Main heading for UI display (optional)")
            ui_steps_heading: str = Field(default="", description="Steps heading for UI display (optional)")
            extracted_rpm: Optional[str] = Field(default=None, description="Extract Engine RPM if mentioned anywhere (user text, symptom, or condition)")
            extracted_speed: Optional[str] = Field(default=None, description="Extract Vehicle Speed if mentioned anywhere (user text, symptom, or condition)")
            extracted_load: Optional[str] = Field(default=None, description="Extract Engine Load % if mentioned anywhere (user text, symptom, or condition)")
            extracted_temp: Optional[str] = Field(default=None, description="Extract Coolant Temp if mentioned anywhere (user text, symptom, or condition)")
            
        t_parser = PydanticOutputParser(pydantic_object=Triage)
        
        t_prompt = (
            f"Context from previous turn:\n{req.history_context}\n\n"
            f"User Input: '{req.user_text}' | Vehicle: {req.car_model_val} | DTC: {req.dtc_val} | "
            f"Symptom: {req.symptom_val} | Condition: {req.condition_val} | "
            f"Sensors: RPM={req.rpm_val}, Speed={req.speed_val}, Load={req.load_val}%, Temp={req.temp_val}C\n"
            "CRITICAL RULES:\n"
            "1. If user describes a NEW issue, set is_diagnostic=True and is_follow_up=False.\n"
            "2. If user asks a FOLLOW-UP question, set is_diagnostic=False, is_follow_up=True, and write the answer in 'response'.\n"
            "3. If general chat, set is_diagnostic=False and reply in 'response'.\n"
            "4. If is_diagnostic=True BUT the input is vague and lacks technical details, set is_sufficient=False. In 'response', act as a helpful mechanic and ask a specific CLARIFYING QUESTION.\n"
            "5. Analyze User Input, Symptom, and Condition fields. If you find sensor values anywhere in those fields, extract them into extracted_rpm, extracted_speed, extracted_load, or extracted_temp.\n"
            f"{t_parser.get_format_instructions()}"
        )
        
        t_res = llm_flash.invoke(t_prompt)
        intent = t_parser.parse(t_res.content.replace('```json','').replace('```','').strip())
        
        # Override req values with dynamically extracted values if present
        if intent.extracted_rpm is not None: req.rpm_val = intent.extracted_rpm
        if intent.extracted_speed is not None: req.speed_val = intent.extracted_speed
        if intent.extracted_load is not None: req.load_val = intent.extracted_load
        if intent.extracted_temp is not None: req.temp_val = intent.extracted_temp
        
        extracted_sensors = { 'rpm': req.rpm_val, 'speed': req.speed_val, 'load': req.load_val, 'temp': req.temp_val }

        if not intent.is_diagnostic or not intent.is_sufficient:
            return {
                "type": "text",
                "content": intent.response,
                "is_follow_up": False,
                "extracted_sensors": extracted_sensors
            }
            
        full_input = (
            f"Vehicle: {req.car_model_val} | DTC: {req.dtc_val} | "
            f"Symptom: {req.symptom_val} | Condition: {req.condition_val} | "
            f"Sensors: RPM={req.rpm_val}, Speed={req.speed_val}, "
            f"Load={req.load_val}%, Temp={req.temp_val}C | User: {req.user_text}"
        )
        
        raw_output = ""
        final_state = None
        
        # In a real streaming architecture we'd use Server-Sent Events (SSE). 
        # But for this iteration, we execute it fully and return the structured response.
        for output in langgraph_app.stream({"messages": [HumanMessage(content=full_input)]}):
            for node_name, state_update in output.items():
                final_state = state_update
        
        duration_ms = (time.time() - start_time) * 1000
        
        if final_state and "messages" in final_state:
            raw_content = final_state["messages"][-1].content
            if isinstance(raw_content, list):
                raw_output = "".join([item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_content])
            else:
                raw_output = str(raw_content)
        else:
            raise Exception("Agent flow failed to return messages.")
                
        validated = parser.parse(raw_output.replace("```json", "").replace("```", "").strip())
        
        structured_data = {
            "id": str(datetime.now().timestamp()),
            "main_heading": intent.ui_main_heading or "Diagnostic Analysis Results",
            "diagnosis": validated.diagnosis,
            "rag_evidence": validated.rag_evidence,
            "web_evidence": validated.web_evidence,
            "rag_score": validated.rag_score,
            "ml_score": validated.ml_score,
            "steps_heading": intent.ui_steps_heading or "Action Plan",
            "action_plan": [clean_industry_text(step) for step in validated.action_plan],
            "safety_warning": validated.safety_warning,
            "confidence_level": validated.confidence_level,
            "vehicle_model": req.car_model_val,
            "dtc_codes": req.dtc_val,
            "symptoms": req.symptom_val,
            "sensor_readings": { 'rpm': req.rpm_val, 'speed': req.speed_val, 'load': req.load_val, 'temp': req.temp_val }
        }
        
        diagnostic_history.save_diagnosis(structured_data)
        
        if logger:
            perf_logger.log_execution_time("Agent_Execution", duration_ms)
            
        return {
            "type": "conversational_diagnostic" if intent.is_follow_up else "structured",
            "data": structured_data,
            "duration_ms": duration_ms
        }
    except Exception as e:
        logger.error(f"Chat API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
