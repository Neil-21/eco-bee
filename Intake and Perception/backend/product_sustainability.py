#!/usr/bin/env python3
"""
Product Sustainability Analysis Module
This module provides comprehensive product information and sustainability scoring
"""

import requests
import json
import os
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class SustainabilityScore:
    """Sustainability scoring for a product"""
    overall_score: float  # 0-100
    environmental_impact: float  # 0-100
    carbon_footprint: float  # 0-100
    packaging_score: float  # 0-100
    recyclability: float  # 0-100
    ethical_sourcing: float  # 0-100
    certifications: List[str]
    improvement_suggestions: List[str]

@dataclass
class ProductInfo:
    """Complete product information"""
    name: str
    brand: str
    category: str
    barcode: str
    description: str
    ingredients: List[str]
    sustainability_score: SustainabilityScore
    price_range: str
    alternatives: List[Dict[str, str]]  # Suggested eco-friendly alternatives

class ProductSustainabilityAnalyzer:
    """Analyze product sustainability using multiple data sources"""
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        
        # Cache for API responses to avoid repeated calls
        self.cache = {}
        
    def get_product_info(self, barcode: str, product_type: str = "food") -> Optional[ProductInfo]:
        """Get comprehensive product information and sustainability analysis
        
        Args:
            barcode: Product barcode number
            product_type: Type of product ("food" or "clothing")
            
        Returns:
            ProductInfo object with sustainability analysis or None
        """
        try:
            print(f"🔍 Starting {product_type} product lookup for barcode: {barcode}")
            
            # Check cache first
            cache_key = f"product_{product_type}_{barcode}"
            if cache_key in self.cache:
                print(f"💾 Found in cache for barcode: {barcode}")
                return self.cache[cache_key]
            
            # Route to appropriate data source based on product type
            if product_type == "clothing":
                basic_info = self._get_clothing_product_data(barcode)
            else:
                # Step 1: Get basic product info from Open Food Facts (for food products)
                print(f"📊 Checking OpenFoodFacts for barcode: {barcode}")
                basic_info = self._get_openfoodfacts_data(barcode)
                
                # Step 2: If not found in OpenFoodFacts, try UPCitemdb
                if not basic_info:
                    print(f"📊 Checking UPCitemdb for barcode: {barcode}")
                    basic_info = self._get_upcitemdb_data(barcode)
            
            # Step 3: If still no info, create basic structure
            if not basic_info:
                print(f"❌ No product data found for barcode: {barcode}, creating fallback")
                basic_info = {
                    'name': f'Unknown {product_type.title()} Product',
                    'brand': 'Unknown Brand',
                    'category': f'{product_type}',
                    'description': '',
                    'ingredients': [] if product_type == "food" else [],
                    'materials': [] if product_type == "clothing" else []
                }
            
            # Step 4: Detect and verify category
            detected_category = self._detect_product_category(basic_info)
            category_confidence = self._calculate_category_confidence(basic_info, product_type)
            
            print(f"🔍 Category detection - Expected: {product_type}, Detected: {detected_category}, Confidence: {category_confidence}")
            
            # Step 5: Use AI to analyze sustainability
            print(f"🤖 Starting AI sustainability analysis for: {basic_info.get('name', 'Unknown')}")
            if product_type == "clothing":
                sustainability_analysis = self._analyze_clothing_sustainability_with_ai(basic_info, barcode)
            else:
                sustainability_analysis = self._analyze_sustainability_with_ai(basic_info, barcode)
            
            # Step 5: Create ProductInfo object with category detection
            product_info = ProductInfo(
                name=basic_info.get('name', 'Unknown Product'),
                brand=basic_info.get('brand', 'Unknown Brand'),
                category=basic_info.get('category', 'Unknown'),
                barcode=barcode,
                description=basic_info.get('description', ''),
                ingredients=basic_info.get('ingredients', []),
                sustainability_score=sustainability_analysis,
                price_range=basic_info.get('price_range', 'Unknown'),
                alternatives=self._get_sustainable_alternatives(basic_info)
            )
            
            # Add category detection metadata
            product_info.detected_category = detected_category
            product_info.expected_category = product_type
            product_info.category_confidence = category_confidence
            product_info.category_mismatch = detected_category != product_type and detected_category != "unknown"
            
            # Cache the result
            self.cache[cache_key] = product_info
            print(f"✅ Successfully created product info for: {product_info.name}")
            
            return product_info
            
        except Exception as e:
            print(f"Error getting product info for {barcode}: {e}")
            return None
    
    def _get_openfoodfacts_data(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product data from Open Food Facts API"""
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 1:  # Product found
                    product = data['product']
                    
                    # Extract ingredients
                    ingredients = []
                    if 'ingredients_text' in product:
                        ingredients = [ing.strip() for ing in product['ingredients_text'].split(',')]
                    elif 'ingredients' in product:
                        ingredients = [ing.get('text', '') for ing in product['ingredients']]
                    
                    return {
                        'name': product.get('product_name', ''),
                        'brand': product.get('brands', ''),
                        'category': product.get('categories', ''),
                        'description': product.get('generic_name', ''),
                        'ingredients': ingredients,
                        'nutriscore': product.get('nutriscore_grade', ''),
                        'ecoscore': product.get('ecoscore_grade', ''),
                        'labels': product.get('labels', '').split(',') if product.get('labels') else [],
                        'packaging': product.get('packaging', ''),
                        'source': 'openfoodfacts'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from OpenFoodFacts: {e}")
            return None
    
    def _get_upcitemdb_data(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product data from UPCitemdb API"""
        try:
            url = f"https://api.upcitemdb.com/prod/trial/lookup"
            params = {'upc': barcode}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('code') == 'OK' and data.get('items'):
                    item = data['items'][0]
                    
                    return {
                        'name': item.get('title', ''),
                        'brand': item.get('brand', ''),
                        'category': item.get('category', ''),
                        'description': item.get('description', ''),
                        'ingredients': [],
                        'source': 'upcitemdb'
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching from UPCitemdb: {e}")
            return None
    
    def _get_clothing_product_data(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get clothing/textile product data from various sources
        
        Args:
            barcode: Product barcode
            
        Returns:
            Dict with product information or None
        """
        try:
            print(f"👕 Searching clothing databases for barcode: {barcode}")
            
            # First try UPCitemdb (works for many retail products including clothing)
            clothing_info = self._get_upcitemdb_data(barcode)
            
            if clothing_info:
                # Enhance with clothing-specific categorization
                category = clothing_info.get('category', '').lower()
                if any(term in category for term in ['apparel', 'clothing', 'fashion', 'textile', 'wear']):
                    clothing_info['product_type'] = 'clothing'
                    clothing_info['materials'] = self._extract_materials_from_description(
                        clothing_info.get('description', '') + ' ' + clothing_info.get('name', '')
                    )
                    return clothing_info
            
            # Try to get clothing brand sustainability info if we have a brand
            if clothing_info and clothing_info.get('brand'):
                brand_info = self._get_brand_sustainability_info(clothing_info['brand'])
                if brand_info:
                    clothing_info.update(brand_info)
            
            return clothing_info
            
        except Exception as e:
            print(f"Error fetching clothing product data: {e}")
            return None
    
    def _extract_materials_from_description(self, text: str) -> List[str]:
        """Extract material information from product description"""
        materials = []
        text_lower = text.lower()
        
        # Common clothing materials
        material_keywords = [
            'cotton', 'polyester', 'wool', 'silk', 'linen', 'denim', 'leather',
            'nylon', 'spandex', 'elastane', 'rayon', 'viscose', 'bamboo',
            'hemp', 'cashmere', 'alpaca', 'mohair', 'acrylic', 'fleece'
        ]
        
        for material in material_keywords:
            if material in text_lower:
                materials.append(material.title())
        
        return materials
    
    def _get_brand_sustainability_info(self, brand: str) -> Optional[Dict[str, Any]]:
        """Get sustainability information about a clothing brand
        
        Args:
            brand: Brand name
            
        Returns:
            Dict with brand sustainability info
        """
        try:
            # Known sustainable clothing brands and their ratings
            sustainable_brands = {
                'patagonia': {'sustainability_rating': 'A+', 'certifications': ['B-Corp', 'Fair Trade', 'Organic Cotton']},
                'eileen fisher': {'sustainability_rating': 'A', 'certifications': ['B-Corp', 'Organic Cotton']},
                'reformation': {'sustainability_rating': 'A', 'certifications': ['Sustainable Packaging']},
                'everlane': {'sustainability_rating': 'B+', 'certifications': ['Ethical Manufacturing']},
                'levi\'s': {'sustainability_rating': 'B', 'certifications': ['Water<Less', 'Organic Cotton']},
                'h&m': {'sustainability_rating': 'C+', 'certifications': ['Conscious Collection', 'Organic Cotton']},
                'zara': {'sustainability_rating': 'C', 'certifications': ['Join Life Collection']},
                'uniqlo': {'sustainability_rating': 'B-', 'certifications': ['Recycled Materials']},
                'nike': {'sustainability_rating': 'B', 'certifications': ['Move to Zero', 'Recycled Materials']},
                'adidas': {'sustainability_rating': 'B+', 'certifications': ['Primegreen', 'Ocean Plastic']}
            }
            
            brand_lower = brand.lower()
            for known_brand, info in sustainable_brands.items():
                if known_brand in brand_lower or brand_lower in known_brand:
                    return {
                        'brand_sustainability': info,
                        'is_sustainable_brand': info['sustainability_rating'] in ['A+', 'A', 'B+']
                    }
            
            return None
            
        except Exception as e:
            print(f"Error getting brand sustainability info: {e}")
            return None
    
    def _analyze_sustainability_with_ai(self, product_data: Dict[str, Any], barcode: str) -> SustainabilityScore:
        """Use Mistral AI to analyze product sustainability"""
        try:
            if not self.mistral_api_key:
                return self._create_fallback_sustainability_score()
            
            # Create comprehensive prompt for sustainability analysis
            prompt = f"""
            Analyze the sustainability of this product and provide detailed scoring:

            Product Information:
            - Name: {product_data.get('name', 'Unknown')}
            - Brand: {product_data.get('brand', 'Unknown')}
            - Category: {product_data.get('category', 'Unknown')}
            - Ingredients: {', '.join(product_data.get('ingredients', []))}
            - Labels/Certifications: {', '.join(product_data.get('labels', []))}
            - Packaging: {product_data.get('packaging', 'Unknown')}
            - Barcode: {barcode}

            Please provide a comprehensive sustainability analysis in JSON format:
            {{
                "overall_score": 0-100,
                "environmental_impact": 0-100,
                "carbon_footprint": 0-100,
                "packaging_score": 0-100,
                "recyclability": 0-100,
                "ethical_sourcing": 0-100,
                "certifications": ["list of eco certifications found"],
                "improvement_suggestions": ["specific suggestions for consumers"],
                "analysis_reasoning": "detailed explanation of scoring",
                "eco_friendly_level": "Poor/Fair/Good/Excellent",
                "key_concerns": ["main environmental concerns"],
                "positive_aspects": ["environmentally positive aspects"]
            }}

            Base your analysis on:
            1. Ingredient sustainability (organic, locally sourced, etc.)
            2. Packaging materials and recyclability
            3. Brand's environmental track record
            4. Carbon footprint considerations
            5. Ethical sourcing practices
            6. Certifications (organic, fair trade, etc.)
            7. End-of-life disposal impact

            Be thorough and provide actionable insights for environmentally conscious consumers.
            """
            
            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "mistral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.3
            }
            
            response = requests.post(self.mistral_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    # Extract JSON from response
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = content[json_start:json_end]
                        analysis = json.loads(json_str)
                        
                        return SustainabilityScore(
                            overall_score=analysis.get('overall_score', 50),
                            environmental_impact=analysis.get('environmental_impact', 50),
                            carbon_footprint=analysis.get('carbon_footprint', 50),
                            packaging_score=analysis.get('packaging_score', 50),
                            recyclability=analysis.get('recyclability', 50),
                            ethical_sourcing=analysis.get('ethical_sourcing', 50),
                            certifications=analysis.get('certifications', []),
                            improvement_suggestions=analysis.get('improvement_suggestions', [])
                        )
                
                except json.JSONDecodeError:
                    pass
            
            return self._create_fallback_sustainability_score()
        
        except Exception as e:
            print(f"Error in AI sustainability analysis: {e}")
            return self._create_fallback_sustainability_score()
    
    def _analyze_clothing_sustainability_with_ai(self, product_data: Dict[str, Any], barcode: str) -> SustainabilityScore:
        """Use Mistral AI to analyze clothing sustainability"""
        try:
            if not self.mistral_api_key:
                return self._create_fallback_clothing_sustainability_score(product_data)
            
            # Create comprehensive prompt for clothing sustainability analysis
            materials = product_data.get('materials', [])
            brand_sustainability = product_data.get('brand_sustainability', {})
            
            prompt = f"""
            Analyze the sustainability of this clothing/textile product and provide detailed scoring:

            Product Information:
            - Name: {product_data.get('name', 'Unknown')}
            - Brand: {product_data.get('brand', 'Unknown')}
            - Category: {product_data.get('category', 'Clothing')}
            - Materials: {', '.join(materials) if materials else 'Not specified'}
            - Brand Sustainability Rating: {brand_sustainability.get('sustainability_rating', 'Unknown')}
            - Brand Certifications: {', '.join(brand_sustainability.get('certifications', []))}

            Please analyze and provide scores (0-100) for:

            1. **Overall Sustainability Score** (0-100)
            2. **Environmental Impact** (0-100) - Consider material production, dyeing, manufacturing
            3. **Carbon Footprint** (0-100) - Manufacturing, transportation, packaging
            4. **Labor Practices** (0-100) - Fair wages, working conditions, ethical sourcing
            5. **Material Sustainability** (0-100) - Organic, recycled, biodegradable materials
            6. **Durability & Longevity** (0-100) - Quality, repairability, timeless design
            7. **End-of-Life** (0-100) - Recyclability, biodegradability, take-back programs

            Also provide:
            - List of positive certifications found
            - 3-5 specific improvement suggestions for more sustainable clothing choices
            - Alternative sustainable brands/products

            Consider these sustainability factors:
            - Organic or recycled materials (cotton, polyester, etc.)
            - Fair Trade and ethical labor certifications
            - Low-impact dyes and manufacturing processes
            - Circular economy practices (take-back programs, recycling)
            - Brand transparency and sustainability commitments
            - Fast fashion vs. slow fashion approach

            Format as JSON with exact keys: overall_score, environmental_impact, carbon_footprint, 
            labor_practices, material_sustainability, durability, end_of_life, certifications, improvement_suggestions, alternatives
            """

            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "mistral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }

            response = requests.post(self.mistral_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from response
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start != -1 and json_end != -1:
                        json_str = ai_response[json_start:json_end]
                        scores_data = json.loads(json_str)
                        
                        return SustainabilityScore(
                            overall_score=float(scores_data.get('overall_score', 50)),
                            environmental_impact=float(scores_data.get('environmental_impact', 50)),
                            carbon_footprint=float(scores_data.get('carbon_footprint', 50)),
                            packaging_score=float(scores_data.get('labor_practices', 50)),  # Reusing field for labor
                            recyclability=float(scores_data.get('end_of_life', 50)),
                            ethical_sourcing=float(scores_data.get('material_sustainability', 50)),
                            certifications=scores_data.get('certifications', []),
                            improvement_suggestions=scores_data.get('improvement_suggestions', [])
                        )
                
                except json.JSONDecodeError:
                    pass
            
            # Fallback if AI analysis fails
            return self._create_fallback_clothing_sustainability_score(product_data)
            
        except Exception as e:
            print(f"Error in AI clothing sustainability analysis: {e}")
            return self._create_fallback_clothing_sustainability_score(product_data)
    
    def _create_fallback_clothing_sustainability_score(self, product_data: Dict[str, Any]) -> SustainabilityScore:
        """Create fallback sustainability score for clothing based on available data"""
        try:
            materials = product_data.get('materials', [])
            brand_sustainability = product_data.get('brand_sustainability', {})
            brand = product_data.get('brand', '').lower()
            
            # Base score
            base_score = 50
            
            # Adjust based on materials
            sustainable_materials = ['organic cotton', 'hemp', 'linen', 'bamboo', 'recycled polyester']
            for material in materials:
                if any(sustainable in material.lower() for sustainable in sustainable_materials):
                    base_score += 10
            
            # Adjust based on brand sustainability rating
            brand_rating = brand_sustainability.get('sustainability_rating', '')
            if brand_rating == 'A+':
                base_score += 25
            elif brand_rating == 'A':
                base_score += 20
            elif brand_rating == 'B+':
                base_score += 15
            elif brand_rating == 'B':
                base_score += 10
            
            # Known fast fashion brands (lower scores)
            fast_fashion_brands = ['shein', 'fashion nova', 'forever 21', 'primark']
            if any(ff_brand in brand for ff_brand in fast_fashion_brands):
                base_score -= 20
            
            score = min(100, max(0, base_score))
            
            certifications = brand_sustainability.get('certifications', [])
            
            suggestions = [
                "Look for clothing made from organic or recycled materials",
                "Choose brands with transparent sustainability practices",
                "Consider the garment's durability and timeless design",
                "Support brands with fair labor certifications",
                "Explore clothing rental or second-hand options"
            ]
            
            return SustainabilityScore(
                overall_score=score,
                environmental_impact=score - 5,
                carbon_footprint=score - 10,
                packaging_score=score + 5,  # Labor practices
                recyclability=score - 15,
                ethical_sourcing=score,
                certifications=certifications,
                improvement_suggestions=suggestions
            )
            
        except Exception as e:
            print(f"Error creating fallback clothing score: {e}")
            return SustainabilityScore(
                overall_score=50,
                environmental_impact=50,
                carbon_footprint=50,
                packaging_score=50,
                recyclability=50,
                ethical_sourcing=50,
                certifications=[],
                improvement_suggestions=["Consider sustainable clothing options"]
            )
    
    def _create_fallback_sustainability_score(self) -> SustainabilityScore:
        """Create a fallback sustainability score when AI analysis fails"""
        return SustainabilityScore(
            overall_score=50,
            environmental_impact=50,
            carbon_footprint=50,
            packaging_score=50,
            recyclability=50,
            ethical_sourcing=50,
            certifications=[],
            improvement_suggestions=[
                "Look for products with eco-friendly certifications",
                "Choose items with minimal packaging",
                "Consider local or organic alternatives",
                "Check for recyclable packaging materials"
            ]
        )
    
    def _get_sustainable_alternatives(self, product_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get suggested sustainable alternatives"""
        alternatives = []
        category = product_data.get('category', '').lower()
        
        # Generic sustainable alternatives based on category
        if 'food' in category or 'drink' in category:
            alternatives = [
                {"name": "Organic equivalent", "reason": "Reduced pesticide use"},
                {"name": "Local/regional brand", "reason": "Lower transportation emissions"},
                {"name": "Bulk/refillable option", "reason": "Reduced packaging waste"}
            ]
        elif 'cleaning' in category or 'household' in category:
            alternatives = [
                {"name": "Eco-friendly cleaning products", "reason": "Biodegradable ingredients"},
                {"name": "Concentrated formulas", "reason": "Less packaging and transportation"},
                {"name": "Refillable containers", "reason": "Reduced plastic waste"}
            ]
        elif 'personal care' in category or 'cosmetic' in category:
            alternatives = [
                {"name": "Natural/organic cosmetics", "reason": "Fewer synthetic chemicals"},
                {"name": "Solid/bar alternatives", "reason": "Plastic-free packaging"},
                {"name": "Refillable containers", "reason": "Reduced packaging waste"}
            ]
        else:
            alternatives = [
                {"name": "Eco-certified alternative", "reason": "Third-party sustainability verification"},
                {"name": "Minimal packaging option", "reason": "Reduced waste"},
                {"name": "Local/regional brand", "reason": "Lower carbon footprint"}
            ]
        
        return alternatives
    
    def _detect_product_category(self, product_data: Dict[str, Any]) -> str:
        """Detect the actual category of a product based on its data"""
        try:
            name = product_data.get('name', '').lower()
            category = product_data.get('category', '').lower()
            description = product_data.get('description', '').lower()
            ingredients = product_data.get('ingredients', [])
            materials = product_data.get('materials', [])
            
            # Food indicators
            food_keywords = [
                'food', 'snack', 'drink', 'beverage', 'meal', 'nutrition', 'organic',
                'juice', 'water', 'soda', 'cookie', 'bread', 'milk', 'cheese',
                'meat', 'vegetable', 'fruit', 'cereal', 'pasta', 'rice', 'coffee',
                'tea', 'chocolate', 'candy', 'sauce', 'soup', 'frozen', 'fresh'
            ]
            
            # Clothing indicators
            clothing_keywords = [
                'clothing', 'apparel', 'shirt', 'pants', 'dress', 'jacket', 'sweater',
                'jeans', 'shorts', 'skirt', 'blouse', 'hoodie', 'coat', 'vest',
                'underwear', 'socks', 'fashion', 'textile', 'fabric', 'cotton',
                'polyester', 'wool', 'silk', 'denim', 'leather', 'shoes', 'boots'
            ]
            
            # Count keyword matches
            food_score = sum(1 for keyword in food_keywords if keyword in name or keyword in category or keyword in description)
            clothing_score = sum(1 for keyword in clothing_keywords if keyword in name or keyword in category or keyword in description)
            
            # Check ingredients/materials
            if ingredients and len(ingredients) > 0:
                food_score += 2  # Having ingredients strongly suggests food
            if materials and len(materials) > 0:
                clothing_score += 2  # Having materials strongly suggests clothing
            
            # Determine category
            if food_score > clothing_score:
                return "food"
            elif clothing_score > food_score:
                return "clothing"
            else:
                return "unknown"
                
        except Exception as e:
            print(f"Error detecting product category: {e}")
            return "unknown"
    
    def _calculate_category_confidence(self, product_data: Dict[str, Any], expected_category: str) -> float:
        """Calculate confidence that the product matches the expected category"""
        try:
            detected_category = self._detect_product_category(product_data)
            
            if detected_category == expected_category:
                return 0.9  # High confidence when categories match
            elif detected_category == "unknown":
                return 0.5  # Medium confidence when unclear
            else:
                return 0.2  # Low confidence when categories don't match
                
        except Exception as e:
            print(f"Error calculating category confidence: {e}")
            return 0.5

def create_sustainability_analyzer() -> ProductSustainabilityAnalyzer:
    """Create a new product sustainability analyzer instance"""
    return ProductSustainabilityAnalyzer()
