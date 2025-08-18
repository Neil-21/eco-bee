from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import base64
import io
import os
import json
from PIL import Image
from datetime import datetime
import uuid

# Enhanced imports
from ecoscore import calculate_ecoscore, score_item, PLANETARY_BOUNDARIES
from product_database import get_product_info, get_sustainability_alternatives, product_db
from recommender import get_recommendations, get_action_info, get_campus_resources
from barcode_scanner import create_scanner  # Add barcode scanner import

# Vision model imports
try:
    import torch
    from transformers import AutoProcessor, AutoModelForVision2Text
    PIXTRAL_AVAILABLE = True
except Exception:
    PIXTRAL_AVAILABLE = False

app = FastAPI(title="EcoBee Intake & Perception API", version="2.0.0")

# Enhanced CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced data models
class QuizResponse(BaseModel):
    question_id: str
    question_text: str
    answer: Union[str, List[str]]
    category: str

class Item(BaseModel):
    type: str = Field(..., description="Type of item (food, clothing, transport)")
    category: str = Field(..., description="Category within the type")
    materials: List[str] = Field(default=[], description="Materials or composition")
    barcode: Optional[str] = Field(None, description="Product barcode if available")

class ChatMessage(BaseModel):
    message: str = Field(..., description="User message to the chatbot")
    context: str = Field(default="sustainability", description="Context for the conversation")
    confidence: float = Field(0.5, description="Classification confidence")
    source: str = Field("user", description="Source of classification (user, vision, barcode)")
    product_info: Optional[Dict] = Field(None, description="Additional product information")

class IntakeRequest(BaseModel):
    quiz_responses: List[QuizResponse]
    items: List[Item] = Field(default=[], description="Items to score")
    session_id: Optional[str] = Field(None, description="Session identifier")
    user_id: Optional[str] = Field(None, description="User identifier")

class BoundaryScore(BaseModel):
    climate: float
    biosphere: float
    biogeochemical: float
    freshwater: float
    aerosols: float

class ScoringResult(BaseModel):
    items: List[Dict]
    per_boundary_averages: BoundaryScore
    composite: float
    grade: str
    recommendations: List[Dict]
    boundary_details: Dict

class IntakeResponse(BaseModel):
    items: List[Item]
    quiz_responses: List[QuizResponse]
    scoring_result: Optional[ScoringResult]
    session_id: str
    timestamp: datetime
    alternatives: Optional[List[Dict]] = None

class ImageClassificationRequest(BaseModel):
    image_data: str = Field(..., description="Base64 encoded image")
    item_type: str = Field(..., description="Expected item type (food, clothing)")
    context: Optional[str] = Field(None, description="Additional context for classification")

class BarcodeRequest(BaseModel):
    barcode: str = Field(..., description="Product barcode")
    product_type: Optional[str] = Field(None, description="Expected product type")

# Load vision models
PIXTRAL_MODEL = None
PIXTRAL_PROCESSOR = None
if PIXTRAL_AVAILABLE and os.getenv("ENABLE_PIXTRAL", "1") == "1":
    try:
        MODEL_NAME = os.getenv("PIXTRAL_MODEL_NAME", "mistralai/Pixtral-8B-v0.1")
        print(f"Loading Pixtral model: {MODEL_NAME}")
        PIXTRAL_PROCESSOR = AutoProcessor.from_pretrained(MODEL_NAME)
        PIXTRAL_MODEL = AutoModelForVision2Text.from_pretrained(MODEL_NAME)
        print("Pixtral model loaded successfully")
    except Exception as e:
        print(f"Failed to load Pixtral model: {e}")
        PIXTRAL_MODEL = None
        PIXTRAL_PROCESSOR = None

# Initialize barcode scanner
try:
    BARCODE_SCANNER = create_scanner()
    print("✅ Barcode scanner initialized")
except Exception as e:
    print(f"⚠️  Failed to initialize barcode scanner: {e}")
    BARCODE_SCANNER = None

