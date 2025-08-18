#!/usr/bin/env python3
"""
Test script for the enhanced /api/intake endpoint
This validates that the endpoint meets project deliverable requirements
"""

import json
import urllib.request
import urllib.parse

def test_intake_endpoint():
    """Test the enhanced /api/intake endpoint for normalized output"""
    
    # Test data - comprehensive form submission
    test_data = {
        "meal_type": "plant-based",
        "meal_origin": "Locally sourced", 
        "meal_leftovers": "None left, finished",
        "outfit_material": "mostly natural",
        "mobility_mode": "bike",
        "mobility_distance": "5",
        "resource_action": ["switch off unused electronics", "reuse items instead of buying new"],
        "food_barcode": "1234567890123"
    }
    
    # Convert to JSON
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    url = "http://localhost:8000/api/intake"
    req = urllib.request.Request(url, data=json_data)
    req.add_header('Content-Type', 'application/json')
    
    try:
        print("🧪 Testing enhanced /api/intake endpoint...")
        print(f"📤 Sending data: {test_data}")
        print()
        
        # Make request
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode())
            
        print("✅ Response received successfully!")
        print("📨 Full Response:")
        print(json.dumps(response_data, indent=2))
        print()
        
        # Validate deliverable compliance
        print("🔍 DELIVERABLE COMPLIANCE CHECK:")
        print("📋 Required: 'REST endpoint: POST /api/intake → normalised item list for the Scoring Engine'")
        print()
        
        if 'normalized_items' in response_data:
            items = response_data['normalized_items']
            print(f"✅ Found normalized_items: {len(items)} items")
            
            # Check item structure
            for i, item in enumerate(items):
                print(f"   📦 Item {i+1}: {item.get('type', 'unknown')} - {item.get('category', 'unknown')}")
                
                # Check required fields for scoring engine
                required_fields = ['id', 'type', 'category', 'attributes', 'sustainability_metrics']
                missing_fields = [field for field in required_fields if field not in item]
                
                if missing_fields:
                    print(f"   ⚠️  Missing fields: {missing_fields}")
                else:
                    print(f"   ✅ All required fields present")
            
            print()
            print("🎯 SCORING ENGINE READINESS:")
            if all('sustainability_metrics' in item for item in items):
                print("✅ All items have sustainability_metrics for scoring")
            else:
                print("⚠️  Some items missing sustainability_metrics")
                
            if all('confidence' in item for item in items):
                print("✅ All items have confidence scores")
            else:
                print("⚠️  Some items missing confidence scores")
                
            print()
            print("📊 COMPREHENSIVE ANALYSIS:")
            if 'comprehensive_analysis' in response_data:
                analysis = response_data['comprehensive_analysis']
                print("✅ Comprehensive analysis provided")
                print(f"   🌍 Overall impact: {analysis.get('overall_impact', {})}")
                print(f"   📂 Categories analyzed: {list(analysis.get('category_breakdown', {}).keys())}")
            else:
                print("⚠️  No comprehensive analysis found")
                
            print()
            print("🏆 ECO-SCORE CALCULATION:")
            if 'eco_score' in response_data:
                eco_score = response_data['eco_score']
                print("✅ Eco-score calculation provided")
                print(f"   📊 Overall score: {eco_score.get('overall_score')}")
                print(f"   🎖️  Grade: {eco_score.get('grade')}")
                print(f"   📈 Percentile: {eco_score.get('percentile')}")
            else:
                print("⚠️  No eco-score calculation found")
                
        else:
            print("❌ No normalized_items found in response")
            print("🚨 DELIVERABLE NOT MET: Endpoint does not return normalized item list")
            
        print()
        print("=" * 60)
        print("📝 DELIVERABLE ASSESSMENT:")
        
        meets_requirements = (
            'normalized_items' in response_data and
            len(response_data['normalized_items']) > 0 and
            all('sustainability_metrics' in item for item in response_data['normalized_items'])
        )
        
        if meets_requirements:
            print("✅ DELIVERABLE MET: POST /api/intake returns normalized item list suitable for Scoring Engine")
        else:
            print("❌ DELIVERABLE NOT MET: Response structure needs adjustment")
            
        return meets_requirements
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        print("🚨 Make sure the server is running on http://localhost:8000")
        return False

if __name__ == "__main__":
    test_intake_endpoint()
