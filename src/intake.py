# ecoscore/intake.py
from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import requests
import json
from .normalise_map import canonicalise_food, canonicalise_fashion

router = APIRouter()

# --- Part 1: Hugging Face Dedicated Endpoint Configuration ---


HF_API_TOKEN = "hf" 
API_URL = "httpd" 

# Renamed prompts for clarity
LLAVA_PROMPT_MEAL = (
    "You are an expert classifying a MEAL image. "
    "Return ONLY a single, minified JSON object with the key 'diet'. "
    "The value should be a dictionary where keys are food categories and values are counts. "
    "Example: {\"diet\": {\"beef\": 1, \"rice\": 1}}"
)

LLAVA_PROMPT_OUTFIT = (
    "You are an expert classifying an OUTFIT image. "
    "Return ONLY a single, minified JSON object with the key 'fashion'. "
    "The value should be a dictionary where keys are clothing items and values are counts. "
    "Example: {\"fashion\": {\"tshirt\": 1, \"jeans\": 1}}"
)

def call_vision_model(img_bytes: bytes, prompt: str) -> Dict[str, Any]:
    """Sends an image and prompt to a dedicated Hugging Face Inference Endpoint."""
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    try:
        print(f"Sending request to Dedicated Endpoint: {API_URL}")
        response = requests.post(API_URL, headers=headers, data=img_bytes)
        response.raise_for_status()
        
        generated_text = response.json()[0].get('generated_text', '')
        print(f"Vision model raw response: {generated_text}")
        
        # Extract the JSON part from the model's full response string
        json_str = '{' + generated_text.split('{', 1)[-1].rsplit('}', 1)[0] + '}'
        
        return json.loads(json_str)

    except Exception as e:
        print(f"Error communicating with Dedicated Endpoint: {e}")
        return {}

# --- Part 2: Data Validation and Helper ---

class IntakeForm(BaseModel):
    diet: Dict[str, float] = Field(default_factory=dict)
    mobility: Dict[str, float] = Field(default_factory=dict)
    fashion: Dict[str, float] = Field(default_factory=dict)
    image_type: str = "meal"

def form_body(form: str = Form(...)):
    return IntakeForm.parse_raw(form)

# --- Part 3: The API Endpoint ---

@router.post("/api/intake")
async def intake(
    form: IntakeForm = Depends(form_body),
    image: Optional[UploadFile] = File(default=None),
) -> Dict[str, Any]:
    
    diet = {canonicalise_food(k): v for k, v in form.diet.items() if v > 0}
    fashion = {canonicalise_fashion(k): v for k, v in form.fashion.items() if v > 0}
    mobility = dict(form.mobility)

    if image is not None:
        img_bytes = await image.read()
        
        prompt_to_use = LLAVA_PROMPT_MEAL
        if form.image_type == "outfit":
            prompt_to_use = LLAVA_PROMPT_OUTFIT
            
        vision_output = call_vision_model(img_bytes, prompt_to_use)
        
        if form.image_type == "meal":
            for k, v in vision_output.get("diet", {}).items():
                diet[canonicalise_food(k)] = diet.get(canonicalise_food(k), 0) + v
        elif form.image_type == "outfit":
            for k, v in vision_output.get("fashion", {}).items():
                fashion[canonicalise_fashion(k)] = fashion.get(canonicalise_fashion(k), 0) + v
            
    payload = {
        "diet": diet,
        "mobility": mobility,
        "fashion": fashion,
        "meta": {"source": "form+image" if image else "form"}
    }
    
    return payload