def enhanced_classify_with_pixtral(image_bytes: bytes, item_type: str, context: str = "") -> Dict:
    """Enhanced classification using Pixtral with better prompting"""
    if PIXTRAL_MODEL is None or PIXTRAL_PROCESSOR is None:
        return fallback_classification(item_type)

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Enhanced prompts for different item types
        prompts = {
            "food": f"Analyze this food image. Identify: 1) Food category (plant-based, mixed, meat-heavy, snack, drink, packaged, organic), 2) Main ingredients/materials, 3) Processing level. {context}",
            "clothing": f"Analyze this clothing item. Identify: 1) Material type (cotton, polyester, wool, linen, leather, recycled, synthetic), 2) Fabric composition, 3) Manufacturing quality indicators. {context}",
            "meal": f"Analyze this meal image. Identify: 1) Meal type (plant-based, mixed, meat-heavy), 2) Main ingredients, 3) Portion size and preparation method. {context}",
            "outfit": f"Analyze this outfit/clothing. Identify: 1) Primary materials (cotton, synthetic, natural, mixed), 2) Manufacturing indicators, 3) Quality/durability signs. {context}"
        }
        
        prompt = prompts.get(item_type, prompts["food"])
        
        inputs = PIXTRAL_PROCESSOR(images=image, text=prompt, return_tensors="pt")
        outputs = PIXTRAL_MODEL.generate(**inputs, max_length=256, do_sample=True, temperature=0.3)
        description = PIXTRAL_PROCESSOR.decode(outputs[0], skip_special_tokens=True)
        
        return parse_classification_response(description, item_type)
    
    except Exception as e:
        print(f"Pixtral classification error: {e}")
        return fallback_classification(item_type)

def parse_classification_response(description: str, item_type: str) -> Dict:
    """Parse Pixtral response into structured classification"""
    description_lower = description.lower()
    
    # Category classification based on item type
    if item_type in ["food", "meal"]:
        categories = ["plant-based", "mixed", "meat-heavy", "snack", "drink", "packaged", "organic"]
        category = "mixed"  # default
        
        for cat in categories:
            if cat.replace("-", " ") in description_lower or cat in description_lower:
                category = cat
                break
        
        # Detect materials/ingredients
        food_materials = []
        food_keywords = {
            "vegetable": "vegetables", "fruit": "fruits", "meat": "meat",
            "chicken": "chicken", "beef": "beef", "pork": "pork",
            "fish": "fish", "dairy": "dairy", "grain": "grains",
            "organic": "organic", "processed": "processed"
        }
        
        for keyword, material in food_keywords.items():
            if keyword in description_lower:
                food_materials.append(material)
    
    elif item_type in ["clothing", "outfit"]:
        categories = ["cotton", "polyester", "wool", "linen", "leather", "recycled", "synthetic"]
        category = "synthetic"  # default
        
        for cat in categories:
            if cat in description_lower:
                category = cat
                break
        
        # Detect materials
        clothing_materials = []
        clothing_keywords = {
            "cotton": "cotton", "polyester": "polyester", "wool": "wool",
            "linen": "linen", "leather": "leather", "denim": "denim",
            "silk": "silk", "synthetic": "synthetic", "recycled": "recycled",
            "organic": "organic"
        }
        
        for keyword, material in clothing_keywords.items():
            if keyword in description_lower:
                clothing_materials.append(material)
        
        food_materials = clothing_materials
    
    else:
        category = item_type
        food_materials = []
    
    confidence = 0.85 if len(food_materials) > 0 else 0.6
    
    return {
        "category": category,
        "materials": food_materials[:3],  # Limit to 3 materials
        "confidence": confidence,
        "raw_description": description[:200]  # Truncate for storage
    }

