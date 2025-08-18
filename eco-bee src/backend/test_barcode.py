#!/usr/bin/env python3
"""
Test script to debug barcode product lookup
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from product_sustainability import create_sustainability_analyzer

def test_barcode_lookup(barcode):
    """Test barcode lookup"""
    print(f"Testing barcode: {barcode}")
    
    analyzer = create_sustainability_analyzer()
    
    # Test Open Food Facts first
    print("\n1. Testing Open Food Facts API...")
    basic_info = analyzer._get_openfoodfacts_data(barcode)
    if basic_info:
        print(f"✅ Found product in OpenFoodFacts: {basic_info['name']}")
        print(f"   Brand: {basic_info['brand']}")
        print(f"   Category: {basic_info['category']}")
        print(f"   Ingredients: {basic_info['ingredients'][:3]}...")  # First 3 ingredients
    else:
        print("❌ Not found in OpenFoodFacts")
    
    # Test UPC Item DB if not found
    if not basic_info:
        print("\n2. Testing UPCitemdb API...")
        basic_info = analyzer._get_upcitemdb_data(barcode)
        if basic_info:
            print(f"✅ Found product in UPCitemdb: {basic_info['name']}")
            print(f"   Brand: {basic_info['brand']}")
            print(f"   Category: {basic_info['category']}")
        else:
            print("❌ Not found in UPCitemdb")
    
    # Test full product info lookup
    print("\n3. Testing full product analysis...")
    product_info = analyzer.get_product_info(barcode)
    if product_info:
        print(f"✅ Full analysis completed!")
        print(f"   Product: {product_info.name}")
        print(f"   Sustainability Score: {product_info.sustainability_score.overall_score}/100")
        print(f"   Eco Rating: {analyzer._get_eco_rating(product_info.sustainability_score.overall_score)}")
        print(f"   Certifications: {product_info.sustainability_score.certifications}")
        print(f"   Suggestions: {product_info.sustainability_score.improvement_suggestions[:2]}")
    else:
        print("❌ Full analysis failed")
    
    return product_info

if __name__ == "__main__":
    # Test with the barcode you mentioned
    test_barcode = "5012035927608"
    
    print("🧪 Barcode Product Lookup Test")
    print("=" * 50)
    
    result = test_barcode_lookup(test_barcode)
    
    if result:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n❌ Test failed - no product data retrieved")
