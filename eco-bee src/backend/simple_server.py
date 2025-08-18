#!/usr/bin/env python3
"""
Simple HTTP server for the EcoBee Intake & Perception API
This runs without FastAPI/uvicorn dependencies using only Python standard library
Includes Pixtral-based barcode scanning capabilities
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
try:
    import cgi
except ImportError:
    # Fallback for Python 3.13+ when cgi is removed
    cgi = None
import tempfile
from typing import Dict, Any

# Import barcode scanner
try:
    from barcode_scanner import create_scanner
    BARCODE_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Barcode scanner not available: {e}")
    BARCODE_SCANNER_AVAILABLE = False

class IntakeHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Initialize barcode scanner if available
        self.scanner = None
        if BARCODE_SCANNER_AVAILABLE:
            try:
                self.scanner = create_scanner()
            except Exception as e:
                print(f"⚠️  Failed to initialize barcode scanner: {e}")
        super().__init__(*args, **kwargs)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_json_response({
                "status": "ok", 
                "pixtral_loaded": BARCODE_SCANNER_AVAILABLE and self.scanner is not None,
                "message": "Simple server running with Pixtral barcode scanner" if BARCODE_SCANNER_AVAILABLE else "Simple server running - Pixtral disabled"
            })
        else:
            self.send_json_response({"error": "Not found"}, status=404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/intake':
            self.handle_intake()
        elif self.path == '/api/score':
            self.handle_score()
        elif self.path == '/api/scan-barcode':
            self.handle_barcode_scan()
        elif self.path == '/api/product-sustainability':
            self.handle_product_sustainability()
        else:
            self.send_json_response({"error": "Not found"}, status=404)
    
    def handle_intake(self):
        """Handle intake form submission - Returns normalized item list for Scoring Engine"""
        try:
            print("📥 Processing intake form submission...")
            
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse the form data
            if self.headers.get('Content-Type', '').startswith('multipart/form-data'):
                # Simple multipart parsing - in a real app you'd use a proper parser
                data_str = post_data.decode('utf-8')
                
                # Extract form fields
                item_type = self.extract_form_field(data_str, 'item_type') or 'meal'
                form_responses = self.extract_form_field(data_str, 'form_responses') or '{}'
                food_barcode = self.extract_form_field(data_str, 'food_barcode') or ''
                clothing_barcode = self.extract_form_field(data_str, 'clothing_barcode') or ''
                
                try:
                    form_data = json.loads(form_responses)
                except:
                    form_data = {}
                
                print(f"📊 Extracted form data: {form_data}")
                
                # Normalize the data into structured items for scoring
                normalized_items = self.normalize_intake_data(form_data, food_barcode, clothing_barcode)
                
                # Generate analysis and scoring
                analysis = self.generate_comprehensive_analysis(normalized_items, form_data)
                eco_score = self.calculate_comprehensive_eco_score(normalized_items, form_data)
                
                response = {
                    "success": True,
                    "normalized_items": normalized_items,  # For deliverable compliance
                    "items": normalized_items,  # For frontend compatibility
                    "comprehensive_analysis": analysis,  # Enhanced analysis
                    "analysis": analysis,  # For frontend compatibility
                    "eco_score": eco_score,  # Enhanced scoring
                    "score": {  # Legacy compatibility
                        "total": eco_score.get("overall_score", 0),
                        "level": eco_score.get("grade", "N/A"),
                        "breakdown": {
                            "food_choices": eco_score.get("category_scores", {}).get("meal", 0),
                            "transportation": eco_score.get("category_scores", {}).get("transportation", 0),
                            "daily_actions": eco_score.get("category_scores", {}).get("environmental_actions", 0),
                            "clothing": eco_score.get("category_scores", {}).get("clothing", 0),
                            "reflection": 0  # Not calculated in new system
                        }
                    },
                    "metadata": {
                        "submission_type": "intake_form",
                        "processed_at": self.get_timestamp(),
                        "total_items": len(normalized_items),
                        "categories": list(set([item["category"] for item in normalized_items]))
                    }
                }
                
                print(f"✅ Normalized {len(normalized_items)} items for scoring engine")
                self.send_json_response(response)
                
            else:
                # Handle JSON payload
                try:
                    json_data = json.loads(post_data.decode('utf-8'))
                    form_data = json_data.get('form_responses', json_data)
                    food_barcode = json_data.get('food_barcode', '')
                    clothing_barcode = json_data.get('clothing_barcode', '')
                    
                    # Normalize the JSON data
                    normalized_items = self.normalize_intake_data(form_data, food_barcode, clothing_barcode)
                    analysis = self.generate_comprehensive_analysis(normalized_items, form_data)
                    eco_score = self.calculate_comprehensive_eco_score(normalized_items, form_data)
                    
                    response = {
                        "success": True,
                        "normalized_items": normalized_items,  # For deliverable compliance
                        "items": normalized_items,  # For frontend compatibility
                        "comprehensive_analysis": analysis,  # Enhanced analysis
                        "analysis": analysis,  # For frontend compatibility
                        "eco_score": eco_score,  # Enhanced scoring
                        "score": {  # Legacy compatibility
                            "total": eco_score.get("overall_score", 0),
                            "level": eco_score.get("grade", "N/A"),
                            "breakdown": {
                                "food_choices": eco_score.get("category_scores", {}).get("meal", 0),
                                "transportation": eco_score.get("category_scores", {}).get("transportation", 0),
                                "daily_actions": eco_score.get("category_scores", {}).get("environmental_actions", 0),
                                "clothing": eco_score.get("category_scores", {}).get("clothing", 0),
                                "reflection": 0  # Not calculated in new system
                            }
                        },
                        "metadata": {
                            "submission_type": "json_api",
                            "processed_at": self.get_timestamp(),
                            "total_items": len(normalized_items),
                            "categories": list(set([item["category"] for item in normalized_items]))
                        }
                    }
                    
                    self.send_json_response(response)
                    
                except json.JSONDecodeError:
                    self.send_json_response({"error": "Invalid JSON data"}, status=400)
                    
        except Exception as e:
            print(f"❌ Error processing intake: {str(e)}")
            self.send_json_response({"error": f"Server error: {str(e)}"}, status=500)
    
    def handle_score(self):
        """Handle score calculation"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Mock scoring - calculate based on number of items and sustainability
            items = data.get('items', [])
            score = 50  # Base score
            
            for item in items:
                if 'plant' in item.get('category', '').lower():
                    score += 20
                elif 'sustainable' in item.get('category', '').lower():
                    score += 15
                else:
                    score += 5
            
            response = {
                "total_score": min(score, 100),
                "breakdown": {
                    "sustainability": score * 0.6,
                    "awareness": score * 0.4
                },
                "recommendations": [
                    "Try more plant-based options",
                    "Consider sustainable materials",
                    "Keep tracking your choices!"
                ]
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({"error": f"Scoring error: {str(e)}"}, status=500)
    
    def handle_barcode_scan(self):
        """Handle barcode scanning requests"""
        try:
            if not BARCODE_SCANNER_AVAILABLE or not self.scanner:
                self.send_json_response({
                    "success": False,
                    "error": "Barcode scanner not available. Please install required dependencies (Pillow, requests, mistralai) and set MISTRAL_API_KEY environment variable.",
                    "barcode": None,
                    "product_info": None
                }, status=503)
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Default product type
            product_type = "food"
            
            # Check if it's multipart form data (image upload)
            if self.headers.get('Content-Type', '').startswith('multipart/form-data'):
                if cgi is None:
                    self.send_json_response({
                        "success": False,
                        "error": "Multipart form data parsing not available in this Python version",
                        "barcode": None,
                        "product_info": None
                    }, status=500)
                    return
                
                # Parse multipart form data
                boundary = self.headers.get('Content-Type').split('boundary=')[1]
                env = os.environ.copy()
                env['REQUEST_METHOD'] = 'POST'
                env['CONTENT_TYPE'] = self.headers.get('Content-Type')
                env['CONTENT_LENGTH'] = str(content_length)
                
                # Create a temporary file for the form data
                with tempfile.NamedTemporaryFile() as tmp:
                    tmp.write(post_data)
                    tmp.seek(0)
                    
                    # Parse form data
                    form = cgi.FieldStorage(
                        fp=tmp,
                        environ=env,
                        keep_blank_values=True
                    )
                    
                    # Extract product_type if present
                    if 'product_type' in form:
                        product_type = form['product_type'].value
                    
                    # Look for image field
                    if 'image' in form:
                        image_field = form['image']
                        if image_field.file:
                            image_data = image_field.file.read()
                            
                            # Scan barcode using Pixtral
                            result = self.scanner.scan_barcode_from_image(image_data, product_type)
                            self.send_json_response(result)
                            return
                    
                    # If no image found in form
                    self.send_json_response({
                        "success": False,
                        "error": "No image found in form data",
                        "barcode": None,
                        "product_info": None
                    }, status=400)
                    
            else:
                # Handle JSON payload with base64 image
                try:
                    json_data = json.loads(post_data.decode('utf-8'))
                    
                    # Extract product_type if present
                    if 'product_type' in json_data:
                        product_type = json_data['product_type']
                    
                    if 'image_base64' in json_data:
                        base64_image = json_data['image_base64']
                        
                        # Remove data URL prefix if present
                        if base64_image.startswith('data:image'):
                            base64_image = base64_image.split(',')[1]
                        
                        # Scan barcode using Pixtral
                        result = self.scanner.scan_barcode_from_base64(base64_image, product_type)
                        self.send_json_response(result)
                    else:
                        self.send_json_response({
                            "success": False,
                            "error": "No image_base64 field found in JSON data",
                            "barcode": None,
                            "product_info": None
                        }, status=400)
                        
                except json.JSONDecodeError:
                    self.send_json_response({
                        "success": False,
                        "error": "Invalid JSON data",
                        "barcode": None,
                        "product_info": None
                    }, status=400)
                    
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": f"Barcode scanning error: {str(e)}",
                "barcode": None,
                "product_info": None
            }, status=500)
    
    def handle_product_sustainability(self):
        """Handle product sustainability lookup by barcode"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                json_data = json.loads(post_data.decode('utf-8'))
                barcode = json_data.get('barcode', '')
                product_type = json_data.get('product_type', 'food')  # Default to food if not specified
                
                if not barcode:
                    self.send_json_response({
                        "success": False,
                        "error": "No barcode provided",
                        "sustainability": None
                    }, status=400)
                    return
                
                # Check if sustainability analyzer is available
                if not BARCODE_SCANNER_AVAILABLE or not self.scanner or not self.scanner.sustainability_analyzer:
                    self.send_json_response({
                        "success": False,
                        "error": "Product sustainability analysis not available. Please check dependencies and API keys.",
                        "sustainability": None
                    }, status=503)
                    return
                
                # Get sustainability information
                print(f"🔍 Looking up sustainability info for {product_type} barcode: {barcode}")
                sustainability_info = self.scanner._get_product_sustainability(barcode, product_type)
                print(f"📊 Sustainability result: {sustainability_info is not None}")
                
                if sustainability_info:
                    print(f"✅ Found {product_type} product: {sustainability_info.get('name', 'Unknown')}")
                    self.send_json_response({
                        "success": True,
                        "barcode": barcode,
                        "product_type": product_type,
                        "sustainability": sustainability_info
                    })
                else:
                    print(f"❌ No sustainability info found for {product_type} barcode: {barcode}")
                    self.send_json_response({
                        "success": False,
                        "error": f"Could not find sustainability information for this {product_type} product",
                        "sustainability": None
                    }, status=404)
                    
            except json.JSONDecodeError:
                self.send_json_response({
                    "success": False,
                    "error": "Invalid JSON data",
                    "sustainability": None
                }, status=400)
                
        except Exception as e:
            self.send_json_response({
                "success": False,
                "error": f"Product sustainability lookup error: {str(e)}",
                "sustainability": None
            }, status=500)
    
    def extract_form_field(self, data_str: str, field_name: str) -> str:
        """Extract a field from multipart form data (very basic)"""
        try:
            # Look for pattern: name="field_name"
            start_pattern = f'name="{field_name}"'
            start_idx = data_str.find(start_pattern)
            if start_idx == -1:
                return ""
            
            # Find the start of the value (after the double newline)
            value_start = data_str.find('\r\n\r\n', start_idx)
            if value_start == -1:
                return ""
            value_start += 4
            
            # Find the end of the value (next boundary)
            value_end = data_str.find('\r\n--', value_start)
            if value_end == -1:
                value_end = len(data_str)
            
            return data_str[value_start:value_end].strip()
        except:
            return ""
    
    def normalize_intake_data(self, form_data: dict, food_barcode: str = "", clothing_barcode: str = "") -> list:
        """Normalize intake form data into structured items for the Scoring Engine"""
        normalized_items = []
        
        # 1. MEAL ITEM - Primary food consumption
        meal_item = {
            "id": "meal_001",
            "type": "meal",
            "category": form_data.get('meal_type', 'mixed'),
            "subcategory": self.get_meal_subcategory(form_data.get('meal_type', 'mixed')),
            "attributes": {
                "origin": form_data.get('meal_origin', 'unknown'),
                "leftovers": form_data.get('meal_leftovers', 'unknown'),
                "barcode": food_barcode if food_barcode else None,
                "source_local": form_data.get('meal_origin') == 'Locally sourced',
                "source_homegrown": form_data.get('meal_origin') == 'Home-grown',
                "waste_level": self.categorize_waste_level(form_data.get('meal_leftovers', ''))
            },
            "sustainability_metrics": {
                "carbon_footprint": self.calculate_meal_carbon_footprint(form_data),
                "water_usage": self.calculate_meal_water_usage(form_data),
                "land_use": self.calculate_meal_land_use(form_data),
                "packaging_score": self.calculate_packaging_score(form_data)
            },
            "confidence": 0.95,
            "data_quality": "high"
        }
        normalized_items.append(meal_item)
        
        # 2. CLOTHING ITEM - Outfit choices
        if form_data.get('outfit_material') or clothing_barcode:
            clothing_item = {
                "id": "clothing_001", 
                "type": "clothing",
                "category": form_data.get('outfit_material', 'mixed'),
                "subcategory": self.get_clothing_subcategory(form_data.get('outfit_material')),
                "attributes": {
                    "material_type": form_data.get('outfit_material'),
                    "barcode": clothing_barcode if clothing_barcode else None,
                    "synthetic_content": self.get_synthetic_content(form_data.get('outfit_material')),
                    "natural_content": self.get_natural_content(form_data.get('outfit_material'))
                },
                "sustainability_metrics": {
                    "production_impact": self.calculate_clothing_production_impact(form_data),
                    "durability_score": self.calculate_clothing_durability(form_data),
                    "recyclability": self.calculate_clothing_recyclability(form_data)
                },
                "confidence": 0.8,
                "data_quality": "medium"
            }
            normalized_items.append(clothing_item)
        
        # 3. MOBILITY ITEM - Transportation choices
        if form_data.get('mobility_mode'):
            mobility_item = {
                "id": "mobility_001",
                "type": "transportation", 
                "category": form_data.get('mobility_mode', 'unknown'),
                "subcategory": self.get_mobility_subcategory(form_data.get('mobility_mode')),
                "attributes": {
                    "mode": form_data.get('mobility_mode'),
                    "distance": form_data.get('mobility_distance', '1'),
                    "distance_numeric": self.parse_distance(form_data.get('mobility_distance', '1')),
                    "emission_factor": self.get_emission_factor(form_data.get('mobility_mode'))
                },
                "sustainability_metrics": {
                    "carbon_emissions": self.calculate_mobility_emissions(form_data),
                    "energy_efficiency": self.calculate_mobility_efficiency(form_data),
                    "environmental_impact": self.calculate_mobility_impact(form_data)
                },
                "confidence": 0.9,
                "data_quality": "high"
            }
            normalized_items.append(mobility_item)
        
        # 4. RESOURCE ACTION ITEMS - Environmental actions taken
        resource_actions = form_data.get('resource_action', [])
        if resource_actions:
            for i, action in enumerate(resource_actions):
                action_item = {
                    "id": f"action_{i+1:03d}",
                    "type": "environmental_action",
                    "category": "resource_conservation",
                    "subcategory": self.categorize_action(action),
                    "attributes": {
                        "action_type": action,
                        "impact_level": self.get_action_impact_level(action),
                        "frequency": "daily"  # Assuming daily actions
                    },
                    "sustainability_metrics": {
                        "positive_impact_score": self.calculate_action_impact(action),
                        "resource_savings": self.calculate_resource_savings(action)
                    },
                    "confidence": 0.85,
                    "data_quality": "medium"
                }
                normalized_items.append(action_item)
        
        return normalized_items
    
    # Helper methods for normalization
    def get_meal_subcategory(self, meal_type: str) -> str:
        mapping = {
            'plant-based': 'vegetarian_vegan',
            'mixed': 'omnivore_balanced', 
            'meat-heavy': 'meat_focused',
            'snack': 'processed_snack',
            'drink': 'beverage'
        }
        return mapping.get(meal_type, 'other')
    
    def get_clothing_subcategory(self, material: str) -> str:
        mapping = {
            'mostly synthetic': 'synthetic_dominant',
            'mostly natural': 'natural_dominant', 
            'mixed': 'blended_materials'
        }
        return mapping.get(material, 'unknown')
    
    def get_mobility_subcategory(self, mode: str) -> str:
        mapping = {
            'walk': 'active_transport',
            'bike': 'active_transport',
            'public_transport': 'mass_transit',
            'car': 'private_vehicle',
            'other': 'alternative_transport'
        }
        return mapping.get(mode, 'unknown')
    
    def categorize_waste_level(self, leftovers: str) -> str:
        if 'None left' in leftovers:
            return 'no_waste'
        elif 'will eat later' in leftovers:
            return 'minimal_waste'
        elif 'will throw away' in leftovers:
            return 'high_waste'
        else:
            return 'unknown'
    
    def categorize_action(self, action: str) -> str:
        action_lower = action.lower()
        if 'water' in action_lower:
            return 'water_conservation'
        elif 'energy' in action_lower or 'electricity' in action_lower:
            return 'energy_conservation'
        elif 'waste' in action_lower or 'recycle' in action_lower:
            return 'waste_reduction'
        elif 'transport' in action_lower or 'car' in action_lower:
            return 'transport_optimization'
        else:
            return 'general_conservation'
    
    def get_synthetic_content(self, material: str) -> float:
        if 'mostly synthetic' in material:
            return 0.8
        elif 'mixed' in material:
            return 0.5
        else:
            return 0.2
    
    def get_natural_content(self, material: str) -> float:
        return 1.0 - self.get_synthetic_content(material)
    
    def parse_distance(self, distance_str: str) -> float:
        try:
            return float(distance_str)
        except:
            return 1.0
    
    def get_emission_factor(self, mode: str) -> float:
        # CO2 kg per km
        factors = {
            'walk': 0.0,
            'bike': 0.0,
            'public_transport': 0.04,
            'car': 0.21,
            'other': 0.15
        }
        return factors.get(mode, 0.1)
    
    def get_action_impact_level(self, action: str) -> str:
        high_impact = ['switch off unused electronics', 'use public transport']
        medium_impact = ['reuse items', 'conserve water']
        
        if action in high_impact:
            return 'high'
        elif action in medium_impact:
            return 'medium'
        else:
            return 'low'
    
    # Sustainability metric calculation methods
    def calculate_meal_carbon_footprint(self, form_data: dict) -> float:
        meal_type = form_data.get('meal_type', 'mixed')
        base_scores = {
            'plant-based': 1.5,
            'mixed': 4.5,
            'meat-heavy': 8.5,
            'snack': 2.0,
            'drink': 1.0
        }
        
        base_score = base_scores.get(meal_type, 4.0)
        
        # Adjust for origin
        origin = form_data.get('meal_origin', '')
        if 'Locally sourced' in origin or 'Home-grown' in origin:
            base_score *= 0.7
        elif 'Takeaway' in origin:
            base_score *= 1.3
            
        return round(base_score, 2)
    
    def calculate_meal_water_usage(self, form_data: dict) -> float:
        meal_type = form_data.get('meal_type', 'mixed')
        water_usage = {
            'plant-based': 500,
            'mixed': 1500, 
            'meat-heavy': 3000,
            'snack': 200,
            'drink': 100
        }
        return water_usage.get(meal_type, 1000)
    
    def calculate_meal_land_use(self, form_data: dict) -> float:
        meal_type = form_data.get('meal_type', 'mixed')
        land_use = {
            'plant-based': 1.0,
            'mixed': 3.0,
            'meat-heavy': 8.0,
            'snack': 0.5,
            'drink': 0.2
        }
        return land_use.get(meal_type, 2.0)
    
    def calculate_packaging_score(self, form_data: dict) -> float:
        origin = form_data.get('meal_origin', '')
        if 'Home-grown' in origin:
            return 10.0  # Best score
        elif 'Locally sourced' in origin:
            return 8.0
        elif 'Supermarket' in origin:
            return 6.0
        elif 'Takeaway' in origin:
            return 3.0
        else:
            return 5.0
    
    def calculate_clothing_production_impact(self, form_data: dict) -> float:
        material = form_data.get('outfit_material', 'mixed')
        impact_scores = {
            'mostly natural': 6.0,
            'mixed': 7.5,
            'mostly synthetic': 9.0
        }
        return impact_scores.get(material, 7.0)
    
    def calculate_clothing_durability(self, form_data: dict) -> float:
        material = form_data.get('outfit_material', 'mixed')
        durability = {
            'mostly natural': 8.0,
            'mixed': 7.0,
            'mostly synthetic': 6.0
        }
        return durability.get(material, 7.0)
    
    def calculate_clothing_recyclability(self, form_data: dict) -> float:
        material = form_data.get('outfit_material', 'mixed')
        recyclability = {
            'mostly natural': 9.0,
            'mixed': 6.0,
            'mostly synthetic': 4.0
        }
        return recyclability.get(material, 6.0)
    
    def calculate_mobility_emissions(self, form_data: dict) -> float:
        mode = form_data.get('mobility_mode', 'car')
        distance = self.parse_distance(form_data.get('mobility_distance', '1'))
        emission_factor = self.get_emission_factor(mode)
        return round(distance * emission_factor, 3)
    
    def calculate_mobility_efficiency(self, form_data: dict) -> float:
        mode = form_data.get('mobility_mode', 'car')
        efficiency_scores = {
            'walk': 10.0,
            'bike': 10.0,
            'public_transport': 8.0,
            'car': 4.0,
            'other': 6.0
        }
        return efficiency_scores.get(mode, 5.0)
    
    def calculate_mobility_impact(self, form_data: dict) -> float:
        emissions = self.calculate_mobility_emissions(form_data)
        if emissions == 0:
            return 10.0
        elif emissions < 0.5:
            return 8.0
        elif emissions < 2.0:
            return 6.0
        else:
            return 3.0
    
    def calculate_action_impact(self, action: str) -> float:
        impact_scores = {
            'switch off unused electronics': 8.0,
            'use public transport instead of car': 9.0,
            'reuse items instead of buying new': 7.0,
            'conserve water usage': 6.0,
            'reduce food waste': 8.0,
            'recycle materials': 6.0
        }
        return impact_scores.get(action, 5.0)
    
    def calculate_resource_savings(self, action: str) -> dict:
        savings = {
            'switch off unused electronics': {'energy': 0.5, 'cost': 2.0},
            'use public transport instead of car': {'carbon': 2.1, 'cost': 5.0},
            'reuse items instead of buying new': {'waste': 0.8, 'cost': 10.0},
            'conserve water usage': {'water': 50, 'cost': 1.0},
            'reduce food waste': {'waste': 0.5, 'cost': 3.0},
            'recycle materials': {'waste': 0.3, 'landfill': 0.2}
        }
        return savings.get(action, {'generic': 1.0})
    
    def get_timestamp(self) -> str:
        import datetime
        return datetime.datetime.now().isoformat()
    
    def generate_comprehensive_analysis(self, normalized_items: list, form_data: dict) -> dict:
        """Generate comprehensive analysis of normalized items for scoring"""
        
        total_carbon = sum([
            item.get('sustainability_metrics', {}).get('carbon_footprint', 0) 
            for item in normalized_items if 'carbon_footprint' in item.get('sustainability_metrics', {})
        ])
        
        total_emissions = sum([
            item.get('sustainability_metrics', {}).get('carbon_emissions', 0)
            for item in normalized_items if 'carbon_emissions' in item.get('sustainability_metrics', {})
        ])
        
        action_count = len([item for item in normalized_items if item['type'] == 'environmental_action'])
        
        return {
            "overall_impact": {
                "total_carbon_footprint_kg": round(total_carbon + total_emissions, 2),
                "environmental_actions_taken": action_count,
                "sustainability_rating": self.calculate_overall_rating(normalized_items)
            },
            "category_breakdown": {
                "meal": self.analyze_meal_items(normalized_items),
                "transportation": self.analyze_transport_items(normalized_items), 
                "clothing": self.analyze_clothing_items(normalized_items),
                "actions": self.analyze_action_items(normalized_items)
            },
            "recommendations": self.generate_recommendations(normalized_items, form_data)
        }
    
    def calculate_comprehensive_eco_score(self, normalized_items: list, form_data: dict) -> dict:
        """Calculate comprehensive eco-score based on normalized items"""
        
        # Base scores for different categories
        meal_score = self.score_meal_items(normalized_items)
        transport_score = self.score_transport_items(normalized_items)
        clothing_score = self.score_clothing_items(normalized_items)
        action_bonus = self.score_action_items(normalized_items)
        
        # Weighted overall score
        overall_score = (
            meal_score * 0.4 +      # 40% weight for food choices
            transport_score * 0.3 +  # 30% weight for transportation
            clothing_score * 0.2 +   # 20% weight for clothing
            action_bonus * 0.1       # 10% bonus for positive actions
        )
        
        return {
            "overall_score": round(min(100, max(0, overall_score)), 1),
            "category_scores": {
                "meal": round(meal_score, 1),
                "transportation": round(transport_score, 1),
                "clothing": round(clothing_score, 1),
                "environmental_actions": round(action_bonus, 1)
            },
            "grade": self.get_grade(overall_score),
            "percentile": self.get_percentile(overall_score)
        }
    
    # Analysis helper methods
    def calculate_overall_rating(self, items: list) -> str:
        avg_score = sum([item.get('confidence', 0.5) for item in items]) / len(items) if items else 0.5
        if avg_score > 0.8:
            return "Excellent"
        elif avg_score > 0.6:
            return "Good"
        elif avg_score > 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def analyze_meal_items(self, items: list) -> dict:
        meal_items = [item for item in items if item['type'] == 'meal']
        if not meal_items:
            return {}
        
        meal = meal_items[0]  # Assuming one meal
        return {
            "category": meal.get('category'),
            "carbon_footprint": meal.get('sustainability_metrics', {}).get('carbon_footprint', 0),
            "waste_level": meal.get('attributes', {}).get('waste_level'),
            "local_sourcing": meal.get('attributes', {}).get('source_local', False)
        }
    
    def analyze_transport_items(self, items: list) -> dict:
        transport_items = [item for item in items if item['type'] == 'transportation']
        if not transport_items:
            return {}
        
        transport = transport_items[0]
        return {
            "mode": transport.get('category'),
            "emissions": transport.get('sustainability_metrics', {}).get('carbon_emissions', 0),
            "efficiency_score": transport.get('sustainability_metrics', {}).get('energy_efficiency', 0)
        }
    
    def analyze_clothing_items(self, items: list) -> dict:
        clothing_items = [item for item in items if item['type'] == 'clothing']
        if not clothing_items:
            return {}
        
        clothing = clothing_items[0]
        return {
            "material_type": clothing.get('category'),
            "synthetic_content": clothing.get('attributes', {}).get('synthetic_content', 0),
            "sustainability_score": clothing.get('sustainability_metrics', {}).get('production_impact', 0)
        }
    
    def analyze_action_items(self, items: list) -> dict:
        action_items = [item for item in items if item['type'] == 'environmental_action']
        return {
            "total_actions": len(action_items),
            "action_types": [item.get('attributes', {}).get('action_type') for item in action_items],
            "average_impact": sum([item.get('sustainability_metrics', {}).get('positive_impact_score', 0) 
                                 for item in action_items]) / len(action_items) if action_items else 0
        }
    
    def generate_recommendations(self, items: list, form_data: dict) -> list:
        recommendations = []
        
        # Meal recommendations
        meal_items = [item for item in items if item['type'] == 'meal']
        if meal_items:
            meal = meal_items[0]
            if meal.get('category') == 'meat-heavy':
                recommendations.append("Consider reducing meat consumption to lower your carbon footprint")
            if not meal.get('attributes', {}).get('source_local'):
                recommendations.append("Try to source food locally to reduce transportation emissions")
        
        # Transport recommendations  
        transport_items = [item for item in items if item['type'] == 'transportation']
        if transport_items:
            transport = transport_items[0]
            if transport.get('category') == 'car':
                recommendations.append("Consider walking, cycling, or public transport for short distances")
        
        # Action recommendations
        action_items = [item for item in items if item['type'] == 'environmental_action']
        if len(action_items) < 2:
            recommendations.append("Try to incorporate more daily environmental actions")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    # Scoring helper methods
    def score_meal_items(self, items: list) -> float:
        meal_items = [item for item in items if item['type'] == 'meal']
        if not meal_items:
            return 50.0
        
        meal = meal_items[0]
        category = meal.get('category', 'mixed')
        
        base_scores = {
            'plant-based': 90,
            'mixed': 70,
            'meat-heavy': 40,
            'snack': 60,
            'drink': 80
        }
        
        score = base_scores.get(category, 60)
        
        # Bonus for local sourcing
        if meal.get('attributes', {}).get('source_local'):
            score += 10
        
        # Penalty for waste
        if meal.get('attributes', {}).get('waste_level') == 'high_waste':
            score -= 20
        
        return min(100, max(0, score))
    
    def score_transport_items(self, items: list) -> float:
        transport_items = [item for item in items if item['type'] == 'transportation']
        if not transport_items:
            return 70.0
        
        transport = transport_items[0]
        efficiency = transport.get('sustainability_metrics', {}).get('energy_efficiency', 5.0)
        return min(100, efficiency * 10)
    
    def score_clothing_items(self, items: list) -> float:
        clothing_items = [item for item in items if item['type'] == 'clothing']
        if not clothing_items:
            return 70.0
        
        clothing = clothing_items[0]
        category = clothing.get('category', 'mixed')
        
        scores = {
            'mostly natural': 85,
            'mixed': 70,
            'mostly synthetic': 55
        }
        
        return scores.get(category, 70)
    
    def score_action_items(self, items: list) -> float:
        action_items = [item for item in items if item['type'] == 'environmental_action']
        if not action_items:
            return 0.0
        
        total_impact = sum([
            item.get('sustainability_metrics', {}).get('positive_impact_score', 0)
            for item in action_items
        ])
        
        return min(100, total_impact * len(action_items))
    
    def get_grade(self, score: float) -> str:
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def get_percentile(self, score: float) -> float:
        # Simple percentile calculation based on score
        return min(99.9, max(0.1, score * 0.9 + 10))
    
    def get_meal_materials(self, meal_type: str) -> list:
        """Get materials based on meal type"""
        materials_map = {
            "plant-based": ["vegetables", "grains", "legumes", "fruits"],
            "mixed": ["vegetables", "protein", "grains"],
            "meat-heavy": ["protein", "animal products"],
            "snack": ["processed", "packaged"],
            "drink": ["liquid", "beverage"]
        }
        return materials_map.get(meal_type, ["mixed"])
    
    def get_outfit_materials(self, outfit_type: str) -> list:
        """Get materials based on outfit type"""
        materials_map = {
            "mostly natural": ["cotton", "wool", "linen", "silk"],
            "mostly synthetic": ["polyester", "nylon", "acrylic"],
            "mixed": ["cotton", "polyester", "blend"]
        }
        return materials_map.get(outfit_type, ["mixed"])
    
    def generate_analysis(self, form_data: dict) -> dict:
        """Generate intelligent analysis of user choices"""
        sustainability_score = 0
        recommendations = []
        
        # Analyze meal choices
        meal_type = form_data.get('meal_type', '')
        if meal_type == 'plant-based':
            sustainability_score += 30
            recommendations.append("🌱 Great choice on plant-based eating!")
        elif meal_type == 'mixed':
            sustainability_score += 20
            recommendations.append("🥗 Consider increasing plant-based meals")
        else:
            sustainability_score += 10
            recommendations.append("🌿 Try incorporating more plant-based options")
        
        # Analyze mobility
        mobility = form_data.get('mobility_mode', '')
        if mobility in ['walk', 'bike']:
            sustainability_score += 25
            recommendations.append("🚶 Excellent eco-friendly transportation!")
        elif mobility == 'bus':
            sustainability_score += 15
            recommendations.append("🚌 Public transport is a great choice!")
        else:
            recommendations.append("🚲 Consider walking, biking, or public transport")
        
        # Analyze outfit choices
        outfit = form_data.get('outfit_material', '')
        if outfit == 'mostly natural':
            sustainability_score += 20
            recommendations.append("👕 Natural fibers are eco-friendly!")
        else:
            recommendations.append("🧵 Look for natural fiber clothing options")
        
        # Analyze actions
        actions = form_data.get('resource_action', [])
        if isinstance(actions, list) and len(actions) > 0:
            sustainability_score += len(actions) * 5
            recommendations.append(f"♻️ Great job on {len(actions)} sustainable actions!")
        
        # Analyze reflection text using Mistral AI
        reflection_analysis = self.analyze_reflection(form_data.get('reflection', ''))
        
        return {
            "sustainability_score": min(sustainability_score, 100),
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "impact_summary": self.get_impact_summary(form_data),
            "reflection_analysis": reflection_analysis
        }
    
    def get_impact_summary(self, form_data: dict) -> str:
        """Generate a personalized impact summary"""
        meal_type = form_data.get('meal_type', '')
        mobility = form_data.get('mobility_mode', '')
        actions = form_data.get('resource_action', [])
        
        impact_parts = []
        
        if meal_type == 'plant-based':
            impact_parts.append("reduced your carbon footprint by ~2kg CO2")
        
        if mobility in ['walk', 'bike']:
            impact_parts.append("saved emissions from transportation")
        
        if len(actions) > 0:
            impact_parts.append(f"completed {len(actions)} sustainable actions")
        
        if impact_parts:
            return f"Today you {' and '.join(impact_parts)}!"
        return "Every sustainable choice makes a difference!"
    
    def calculate_eco_score(self, form_data: dict) -> dict:
        """Calculate detailed eco score breakdown"""
        meal_score = self.score_meal_choice(form_data.get('meal_type', ''))
        mobility_score = self.score_mobility_choice(form_data.get('mobility_mode', ''))
        actions_score = self.score_daily_actions(form_data.get('resource_action', []))
        outfit_score = self.score_outfit_choice(form_data.get('outfit_material', ''))
        
        # Get reflection analysis and score (10 points max)
        reflection_analysis = self.analyze_reflection(form_data.get('reflection', ''))
        reflection_score = reflection_analysis.get('reflection_score', 0)
        
        total = meal_score + mobility_score + actions_score + outfit_score + reflection_score
        
        return {
            "total": total,  # Should always be <= 100
            "breakdown": {
                "food_choices": meal_score,
                "transportation": mobility_score,
                "daily_actions": actions_score,
                "clothing": outfit_score,
                "reflection": reflection_score
            },
            "level": self.get_eco_level(total)
        }
    
    def score_meal_choice(self, meal_type: str) -> int:
        """Score meal choice out of 30 points"""
        scores = {
            "plant-based": 30,
            "mixed": 20,
            "meat-heavy": 10,
            "snack": 15,
            "drink": 12
        }
        return scores.get(meal_type, 15)
    
    def score_mobility_choice(self, mobility: str) -> int:
        """Score mobility choice out of 25 points"""
        scores = {
            "walk": 25,
            "bike": 25,
            "bus": 18,
            "train": 18,
            "car": 8,
            "other": 12
        }
        return scores.get(mobility, 12)
    
    def score_daily_actions(self, actions: list) -> int:
        """Score daily actions out of 25 points"""
        if not isinstance(actions, list):
            return 0
        
        # Each sustainable action is worth points
        action_scores = {
            "Used a reusable bottle/cup": 5,
            "Turned off lights/electronics": 4,
            "Recycled something": 4,
            "Chose a plant-based meal": 6,
            "Used public/shared transport": 6,
            "None of these": 0
        }
        
        total_score = 0
        for action in actions:
            total_score += action_scores.get(action, 0)
        
        return min(total_score, 25)  # Cap at 25 points
    
    def score_outfit_choice(self, outfit: str) -> int:
        """Score outfit choice out of 10 points"""
        scores = {
            "mostly natural": 10,
            "mixed": 6,
            "mostly synthetic": 3
        }
        return scores.get(outfit, 5)
    
    def get_eco_level(self, score: int) -> str:
        if score >= 80:
            return "🌟 Eco Champion"
        elif score >= 60:
            return "🌱 Green Guardian"
        elif score >= 40:
            return "🌿 Earth Friend"
        else:
            return "🌍 Climate Beginner"
    
    def analyze_reflection(self, reflection_text: str) -> dict:
        """Analyze reflection text using Mistral AI to provide personalized insights and score out of 10"""
        if not reflection_text or not reflection_text.strip():
            return {
                "insights": "No reflection provided - consider sharing your thoughts on sustainability!",
                "themes": [],
                "encouragement": "Your voice matters in the climate conversation! 🌍",
                "reflection_score": 0,
                "scoring_criteria": "No reflection provided"
            }
        
        # Only proceed if we have barcode scanner available (which includes Mistral AI)
        if not BARCODE_SCANNER_AVAILABLE or not self.scanner:
            return {
                "insights": "Reflection analysis not available - Mistral AI integration needed.",
                "themes": [],
                "encouragement": "Thank you for sharing your thoughts on sustainability! 💚",
                "reflection_score": 3,  # Basic score for providing reflection
                "scoring_criteria": "Basic score - AI analysis unavailable"
            }
        
        try:
            # Use Mistral AI to analyze the reflection
            import requests
            import os
            
            api_key = os.getenv('MISTRAL_API_KEY')
            if not api_key:
                return {
                    "insights": "AI analysis not available - API key not configured.",
                    "themes": [],
                    "encouragement": "Thank you for sharing your sustainability perspective! 🌱",
                    "reflection_score": 3,
                    "scoring_criteria": "Basic score - API key not configured"
                }
            
            prompt = f"""
            Analyze this person's reflection on sustainability: "{reflection_text}"
            
            Score the reflection out of 10 points based on these criteria:
            - Depth of understanding (0-3 points): Shows genuine comprehension of sustainability concepts
            - Personal connection (0-2 points): Demonstrates personal relevance or commitment  
            - Specificity (0-2 points): Includes concrete examples or specific aspects
            - Forward-thinking (0-2 points): Mentions future implications, responsibility, or action
            - Clarity (0-1 point): Well-articulated and coherent response
            
            Provide response in JSON format:
            {{
                "insights": "A personalized 1-2 sentence insight about their understanding",
                "themes": ["list", "of", "key", "sustainability", "themes"],
                "encouragement": "An encouraging message that builds on their perspective",
                "reflection_score": 0-10,
                "scoring_criteria": "Brief explanation of why this score was given",
                "strengths": ["what", "was", "particularly", "good"],
                "suggestions": ["gentle", "suggestions", "for", "deeper", "thinking"]
            }}
            
            Guidelines:
            - Be encouraging and constructive
            - Score fairly but generously - most sincere attempts should get 5+ points
            - Identify key themes like: future generations, personal responsibility, environmental protection, systems thinking, etc.
            - Keep feedback supportive and educational
            - Even simple responses that show genuine thought should receive reasonable scores
            """
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "mistral-small-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 400,
                "temperature": 0.2  # Lower temperature for more consistent scoring
            }
            
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Extract JSON from response
                import json
                try:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        # Ensure reflection_score is within range 0-10
                        score = analysis.get('reflection_score', 5)
                        analysis['reflection_score'] = min(max(score, 0), 10)
                        
                        # Ensure required fields exist
                        analysis.setdefault('insights', 'Your reflection shows thoughtful engagement with sustainability.')
                        analysis.setdefault('themes', ['sustainability awareness'])
                        analysis.setdefault('encouragement', 'Thank you for sharing your perspective!')
                        analysis.setdefault('scoring_criteria', 'AI analysis completed')
                        analysis.setdefault('strengths', ['thoughtful response'])
                        analysis.setdefault('suggestions', [])
                        
                        return analysis
                    else:
                        raise ValueError("No JSON found in response")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"JSON parsing error: {e}")
                    # Fallback response with estimated score based on text length and content
                    word_count = len(reflection_text.split())
                    
                    # Basic scoring based on length and keyword presence
                    score = 3  # Base score for providing reflection
                    
                    if word_count >= 15:  # Longer responses
                        score += 2
                    elif word_count >= 8:  # Medium responses
                        score += 1
                    
                    # Check for sustainability keywords
                    sustainability_keywords = [
                        'future', 'generation', 'environment', 'planet', 'responsible', 
                        'protect', 'care', 'preserve', 'reduce', 'recycle', 'green',
                        'climate', 'carbon', 'renewable', 'conscious', 'mindful'
                    ]
                    
                    keyword_count = sum(1 for word in sustainability_keywords 
                                      if word in reflection_text.lower())
                    score += min(keyword_count, 3)  # Up to 3 bonus points for keywords
                    
                    return {
                        "insights": "Your reflection demonstrates engagement with sustainability concepts.",
                        "themes": ["sustainability awareness", "personal reflection"],
                        "encouragement": "Thank you for taking time to reflect on this important topic! 🌍",
                        "reflection_score": min(score, 10),
                        "scoring_criteria": f"Scored based on content analysis ({word_count} words, sustainability themes present)",
                        "strengths": ["thoughtful engagement"],
                        "suggestions": ["continue exploring sustainability in daily life"]
                    }
            else:
                # API request failed - provide basic scoring
                word_count = len(reflection_text.split())
                basic_score = min(5 + (word_count // 10), 8)  # 5-8 points based on effort
                
                return {
                    "insights": "Your reflection on sustainability is valued and appreciated.",
                    "themes": ["personal perspective"],
                    "encouragement": "Every voice in the sustainability conversation matters! 💚",
                    "reflection_score": basic_score,
                    "scoring_criteria": "Basic scoring - API temporarily unavailable",
                    "strengths": ["sharing perspective"],
                    "suggestions": []
                }
                
        except Exception as e:
            print(f"Error analyzing reflection: {str(e)}")
            # Fallback scoring based on basic text analysis
            word_count = len(reflection_text.split())
            fallback_score = min(4 + (word_count // 8), 7)  # 4-7 points
            
            return {
                "insights": "Thank you for sharing your thoughts on sustainability.",
                "themes": ["personal reflection"],
                "encouragement": "Your perspective on sustainability helps build a more conscious community! 🌱",
                "reflection_score": fallback_score,
                "scoring_criteria": "Fallback scoring - technical issue with analysis",
                "strengths": ["participating in reflection"],
                "suggestions": []
            }
    
    def send_json_response(self, data: Dict[str, Any], status: int = 200):
        """Send a JSON response"""
        response_json = json.dumps(data).encode('utf-8')
        
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Content-Length', str(len(response_json)))
        self.end_headers()
        self.wfile.write(response_json)
    
    def log_message(self, format, *args):
        """Override to provide cleaner logging"""
        print(f"[{self.address_string()}] {format % args}")

def run_server(port: int = 8000):
    """Run the simple HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, IntakeHandler)
    
    print(f"🌱 EcoBee Simple Server starting on http://localhost:{port}")
    print("📍 Available endpoints:")
    print("   GET  /health")
    print("   POST /api/intake") 
    print("   POST /api/score")
    print("   POST /api/scan-barcode")
    print("   POST /api/product-sustainability")
    print(f"📱 Barcode Scanner: {'✅ Enabled (Pixtral)' if BARCODE_SCANNER_AVAILABLE else '❌ Disabled'}")
    print(f"🌱 Product Analysis: {'✅ Enabled (AI-powered)' if BARCODE_SCANNER_AVAILABLE else '❌ Disabled'}")
    if BARCODE_SCANNER_AVAILABLE:
        print("💡 To use barcode scanning and product analysis, set MISTRAL_API_KEY environment variable")
    print("\n🔗 Frontend should connect to: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