def fallback_classification(item_type: str) -> Dict:
    """Fallback classification when vision model is unavailable"""
    fallback_categories = {
        "food": "mixed",
        "meal": "mixed", 
        "clothing": "synthetic",
        "outfit": "synthetic",
        "transport": "car",
        "mobility": "car"
    }
    
    return {
        "category": fallback_categories.get(item_type, "mixed"),
        "materials": [],
        "confidence": 0.3,
        "raw_description": "Fallback classification - vision model unavailable"
    }

def read_barcode_with_pixtral(image_bytes: bytes) -> Optional[str]:
    """Enhanced barcode reading with Pixtral"""
    if PIXTRAL_MODEL is None or PIXTRAL_PROCESSOR is None:
        return None
    
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        prompt = "Look for any barcodes, QR codes, or product codes in this image. Extract the exact numeric sequence. If you see a barcode, provide only the numbers. If no barcode is visible, respond with 'none'."
        
        inputs = PIXTRAL_PROCESSOR(images=image, text=prompt, return_tensors="pt")
        outputs = PIXTRAL_MODEL.generate(**inputs, max_length=64, temperature=0.1)
        description = PIXTRAL_PROCESSOR.decode(outputs[0], skip_special_tokens=True)
        
        # Extract barcode-like sequences
        import re
        matches = re.findall(r'\b\d{8,14}\b', description)
        if matches:
            return matches[0]  # Return first valid barcode
        
        if "none" in description.lower() or "no barcode" in description.lower():
            return None
            
        return None
    
    except Exception as e:
        print(f"Barcode reading error: {e}")
        return None

