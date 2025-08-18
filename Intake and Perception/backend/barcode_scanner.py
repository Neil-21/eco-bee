#!/usr/bin/env python3
"""
Barcode Scanner using Mistral's Pixtral Vision Model
This module provides barcode scanning capabilities for both camera capture and image upload
with comprehensive product sustainability analysis
"""

import base64
import io
import json
import os
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import sustainability analyzer
try:
    from product_sustainability import create_sustainability_analyzer
    SUSTAINABILITY_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Product sustainability analyzer not available: {e}")
    SUSTAINABILITY_ANALYZER_AVAILABLE = False

class PixtralBarcodeScanner:
    """Barcode scanner using Mistral's Pixtral vision model"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Pixtral barcode scanner
        
        Args:
            api_key: Mistral API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        if not self.api_key:
            print("⚠️  Warning: No Mistral API key found. Please check your .env file or set MISTRAL_API_KEY environment variable")
        
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "pixtral-12b-2409"
        
        # Initialize sustainability analyzer
        self.sustainability_analyzer = None
        if SUSTAINABILITY_ANALYZER_AVAILABLE:
            try:
                self.sustainability_analyzer = create_sustainability_analyzer()
                print("✅ Product sustainability analyzer initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize sustainability analyzer: {e}")
        
    def scan_barcode_from_image(self, image_data: bytes, product_type: str = "food") -> Dict[str, Any]:
        """Scan barcode from image bytes
        
        Args:
            image_data: Raw image bytes
            product_type: Expected product type ("food" or "clothing")
            
        Returns:
            Dictionary containing barcode data and product information
        """
        try:
            # Convert image bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to base64 for API
            base64_image = self._image_to_base64(image)
            
            # Call Pixtral API for barcode detection
            barcode_result = self._call_pixtral_api(base64_image)
            
            # If barcode was successfully detected, get sustainability info
            if barcode_result.get("success") and barcode_result.get("barcode"):
                barcode_number = barcode_result["barcode"]
                sustainability_info = self._get_product_sustainability(barcode_number, product_type)
                
                # Merge sustainability info into the result
                if sustainability_info:
                    barcode_result["sustainability"] = sustainability_info
                    barcode_result["product_details"] = {
                        "name": sustainability_info.get("name"),
                        "brand": sustainability_info.get("brand"),
                        "category": sustainability_info.get("category"),
                        "description": sustainability_info.get("description"),
                        "ingredients": sustainability_info.get("ingredients", [])
                    }
                    
                    # Update product_info with correct name and brand from sustainability data
                    if barcode_result.get("product_info"):
                        barcode_result["product_info"]["name"] = sustainability_info.get("name", barcode_result["product_info"].get("name", "Unknown"))
                        barcode_result["product_info"]["brand"] = sustainability_info.get("brand", barcode_result["product_info"].get("brand", "Unknown"))
                        # Update category to be more specific for quiz logic
                        if "snack" in sustainability_info.get("category", "").lower() or "sweet" in sustainability_info.get("category", "").lower() or "candy" in sustainability_info.get("category", "").lower():
                            barcode_result["product_info"]["category"] = "Processed/Packaged"
                        else:
                            barcode_result["product_info"]["category"] = sustainability_info.get("category", barcode_result["product_info"].get("category", "Food"))
            
            return barcode_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to scan barcode: {str(e)}",
                "barcode": None,
                "product_info": None
            }
    
    def scan_barcode_from_base64(self, base64_image: str, product_type: str = "food") -> Dict[str, Any]:
        """Scan barcode from base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            product_type: Expected product type ("food" or "clothing")
            
        Returns:
            Dictionary containing barcode data and product information
        """
        try:
            barcode_result = self._call_pixtral_api(base64_image)
            
            # If barcode was successfully detected, get sustainability info
            if barcode_result.get("success") and barcode_result.get("barcode"):
                barcode_number = barcode_result["barcode"]
                sustainability_info = self._get_product_sustainability(barcode_number, product_type)
                
                # Merge sustainability info into the result
                if sustainability_info:
                    barcode_result["sustainability"] = sustainability_info
                    barcode_result["product_details"] = {
                        "name": sustainability_info.get("name"),
                        "brand": sustainability_info.get("brand"),
                        "category": sustainability_info.get("category"),
                        "description": sustainability_info.get("description"),
                        "ingredients": sustainability_info.get("ingredients", [])
                    }
            
            return barcode_result
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to scan barcode: {str(e)}",
                "barcode": None,
                "product_info": None
            }
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        # Resize image if too large (Pixtral has size limits)
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = tuple(int(dim * ratio) for dim in image.size)
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')
    
    def _call_pixtral_api(self, base64_image: str) -> Dict[str, Any]:
        """Call Mistral Pixtral API for barcode detection
        
        Args:
            base64_image: Base64 encoded image
            
        Returns:
            Dictionary with barcode scanning results
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "No Mistral API key configured",
                "barcode": None,
                "product_info": None
            }
        
        # Construct the prompt for barcode detection
        prompt = """
        Please analyze this image and extract any barcode information you can find. Look for:
        1. Barcode numbers (UPC, EAN, Code 128, QR codes, etc.)
        2. Product name or brand visible on the package
        3. Product category (food, clothing, electronics, etc.)
        4. Any sustainability or eco-friendly indicators
        
        Return your response in JSON format with the following structure:
        {
            "barcode_detected": true/false,
            "barcode_number": "the actual barcode number if found",
            "barcode_type": "UPC/EAN/QR/etc if identifiable",
            "product_name": "product name if visible",
            "brand": "brand name if visible",
            "category": "product category",
            "sustainability_indicators": ["list of any eco-friendly labels or certifications visible"],
            "confidence": 0.0-1.0
        }
        
        If no barcode is detected, set barcode_detected to false and fill in any other product information you can extract.
        """
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse JSON from the response
                try:
                    # Extract JSON from the response (remove any markdown formatting)
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        barcode_data = json.loads(json_str)
                    else:
                        # Fallback if JSON extraction fails
                        barcode_data = {"barcode_detected": False, "error": "Could not parse response"}
                
                except json.JSONDecodeError:
                    # If JSON parsing fails, create a basic response
                    barcode_data = {
                        "barcode_detected": False,
                        "error": "Could not parse barcode data from response",
                        "raw_response": content
                    }
                
                return {
                    "success": True,
                    "barcode": barcode_data.get("barcode_number"),
                    "product_info": {
                        "name": barcode_data.get("product_name"),
                        "brand": barcode_data.get("brand"),
                        "category": barcode_data.get("category"),
                        "sustainability_indicators": barcode_data.get("sustainability_indicators", []),
                        "barcode_type": barcode_data.get("barcode_type"),
                        "confidence": barcode_data.get("confidence", 0.0)
                    },
                    "detected": barcode_data.get("barcode_detected", False),
                    "raw_data": barcode_data
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code} - {response.text}",
                    "barcode": None,
                    "product_info": None
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout - Pixtral API took too long to respond",
                "barcode": None,
                "product_info": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "barcode": None,
                "product_info": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "barcode": None,
                "product_info": None
            }
    
    def _get_product_sustainability(self, barcode: str, product_type: str = "food") -> Optional[Dict[str, Any]]:
        """Get comprehensive product sustainability information
        
        Args:
            barcode: Product barcode number
            product_type: Type of product ("food" or "clothing")
            
        Returns:
            Dictionary with sustainability analysis or None
        """
        if not self.sustainability_analyzer:
            return None
        
        try:
            product_info = self.sustainability_analyzer.get_product_info(barcode, product_type)
            
            if product_info:
                return {
                    "name": product_info.name,
                    "brand": product_info.brand,
                    "category": product_info.category,
                    "description": product_info.description,
                    "ingredients": product_info.ingredients,
                    "materials": getattr(product_info, 'materials', []),  # For clothing products
                    "sustainability_score": {
                        "overall_score": product_info.sustainability_score.overall_score,
                        "environmental_impact": product_info.sustainability_score.environmental_impact,
                        "carbon_footprint": product_info.sustainability_score.carbon_footprint,
                        "packaging_score": product_info.sustainability_score.packaging_score,
                        "recyclability": product_info.sustainability_score.recyclability,
                        "ethical_sourcing": product_info.sustainability_score.ethical_sourcing,
                        "certifications": product_info.sustainability_score.certifications,
                        "improvement_suggestions": product_info.sustainability_score.improvement_suggestions
                    },
                    "price_range": product_info.price_range,
                    "alternatives": product_info.alternatives,
                    "eco_rating": self._get_eco_rating(product_info.sustainability_score.overall_score),
                    "environmental_tips": self._get_environmental_tips(product_info.category),
                    # Category detection fields
                    "detected_category": getattr(product_info, 'detected_category', 'unknown'),
                    "expected_category": getattr(product_info, 'expected_category', product_type),
                    "category_confidence": getattr(product_info, 'category_confidence', 1.0),
                    "category_mismatch": getattr(product_info, 'category_mismatch', False),
                    # Additional fields for frontend compatibility
                    "overall_score": product_info.sustainability_score.overall_score  # For display compatibility
                }
        
        except Exception as e:
            print(f"Error getting sustainability info for barcode {barcode}: {e}")
        
        return None
    
    def _get_eco_rating(self, score: float) -> str:
        """Convert numerical score to eco rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
    
    def _get_environmental_tips(self, category: str) -> List[str]:
        """Get category-specific environmental tips"""
        category_lower = category.lower()
        
        if "food" in category_lower or "drink" in category_lower:
            return [
                "Choose organic when possible to reduce pesticide use",
                "Look for local produce to minimize transportation emissions",
                "Consider plant-based alternatives to reduce carbon footprint",
                "Avoid excessive packaging and choose bulk options"
            ]
        elif "cleaning" in category_lower or "household" in category_lower:
            return [
                "Use concentrated products to reduce packaging",
                "Choose biodegradable formulas",
                "Look for refillable containers",
                "Make your own cleaners with simple ingredients"
            ]
        elif "personal care" in category_lower or "cosmetic" in category_lower:
            return [
                "Choose products with natural ingredients",
                "Look for minimal, recyclable packaging",
                "Consider solid alternatives (bars, shampoo bars)",
                "Buy from brands with sustainable practices"
            ]
        else:
            return [
                "Research the brand's sustainability commitments",
                "Choose products with minimal packaging",
                "Look for eco-certifications and labels",
                "Consider secondhand or refurbished alternatives"
            ]

def create_scanner() -> PixtralBarcodeScanner:
    """Create a new barcode scanner instance"""
    return PixtralBarcodeScanner()
