import json
import os
import uuid
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class LeaderboardEntry:
    user_id: str
    pseudonym: str
    composite_score: float
    boundary_scores: Dict[str, float]
    submission_date: str
    session_count: int
    campus_affiliation: Optional[str] = None
    
class ProductDatabase:
    """Enhanced product database for barcode lookups and sustainability scoring"""
    
    def __init__(self):
        self.db_file = Path(__file__).parent / "product_db.json"
        self.leaderboard_file = Path(__file__).parent / "leaderboard.json"
        self.load_database()
        self.load_leaderboard()
    
    def load_database(self):
        """Load product database from file or create default"""
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.products = json.load(f)
        else:
            self.products = self.create_default_database()
            self.save_database()
    
    def load_leaderboard(self):
        """Load leaderboard from file or create default"""
        try:
            if self.leaderboard_file.exists():
                with open(self.leaderboard_file, 'r') as f:
                    data = json.load(f)
                    self.leaderboard_entries = [
                        LeaderboardEntry(**entry) for entry in data.get('entries', [])
                    ]
                    self.leaderboard_stats = data.get('stats', {})
            else:
                self.leaderboard_entries = []
                self.leaderboard_stats = {}
                self.seed_leaderboard_data()
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error loading leaderboard, creating new one: {e}")
            self.leaderboard_entries = []
            self.leaderboard_stats = {}
            self.save_leaderboard()  # Save empty leaderboard
    
    def save_database(self):
        """Save current database to file"""
        with open(self.db_file, 'w') as f:
            json.dump(self.products, f, indent=2)
    
    def save_leaderboard(self):
        """Save leaderboard to file"""
        data = {
            'entries': [asdict(entry) for entry in self.leaderboard_entries],
            'stats': self.leaderboard_stats,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.leaderboard_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_default_database(self) -> Dict:
        """Create a comprehensive default product database"""
        return {
            # Food products
            "1234567890123": {
                "name": "Organic Quinoa Salad",
                "brand": "EcoFresh",
                "category": "plant-based",
                "type": "food",
                "materials": ["organic", "plant-based"],
                "sustainability": {
                    "climate": 15,
                    "biosphere": 10,
                    "biogeochemical": 20,
                    "freshwater": 25,
                    "aerosols": 15
                },
                "certifications": ["Organic", "Fair Trade"],
                "packaging": "recyclable"
            },
            "2345678901234": {
                "name": "Beef Burger Meal",
                "brand": "FastFood Co",
                "category": "meat-heavy",
                "type": "food",
                "materials": ["meat", "processed"],
                "sustainability": {
                    "climate": 85,
                    "biosphere": 80,
                    "biogeochemical": 75,
                    "freshwater": 70,
                    "aerosols": 60
                },
                "certifications": [],
                "packaging": "mixed"
            },
            "3456789012345": {
                "name": "Oat Milk Latte",
                "brand": "Plant Café",
                "category": "drink",
                "type": "food",
                "materials": ["plant-based", "oat"],
                "sustainability": {
                    "climate": 20,
                    "biosphere": 25,
                    "biogeochemical": 30,
                    "freshwater": 35,
                    "aerosols": 25
                },
                "certifications": ["Organic"],
                "packaging": "recyclable"
            },
            # Clothing products
            "4567890123456": {
                "name": "Organic Cotton T-Shirt",
                "brand": "EcoWear",
                "category": "cotton",
                "type": "clothing",
                "materials": ["organic cotton", "natural"],
                "sustainability": {
                    "climate": 25,
                    "biosphere": 20,
                    "biogeochemical": 35,
                    "freshwater": 40,
                    "aerosols": 20
                },
                "certifications": ["GOTS", "Fair Trade"],
                "packaging": "minimal"
            },
            "5678901234567": {
                "name": "Polyester Jacket",
                "brand": "Fashion Fast",
                "category": "synthetic",
                "type": "clothing",
                "materials": ["polyester", "synthetic"],
                "sustainability": {
                    "climate": 75,
                    "biosphere": 60,
                    "biogeochemical": 40,
                    "freshwater": 30,
                    "aerosols": 80
                },
                "certifications": [],
                "packaging": "plastic"
            },
            "6789012345678": {
                "name": "Recycled Wool Sweater",
                "brand": "CircularFashion",
                "category": "recycled",
                "type": "clothing",
                "materials": ["recycled wool", "natural"],
                "sustainability": {
                    "climate": 20,
                    "biosphere": 25,
                    "biogeochemical": 20,
                    "freshwater": 25,
                    "aerosols": 30
                },
                "certifications": ["Recycled", "Responsible Wool"],
                "packaging": "recyclable"
            }
        }
    
    def lookup_product(self, barcode: str) -> Optional[Dict]:
        """Look up product by barcode"""
        return self.products.get(barcode)
    
    def add_product(self, barcode: str, product_data: Dict):
        """Add new product to database"""
        self.products[barcode] = product_data
        self.save_database()
    
    def search_products(self, query: str, product_type: Optional[str] = None) -> List[Tuple[str, Dict]]:
        """Search products by name, brand, or category"""
        results = []
        query_lower = query.lower()
        
        for barcode, product in self.products.items():
            if product_type and product.get('type') != product_type:
                continue
                
            searchable_text = ' '.join([
                product.get('name', ''),
                product.get('brand', ''),
                product.get('category', ''),
                ' '.join(product.get('materials', []))
            ]).lower()
            
            if query_lower in searchable_text:
                results.append((barcode, product))
        
        return results
    
    def get_sustainability_score(self, barcode: str) -> Optional[Dict]:
        """Get sustainability scores for a product"""
        product = self.lookup_product(barcode)
        if product and 'sustainability' in product:
            return product['sustainability']
        return None
    
    def get_similar_products(self, barcode: str, limit: int = 5) -> List[Tuple[str, Dict, float]]:
        """Find similar products with better sustainability scores"""
        base_product = self.lookup_product(barcode)
        if not base_product:
            return []
        
        base_type = base_product.get('type')
        base_category = base_product.get('category')
        base_sustainability = base_product.get('sustainability', {})
        
        # Calculate base composite score
        base_score = sum(base_sustainability.values()) / len(base_sustainability) if base_sustainability else 50
        
        similar_products = []
        for other_barcode, other_product in self.products.items():
            if other_barcode == barcode:
                continue
            
            # Must be same type
            if other_product.get('type') != base_type:
                continue
            
            other_sustainability = other_product.get('sustainability', {})
            other_score = sum(other_sustainability.values()) / len(other_sustainability) if other_sustainability else 50
            
            # Only include products with better (lower) scores
            if other_score < base_score:
                similarity = self.calculate_similarity(base_product, other_product)
                similar_products.append((other_barcode, other_product, similarity))
        
        # Sort by similarity (descending) and return top results
        similar_products.sort(key=lambda x: x[2], reverse=True)
        return similar_products[:limit]
    
    def calculate_similarity(self, product1: Dict, product2: Dict) -> float:
        """Calculate similarity between two products (0-1 scale)"""
        similarity = 0.0
        
        # Category similarity
        if product1.get('category') == product2.get('category'):
            similarity += 0.4
        
        # Material similarity
        materials1 = set(product1.get('materials', []))
        materials2 = set(product2.get('materials', []))
        if materials1 and materials2:
            material_overlap = len(materials1.intersection(materials2)) / len(materials1.union(materials2))
            similarity += 0.3 * material_overlap
        
        # Brand similarity (same brand gets bonus)
        if product1.get('brand') == product2.get('brand'):
            similarity += 0.2
        
        # Certification similarity
        certs1 = set(product1.get('certifications', []))
        certs2 = set(product2.get('certifications', []))
        if certs1 and certs2:
            cert_overlap = len(certs1.intersection(certs2)) / len(certs1.union(certs2))
            similarity += 0.1 * cert_overlap
        
        return min(1.0, similarity)
    
    def submit_score(self, user_id: str, composite_score: float, boundary_scores: Dict[str, float], 
                     campus_affiliation: Optional[str] = None) -> Dict:
        """Submit a new EcoScore to the leaderboard"""
        # Generate pseudonym if user doesn't exist
        pseudonym = self._generate_pseudonym(user_id)
        
        # Check if user already has an entry
        existing_entry = None
        for i, entry in enumerate(self.leaderboard_entries):
            if entry.user_id == user_id:
                existing_entry = i
                break
        
        if existing_entry is not None:
            # Update existing entry if score improved
            old_entry = self.leaderboard_entries[existing_entry]
            if composite_score < old_entry.composite_score:  # Lower is better
                self.leaderboard_entries[existing_entry] = LeaderboardEntry(
                    user_id=user_id,
                    pseudonym=old_entry.pseudonym,
                    composite_score=composite_score,
                    boundary_scores=boundary_scores,
                    submission_date=datetime.now().isoformat(),
                    session_count=old_entry.session_count + 1,
                    campus_affiliation=campus_affiliation or old_entry.campus_affiliation
                )
                improvement = old_entry.composite_score - composite_score
                result = {"status": "improved", "improvement": round(improvement, 1)}
            else:
                # Update session count even if score didn't improve
                self.leaderboard_entries[existing_entry].session_count += 1
                result = {"status": "no_improvement", "current_best": old_entry.composite_score}
        else:
            # Create new entry
            new_entry = LeaderboardEntry(
                user_id=user_id,
                pseudonym=pseudonym,
                composite_score=composite_score,
                boundary_scores=boundary_scores,
                submission_date=datetime.now().isoformat(),
                session_count=1,
                campus_affiliation=campus_affiliation
            )
            self.leaderboard_entries.append(new_entry)
            result = {"status": "new_entry", "rank": len(self.leaderboard_entries)}
        
        # Update stats
        self._update_leaderboard_stats()
        
        # Save to file
        self.save_leaderboard()
        
        return result
    
    def get_leaderboard(self, limit: int = 50, boundary_filter: Optional[str] = None) -> Dict:
        """Get leaderboard rankings with privacy protection"""
        # Sort by composite score (lower is better)
        if boundary_filter and boundary_filter in ["climate", "biosphere", "biogeochemical", "freshwater", "aerosols"]:
            # Sort by specific boundary score
            sorted_entries = sorted(
                self.leaderboard_entries, 
                key=lambda x: x.boundary_scores.get(boundary_filter, 100)
            )
        else:
            # Sort by composite score
            sorted_entries = sorted(self.leaderboard_entries, key=lambda x: x.composite_score)
        
        # Prepare leaderboard data with privacy protection
        leaderboard_data = []
        for i, entry in enumerate(sorted_entries[:limit]):
            # Calculate rank
            rank = i + 1
            
            # Create anonymous entry
            leaderboard_data.append({
                "rank": rank,
                "pseudonym": entry.pseudonym,
                "composite_score": entry.composite_score,
                "boundary_scores": entry.boundary_scores,
                "submission_date": entry.submission_date[:10],  # Date only, no time
                "session_count": entry.session_count,
                "campus_affiliation": entry.campus_affiliation if entry.campus_affiliation else "Not specified"
            })
        
        # Calculate statistics
        if self.leaderboard_entries:
            all_scores = [entry.composite_score for entry in self.leaderboard_entries]
            stats = {
                "total_participants": len(self.leaderboard_entries),
                "average_score": round(sum(all_scores) / len(all_scores), 1),
                "best_score": round(min(all_scores), 1),
                "median_score": round(sorted(all_scores)[len(all_scores)//2], 1),
                "boundary_averages": self._calculate_boundary_averages()
            }
        else:
            stats = {
                "total_participants": 0,
                "average_score": 0,
                "best_score": 0,
                "median_score": 0,
                "boundary_averages": {}
            }
        
        return {
            "leaderboard": leaderboard_data,
            "stats": stats,
            "filter": boundary_filter,
            "last_updated": datetime.now().isoformat()
        }
    
    def _generate_pseudonym(self, user_id: str) -> str:
        """Generate a unique pseudonym for privacy"""
        # Use hash of user_id to generate consistent pseudonym
        hash_val = hash(user_id) % 10000
        
        # Animal names for fun pseudonyms
        animals = [
            "Eco-Eagle", "Green-Gecko", "Solar-Sparrow", "Wind-Wolf", "Ocean-Otter",
            "Forest-Fox", "River-Rabbit", "Mountain-Mouse", "Garden-Goose", "Desert-Deer",
            "Arctic-Ant", "Jungle-Jay", "Prairie-Panda", "Coral-Cat", "Meadow-Mole",
            "Valley-Viper", "Canyon-Crane", "Tundra-Tiger", "Savanna-Swan", "Reef-Raven"
        ]
        
        # Adjectives for more variety
        adjectives = [
            "Mighty", "Swift", "Wise", "Bold", "Gentle", "Bright", "Noble", "Calm",
            "Keen", "Brave", "Quick", "Smart", "Kind", "Strong", "Pure", "Free"
        ]
        
        animal = animals[hash_val % len(animals)]
        adjective = adjectives[(hash_val // len(animals)) % len(adjectives)]
        number = (hash_val // (len(animals) * len(adjectives))) % 100
        
        return f"{adjective}-{animal}-{number:02d}"
    
    def _calculate_boundary_averages(self) -> Dict[str, float]:
        """Calculate average scores for each boundary"""
        if not self.leaderboard_entries:
            return {}
        
        boundary_sums = {}
        boundary_counts = {}
        
        for entry in self.leaderboard_entries:
            for boundary, score in entry.boundary_scores.items():
                if boundary not in boundary_sums:
                    boundary_sums[boundary] = 0
                    boundary_counts[boundary] = 0
                boundary_sums[boundary] += score
                boundary_counts[boundary] += 1
        
        return {
            boundary: round(boundary_sums[boundary] / boundary_counts[boundary], 1)
            for boundary in boundary_sums.keys()
        }
    
    def _update_leaderboard_stats(self):
        """Update overall leaderboard statistics"""
        if not self.leaderboard_entries:
            return
        
        # Calculate various statistics
        scores = [entry.composite_score for entry in self.leaderboard_entries]
        session_counts = [entry.session_count for entry in self.leaderboard_entries]
        
        self.leaderboard_stats = {
            "total_submissions": sum(session_counts),
            "unique_users": len(self.leaderboard_entries),
            "average_sessions_per_user": round(sum(session_counts) / len(session_counts), 1),
            "score_distribution": {
                "excellent": len([s for s in scores if s <= 30]),
                "good": len([s for s in scores if 30 < s <= 50]),
                "average": len([s for s in scores if 50 < s <= 70]),
                "needs_improvement": len([s for s in scores if s > 70])
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def seed_leaderboard_data(self):
        """Create initial leaderboard data for demonstration"""
        import random
        
        # Generate sample entries to populate leaderboard
        sample_users = [
            ("user_001", "Lancaster University"),
            ("user_002", "Lancaster University"), 
            ("user_003", "Lancaster University"),
            ("user_004", "Other University"),
            ("user_005", "Lancaster University"),
            ("user_006", "Community Member"),
            ("user_007", "Lancaster University"),
            ("user_008", "Lancaster University"),
            ("user_009", "Other University"),
            ("user_010", "Lancaster University")
        ]
        
        for user_id, affiliation in sample_users:
            # Generate realistic scores
            base_score = random.uniform(25, 75)
            variation = random.uniform(-10, 10)
            
            boundary_scores = {
                "climate": max(10, min(90, base_score + random.uniform(-15, 15))),
                "biosphere": max(10, min(90, base_score + random.uniform(-15, 15))),
                "biogeochemical": max(10, min(90, base_score + random.uniform(-15, 15))),
                "freshwater": max(10, min(90, base_score + random.uniform(-15, 15))),
                "aerosols": max(10, min(90, base_score + random.uniform(-15, 15)))
            }
            
            composite = sum(boundary_scores.values()) / len(boundary_scores)
            
            entry = LeaderboardEntry(
                user_id=user_id,
                pseudonym=self._generate_pseudonym(user_id),
                composite_score=round(composite, 1),
                boundary_scores={k: round(v, 1) for k, v in boundary_scores.items()},
                submission_date=(datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                session_count=random.randint(1, 5),
                campus_affiliation=affiliation
            )
            
            self.leaderboard_entries.append(entry)
        
        self._update_leaderboard_stats()
        self.save_leaderboard()

# Global instance
product_db = ProductDatabase()

def get_product_info(barcode: str) -> Optional[Dict]:
    """Get product information by barcode"""
    return product_db.lookup_product(barcode)

def get_sustainability_alternatives(barcode: str) -> List[Dict]:
    """Get more sustainable alternatives for a product"""
    alternatives = product_db.get_similar_products(barcode)
    result = []
    
    for alt_barcode, alt_product, similarity in alternatives:
        alt_sustainability = alt_product.get('sustainability', {})
        alt_score = sum(alt_sustainability.values()) / len(alt_sustainability) if alt_sustainability else 50
        
        result.append({
            "barcode": alt_barcode,
            "name": alt_product.get('name'),
            "brand": alt_product.get('brand'),
            "sustainability_score": round(alt_score, 1),
            "similarity": round(similarity, 2),
            "why_better": generate_improvement_reason(alt_sustainability),
            "certifications": alt_product.get('certifications', [])
        })
    
    return result

def generate_improvement_reason(sustainability: Dict) -> str:
    """Generate a reason why this alternative is better"""
    if not sustainability:
        return "Better overall environmental impact"
    
    # Find the best-scoring boundary
    best_boundary = min(sustainability.items(), key=lambda x: x[1])
    boundary_names = {
        "climate": "lower carbon footprint",
        "biosphere": "better for biodiversity", 
        "biogeochemical": "reduced chemical impact",
        "freshwater": "uses less water",
        "aerosols": "less pollution"
    }
    
    return boundary_names.get(best_boundary[0], "better environmental performance")

if __name__ == '__main__':
    # Test the database
    test_barcode = "1234567890123"
    product = get_product_info(test_barcode)
    print(f"Product: {product}")
    
    alternatives = get_sustainability_alternatives("2345678901234")  # Beef burger
    print(f"Alternatives: {alternatives}")