@app.post("/api/intake", response_model=IntakeResponse)
async def enhanced_intake(
    request: IntakeRequest
):
    """Enhanced intake endpoint with comprehensive scoring"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # Process items and calculate scores
    items_for_scoring = []
    for item in request.items:
        item_dict = {
            "type": item.type,
            "category": item.category,
            "materials": item.materials,
            "barcode": item.barcode
        }
        items_for_scoring.append(item_dict)
    
    # Calculate EcoScore
    scoring_result = None
    if items_for_scoring:
        score_data = calculate_ecoscore(items_for_scoring)
        scoring_result = ScoringResult(
            items=score_data["items"],
            per_boundary_averages=BoundaryScore(**score_data["per_boundary_averages"]),
            composite=score_data["composite"],
            grade=score_data["grade"],
            recommendations=score_data["recommendations"],
            boundary_details=score_data["boundary_details"]
        )
    
    # Get alternatives for barcoded items
    alternatives = []
    for item in request.items:
        if item.barcode:
            item_alternatives = get_sustainability_alternatives(item.barcode)
            if item_alternatives:
                alternatives.extend(item_alternatives)
    
    return IntakeResponse(
        items=request.items,
        quiz_responses=request.quiz_responses,
        scoring_result=scoring_result,
        session_id=session_id,
        timestamp=datetime.now(),
        alternatives=alternatives if alternatives else None
    )

@app.post("/api/classify-image")
async def classify_image(
    image: UploadFile = File(...),
    item_type: str = Form(...),
    context: str = Form("")
):
    """Classify uploaded image using vision AI"""
    try:
        contents = await image.read()
        classification = enhanced_classify_with_pixtral(contents, item_type, context)
        
        # Try to read barcode if present
        barcode = read_barcode_with_pixtral(contents)
        
        # Get product info if barcode found
        product_info = None
        if barcode:
            product_info = get_product_info(barcode)
            if product_info:
                # Update classification with product data
                classification["category"] = product_info.get("category", classification["category"])
                classification["materials"] = product_info.get("materials", classification["materials"])
                classification["confidence"] = 0.95
        
        return {
            "classification": classification,
            "barcode": barcode,
            "product_info": product_info,
            "source": "pixtral" if PIXTRAL_MODEL else "fallback"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image classification failed: {str(e)}")

@app.post("/api/barcode-lookup")
async def barcode_lookup(request: BarcodeRequest):
    """Look up product information by barcode"""
    product_info = get_product_info(request.barcode)
    
    if not product_info:
        raise HTTPException(status_code=404, detail="Product not found")
    
    alternatives = get_sustainability_alternatives(request.barcode)
    
    return {
        "product": product_info,
        "alternatives": alternatives,
        "barcode": request.barcode
    }

@app.post("/api/scan-barcode")
async def scan_barcode(image: UploadFile = File(...), product_type: str = Form("food")):
    """Scan barcode from uploaded image using Pixtral or fallback scanner"""
    try:
        # Read image data
        image_data = await image.read()
        
        # Try to scan with dedicated barcode scanner first
        if BARCODE_SCANNER:
            try:
                print(f"🔍 Attempting to scan with dedicated barcode scanner...")
                scan_result = BARCODE_SCANNER.scan_barcode_from_image(image_data, product_type)
                print(f"📊 Scan result: {scan_result}")
                
                # If successful and barcode found, return the result
                if scan_result.get("success") and scan_result.get("barcode"):
                    print(f"✅ Barcode scan successful: {scan_result.get('barcode')}")
                    return {
                        "success": True,
                        "barcode": scan_result["barcode"],
                        "product_info": scan_result.get("product_info"),
                        "sustainability": scan_result.get("sustainability"),
                        "product_details": scan_result.get("product_details"),
                        "scanner": "pixtral_api",
                        "confidence": scan_result.get("product_info", {}).get("confidence", 0.5)
                    }
                else:
                    print(f"❌ Barcode scan failed or no barcode found: {scan_result}")
            except Exception as e:
                print(f"❌ Dedicated scanner failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to integrated Pixtral model
        barcode = read_barcode_with_pixtral(image_data)
        
        if barcode:
            # Look up product information
            product_info = get_product_info(barcode)
            alternatives = get_sustainability_alternatives(barcode) if product_info else []
            
            return {
                "success": True,
                "barcode": barcode,
                "product_info": product_info,
                "alternatives": alternatives,
                "scanner": "pixtral_local",
                "confidence": 0.8 if product_info else 0.5
            }
        else:
            return {
                "success": False,
                "error": "No barcode detected in image",
                "barcode": None,
                "product_info": None,
                "scanner": "pixtral_local"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode scanning failed: {str(e)}")

@app.post("/api/scan-barcode-base64")
async def scan_barcode_base64(request: Dict):
    """Scan barcode from base64 encoded image"""
    try:
        image_data = request.get("image_data", "")
        product_type = request.get("product_type", "food")
        
        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid base64 image data")
        
        # Try to scan with dedicated barcode scanner first
        if BARCODE_SCANNER:
            try:
                scan_result = BARCODE_SCANNER.scan_barcode_from_image(image_bytes, product_type)
                
                if scan_result.get("success") and scan_result.get("barcode"):
                    return {
                        "success": True,
                        "barcode": scan_result["barcode"],
                        "product_info": scan_result.get("product_info"),
                        "sustainability": scan_result.get("sustainability"),
                        "product_details": scan_result.get("product_details"),
                        "scanner": "pixtral_api",
                        "confidence": scan_result.get("product_info", {}).get("confidence", 0.5)
                    }
            except Exception as e:
                print(f"Dedicated scanner failed: {e}")
        
        # Fallback to integrated Pixtral model
        barcode = read_barcode_with_pixtral(image_bytes)
        
        if barcode:
            # Look up product information
            product_info = get_product_info(barcode)
            alternatives = get_sustainability_alternatives(barcode) if product_info else []
            
            return {
                "success": True,
                "barcode": barcode,
                "product_info": product_info,
                "alternatives": alternatives,
                "scanner": "pixtral_local",
                "confidence": 0.8 if product_info else 0.5
            }
        else:
            return {
                "success": False,
                "error": "No barcode detected in image",
                "barcode": None,
                "product_info": None,
                "scanner": "pixtral_local"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Barcode scanning failed: {str(e)}")

@app.post("/api/score")
async def score_endpoint(payload: Dict):
    """Enhanced scoring endpoint using new calculate_ecoscore function"""
    items = payload.get('items', [])
    if not items:
        raise HTTPException(status_code=400, detail="No items provided for scoring")
    
    return calculate_ecoscore(items)

@app.get("/api/boundaries")
async def get_boundaries():
    """Get planetary boundaries information"""
    return {
        "boundaries": PLANETARY_BOUNDARIES,
        "description": "Planetary boundaries represent Earth's safe operating space"
    }

@app.get("/api/products/search")
async def search_products(q: str, product_type: Optional[str] = None, limit: int = 10):
    """Search products in database"""
    results = product_db.search_products(q, product_type)
    return {
        "query": q,
        "results": [{"barcode": barcode, "product": product} for barcode, product in results[:limit]]
    }

@app.get("/health")
async def health():
    """Enhanced health check with detailed status"""
    return {
        "status": "ok",
        "version": "2.0.0",
        "features": {
            "pixtral_loaded": PIXTRAL_MODEL is not None,
            "pixtral_model": os.getenv("PIXTRAL_MODEL_NAME", "mistralai/Pixtral-8B-v0.1") if PIXTRAL_MODEL else None,
            "product_database": len(product_db.products),
            "planetary_boundaries": len(PLANETARY_BOUNDARIES)
        },
        "endpoints": [
            "/api/intake",
            "/api/classify-image", 
            "/api/barcode-lookup",
            "/api/score",
            "/api/boundaries",
            "/api/products/search"
        ]
    }

# Legacy endpoint for backwards compatibility
@app.post("/api/intake-legacy")
async def intake_legacy(
    item_type: str = Form(...),
    form_responses: str = Form(...),
    image: Optional[UploadFile] = File(None),
    barcode: Optional[str] = Form(None)
):
    """Legacy intake endpoint for backwards compatibility"""
    import json
    
    try:
        form_data = json.loads(form_responses)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form_responses")
    
    items = []
    image_bytes = None
    
    if image is not None:
        contents = await image.read()
        image_bytes = contents
        
        # Try barcode reading if not provided
        if not barcode:
            try:
                detected_barcode = read_barcode_with_pixtral(contents)
                if detected_barcode:
                    barcode = detected_barcode
            except Exception as e:
                print(f"Barcode detection failed: {e}")

    # Classify image if available
    classification = None
    if image_bytes:
        try:
            classification = enhanced_classify_with_pixtral(image_bytes, item_type)
        except Exception as e:
            print(f"Image classification failed: {e}")
            classification = fallback_classification(item_type)
    else:
        classification = fallback_classification(item_type)

    # Create item
    item = Item(
        type=item_type,
        category=classification["category"],
        materials=classification.get("materials", []),
        barcode=barcode,
        confidence=classification.get("confidence", 0.5),
        source="vision" if image_bytes else "user"
    )
    items.append(item)

    return {
        "items": [item.dict() for item in items],
        "form_responses": form_data,
        "classification_details": classification
    }

# New endpoints for EcoBee features

@app.get("/api/leaderboard")
async def get_leaderboard_endpoint(limit: int = 50, boundary: Optional[str] = None):
    """Get EcoScore leaderboard with privacy protection"""
    try:
        leaderboard_data = product_db.get_leaderboard(limit=limit, boundary_filter=boundary)
        return leaderboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving leaderboard: {str(e)}")

@app.post("/api/submit-score")
async def submit_score_endpoint(payload: Dict):
    """Submit EcoScore to leaderboard"""
    try:
        user_id = payload.get('user_id')
        composite_score = payload.get('composite_score')
        boundary_scores = payload.get('boundary_scores', {})
        campus_affiliation = payload.get('campus_affiliation')
        
        if not user_id or composite_score is None:
            raise HTTPException(status_code=400, detail="user_id and composite_score are required")
        
        result = product_db.submit_score(
            user_id=user_id,
            composite_score=composite_score,
            boundary_scores=boundary_scores,
            campus_affiliation=campus_affiliation
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting score: {str(e)}")

@app.get("/api/recommendations")
async def get_recommendations_endpoint(
    climate: float = 50,
    biosphere: float = 50,
    biogeochemical: float = 50,
    freshwater: float = 50,
    aerosols: float = 50,
    difficulty: str = "easy",
    time_availability: str = "daily",
    budget: str = "free",
    social: bool = True,
    is_student: bool = True
):
    """Get personalized action recommendations based on boundary scores"""
    try:
        boundary_scores = {
            "climate": climate,
            "biosphere": biosphere,
            "biogeochemical": biogeochemical,
            "freshwater": freshwater,
            "aerosols": aerosols
        }
        
        user_context = {
            "difficulty_preference": difficulty,
            "time_availability": time_availability,
            "budget_preference": budget,
            "social_preference": social,
            "is_student": is_student
        }
        
        recommendations = get_recommendations(boundary_scores, user_context)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/api/actions/{action_id}")
async def get_action_endpoint(action_id: str):
    """Get detailed information about a specific action"""
    try:
        action_details = get_action_info(action_id)
        if not action_details:
            raise HTTPException(status_code=404, detail="Action not found")
        return action_details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving action: {str(e)}")

@app.get("/api/resources")
async def get_resources_endpoint():
    """Get all campus and local sustainability resources"""
    try:
        resources = get_campus_resources()
        return {"resources": resources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resources: {str(e)}")

@app.post("/api/chat")
async def chat_with_sustainability_bot(chat_message: ChatMessage):
    """Chat endpoint for sustainability questions using Mistral AI"""
    try:
        # For now, provide intelligent responses based on common sustainability topics
        # In production, this would integrate with Mistral AI API
        
        message_lower = chat_message.message.lower()
        
        # Sustainability topic responses
        if any(word in message_lower for word in ["food waste", "waste"]):
            response = """Here are some effective ways to reduce food waste:

