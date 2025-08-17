from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import base64
import io
import os
from PIL import Image
# Only Pixtral-related imports
try:
    import torch
    from transformers import AutoProcessor, AutoModelForVision2Text
    PIXTRAL_AVAILABLE = True
except Exception:
    PIXTRAL_AVAILABLE = False

app = FastAPI(title="EcoBee Intake & Perception API")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    type: str
    category: str
    materials: List[str]
    barcode: Optional[str]
    confidence: float

class IntakeResponse(BaseModel):
    items: List[Item]
    form_responses: Dict[str, str]

# Load Pixtral model optionally (controlled by environment variable)
PIXTRAL_MODEL = None
PIXTRAL_PROCESSOR = None
if PIXTRAL_AVAILABLE and os.getenv("ENABLE_PIXTRAL", "1") == "1":
    try:
        MODEL_NAME = os.getenv("PIXTRAL_MODEL_NAME", "mistralai/Pixtral-8B-v0.1")
        PIXTRAL_PROCESSOR = AutoProcessor.from_pretrained(MODEL_NAME)
        PIXTRAL_MODEL = AutoModelForVision2Text.from_pretrained(MODEL_NAME)
    except Exception as e:
        PIXTRAL_MODEL = None
        PIXTRAL_PROCESSOR = None


def read_barcode_with_pixtral(image_bytes: bytes) -> Optional[str]:
    if PIXTRAL_MODEL is None or PIXTRAL_PROCESSOR is None:
        return None
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    prompt = "What is the barcode number in this image? If none, say 'none'."
    inputs = PIXTRAL_PROCESSOR(images=image, text=prompt, return_tensors="pt")
    outputs = PIXTRAL_MODEL.generate(**inputs, max_length=32)
    description = PIXTRAL_PROCESSOR.decode(outputs[0], skip_special_tokens=True)
    # Try to extract a barcode-like number (sequence of 8+ digits)
    import re
    match = re.search(r"\b\d{8,}\b", description)
    if match:
        return match.group(0)
    if "none" in description.lower():
        return None
    return description.strip() if description.strip() else None

def classify_with_pixtral(image_bytes: bytes, item_type: str) -> Dict:
    # If not available, return a lightweight heuristic
    if PIXTRAL_MODEL is None or PIXTRAL_PROCESSOR is None:
        # fallback: very simple heuristics based on filename size or placeholder
        return {"category": item_type, "materials": [], "confidence": 0.5}

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    prompt = f"Classify this {item_type} image. What is the category and materials?"
    inputs = PIXTRAL_PROCESSOR(images=image, text=prompt, return_tensors="pt")
    outputs = PIXTRAL_MODEL.generate(**inputs, max_length=128)
    description = PIXTRAL_PROCESSOR.decode(outputs[0], skip_special_tokens=True)
    # Very simple parsing: attempt to extract comma-separated tokens
    # Real parsing should be more robust
    tokens = [t.strip() for t in description.replace('\n', ',').split(',') if t.strip()]
    category = tokens[0] if tokens else item_type
    materials = [t for t in tokens[1:4]] if len(tokens) > 1 else []
    return {"category": category, "materials": materials, "confidence": 0.9}

@app.post("/api/intake", response_model=IntakeResponse)
async def intake(
    item_type: str = Form(...),
    form_responses: str = Form(...),  # JSON string of form responses
    image: Optional[UploadFile] = File(None),
    barcode: Optional[str] = Form(None)
):
    """Accepts a form submission with optional image and barcode.
    Returns normalized items for the Scoring Engine.
    """
    import json
    form_data = json.loads(form_responses)
    items = []


    image_bytes = None
    if image is not None:
        contents = await image.read()
        image_bytes = contents
        # attempt barcode read with Pixtral if not provided
        if not barcode:
            try:
                bc = read_barcode_with_pixtral(contents)
                if bc:
                    barcode = bc
            except Exception:
                barcode = None

    classification = None
    if image_bytes:
        try:
            classification = classify_with_pixtral(image_bytes, item_type)
        except Exception:
            classification = {"category": item_type, "materials": [], "confidence": 0.5}
    else:
        classification = {"category": item_type, "materials": [], "confidence": 0.5}

    item = Item(
        type=item_type,
        category=classification["category"],
        materials=classification.get("materials", []),
        barcode=barcode,
        confidence=classification.get("confidence", 0.5)
    )
    items.append(item)

    return IntakeResponse(items=items, form_responses=form_data)

@app.get("/health")
async def health():
    """Health check endpoint with Pixtral status and model name."""
    return {
        "status": "ok",
        "pixtral_loaded": PIXTRAL_MODEL is not None,
        "pixtral_model": os.getenv("PIXTRAL_MODEL_NAME", "mistralai/Pixtral-8B-v0.1") if PIXTRAL_MODEL else None
    }

@app.post("/api/score")
async def score_endpoint(payload: Dict):
    """Compute EcoScore for submitted items."""
    from .ecoscore import score_batch
    items = payload.get('items', [])
    return score_batch(items)
