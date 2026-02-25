import base64
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class VisionInput(BaseModel):
    image_path: str = Field(description="The full path to the image file to analyze.")

def analyze_image(image_path: str) -> str:
    """Analyzes an image file and describes what vehicle issue it shows."""
    try:
        # Load the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # Initialize Vision Model (Gemini Flash supports images)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

        message = HumanMessage(
            content=[
                {"type": "text", "text": "You are a mechanic. Look at this image. If it is a dashboard icon, identify it. If it is a car part, identify the damage. Be specific."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
            ]
        )
        
        response = llm.invoke([message])
        return response.content
    except Exception as e:
        return f"Error analyzing image: {e}"

def get_vision_tool():
    return StructuredTool.from_function(
        func=analyze_image,
        name="vision_analysis",
        description="Use this tool when the user provides an image path. It analyzes dashboard lights or car parts.",
        args_schema=VisionInput
    )