🥗 **Meal Planning**: Plan your meals for the week and make a shopping list
📦 **Proper Storage**: Store fruits and vegetables correctly to extend freshness
🥡 **Creative Leftovers**: Transform leftovers into new meals
🗓️ **Check Expiry Dates**: Use older items first (FIFO - First In, First Out)
🧊 **Freeze Before Spoiling**: Freeze bread, meat, and other perishables
♻️ **Compost**: Turn unavoidable food scraps into nutrient-rich soil

Did you know? Reducing food waste is one of the most impactful things you can do for the planet!"""

        elif any(word in message_lower for word in ["protein", "meat", "plant"]):
            response = """Great question about sustainable proteins! Here's what the science shows:

🌱 **Most Sustainable**: Legumes (beans, lentils, chickpeas), nuts, seeds
🐟 **Moderately Sustainable**: Small fish, shellfish, sustainably sourced seafood
🐔 **Lower Impact Meat**: Chicken, turkey (much lower footprint than beef)
🥛 **Dairy Alternatives**: Oat, soy, almond milk have lower environmental impact
🥩 **Highest Impact**: Beef, lamb (but grass-fed can be better)

💡 **Pro tip**: Even reducing meat consumption by 1-2 days per week makes a significant difference! Try "Meatless Monday" or "Plant-based Wednesday"."""

        elif any(word in message_lower for word in ["packaging", "plastic", "container"]):
            response = """Understanding sustainable packaging is crucial! Here's what to look for:

✅ **Best Options**:
- Minimal/no packaging (bulk bins, farmers markets)
- Glass containers (infinitely recyclable)
- Paper/cardboard (from recycled content)
- Compostable materials (certified biodegradable)

⚠️ **Be Careful With**:
- "Biodegradable" plastic (often needs industrial composting)
- Black plastic (hard to recycle)
- Mixed materials (hard to separate for recycling)

🔄 **Action Steps**:
- Bring reusable bags and containers
- Choose products with minimal packaging
- Support companies with refillable containers
- Check local recycling guidelines"""

        elif any(word in message_lower for word in ["planet", "environment", "impact", "carbon"]):
            response = """The planetary boundaries framework helps us understand environmental limits:

🌡️ **Climate Change**: Reduce energy use, choose renewable energy
🌿 **Biodiversity**: Support regenerative agriculture, reduce habitat destruction
💧 **Water Cycles**: Conserve water, support sustainable farming
🌱 **Nutrient Cycles**: Reduce fertilizer use, support organic farming
🌫️ **Air Quality**: Choose low-emission transport, reduce consumption

🎯 **Your Impact**: Every choice matters! Food choices have some of the biggest environmental impacts in our daily lives."""

        elif any(word in message_lower for word in ["label", "certification", "organic"]):
            response = """Here's how to decode sustainability labels:

🌱 **Trusted Certifications**:
- USDA Organic (no synthetic pesticides/fertilizers)
- Fair Trade (ethical labor practices)
- Rainforest Alliance (biodiversity protection)
- MSC (sustainable seafood)
- B-Corp (holistic sustainability)

⚠️ **Watch Out For**:
- "Natural" (not regulated, can be misleading)
- "Eco-friendly" without certification
- Vague terms like "better for you"

💡 **Pro tip**: Look for specific, third-party certifications rather than marketing terms!"""

        elif any(word in message_lower for word in ["diet", "eating", "food choices"]):
            response = """Creating a planet-friendly diet is easier than you think:

🥬 **The Planetary Health Diet**:
- Fill half your plate with vegetables and fruits
- Choose whole grains over refined
- Include nuts, seeds, and legumes
- Moderate amounts of fish and poultry
- Limit red meat and processed foods

🌍 **Environmental Benefits**:
- 50% less greenhouse gas emissions
- Reduced land and water use
- Lower pollution and biodiversity loss

🍽️ **Practical Steps**:
- Start with one plant-based meal per day
- Try new vegetables and cuisines
- Buy local and seasonal when possible
- Reduce food waste"""

        else:
            # Generic sustainability response
            response = f"""That's a great sustainability question! Here are some key principles to consider:

🌱 **Think Systems**: Every choice connects to larger environmental systems
📊 **Measure Impact**: Look for data on carbon footprint, water use, and biodiversity
🔄 **Circular Economy**: Choose reusable, recyclable, or compostable options
🏪 **Support Better Businesses**: Choose companies with transparent sustainability practices
👥 **Community Action**: Individual actions multiply when shared with others

For your specific question about "{chat_message.message}", I'd recommend:
- Researching certified sustainable options
- Looking at lifecycle impacts
- Starting with small, consistent changes
- Connecting with local sustainability groups

Is there a specific aspect of sustainability you'd like to explore further?"""

        return {"response": response}
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {"response": "I'm sorry, I'm having trouble right now. Please try again later, or check if the backend server is running properly."}

@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint with component status"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "planetary_boundaries_scoring",
            "multi_modal_intake", 
            "recommendation_engine",
            "leaderboard_system",
            "vision_classification",
            "barcode_scanning",
            "sustainability_database",
            "campus_resources"
        ],
        "components": {
            "pixtral_model_loaded": PIXTRAL_MODEL is not None,
            "barcode_scanner_available": BARCODE_SCANNER is not None,
            "product_database_loaded": product_db is not None,
            "recommender_engine": True,
            "ecoscore_calculator": True
        },
        "pixtral_model": os.getenv("PIXTRAL_MODEL_NAME", "mistralai/Pixtral-8B-v0.1") if PIXTRAL_MODEL else None,
        "endpoints": [
            "/api/intake", "/api/score", "/api/scan-barcode", "/api/scan-barcode-base64",
            "/api/barcode-lookup", "/api/classify-image", "/api/leaderboard", 
            "/api/submit-score", "/api/recommendations", "/api/resources", "/api/chat"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
