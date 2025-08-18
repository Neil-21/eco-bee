"""
EcoBee Recommender System
Graph-based recommender for sustainable actions and campus resources
Uses graph embeddings and collaborative filtering for personalized recommendations
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class Action:
    id: str
    name: str
    description: str
    category: str  # food, clothing, transport, lifestyle
    impact_reduction: Dict[str, float]  # boundary -> impact reduction percentage
    difficulty: str  # easy, medium, hard
    time_commitment: str  # daily, weekly, monthly, one-time
    cost: str  # free, low, medium, high
    social_aspect: bool  # whether it involves community/social elements
    campus_specific: bool  # whether it's campus-specific
    tags: List[str]

@dataclass
class Resource:
    id: str
    name: str
    description: str
    type: str  # repair_cafe, swap_shop, bike_share, etc.
    location: str  # general location description
    availability: str  # when available
    cost: str
    related_actions: List[str]  # action IDs this resource supports
    tags: List[str]

class EcoBeeRecommender:
    def __init__(self):
        self.actions = self._load_actions()
        self.resources = self._load_resources()
        self.user_profiles = {}  # user_id -> profile data
        self.action_graph = self._build_action_graph()
    
    def _load_actions(self) -> Dict[str, Action]:
        """Load sustainable actions database"""
        actions_data = {
            # Food Actions
            "plant_meals": Action(
                id="plant_meals",
                name="Plant-Based Meals 3x/week",
                description="Replace meat meals with plant-based alternatives 3 times per week",
                category="food",
                impact_reduction={"climate": 25, "biosphere": 20, "biogeochemical": 30, "freshwater": 15, "aerosols": 10},
                difficulty="easy",
                time_commitment="daily",
                cost="free",
                social_aspect=True,
                campus_specific=False,
                tags=["diet", "health", "climate", "beginner-friendly"]
            ),
            "local_food": Action(
                id="local_food",
                name="Choose Local & Seasonal Food",
                description="Buy locally sourced, seasonal produce when possible",
                category="food",
                impact_reduction={"climate": 15, "biosphere": 25, "freshwater": 10, "aerosols": 20},
                difficulty="medium",
                time_commitment="weekly",
                cost="low",
                social_aspect=False,
                campus_specific=True,
                tags=["local", "seasonal", "farmers-market"]
            ),
            "food_waste_reduction": Action(
                id="food_waste_reduction",
                name="Reduce Food Waste",
                description="Plan meals, store food properly, and compost scraps",
                category="food",
                impact_reduction={"climate": 20, "biogeochemical": 15, "freshwater": 10},
                difficulty="easy",
                time_commitment="daily",
                cost="free",
                social_aspect=False,
                campus_specific=False,
                tags=["waste", "planning", "composting"]
            ),
            
            # Clothing Actions
            "secondhand_shopping": Action(
                id="secondhand_shopping",
                name="Shop Second-Hand First",
                description="Check thrift stores and online marketplaces before buying new clothes",
                category="clothing",
                impact_reduction={"climate": 60, "freshwater": 70, "aerosols": 50, "biosphere": 40},
                difficulty="easy",
                time_commitment="monthly",
                cost="low",
                social_aspect=True,
                campus_specific=True,
                tags=["thrift", "vintage", "budget-friendly"]
            ),
            "clothing_repair": Action(
                id="clothing_repair",
                name="Repair & Mend Clothes",
                description="Fix damaged clothes instead of discarding them",
                category="clothing",
                impact_reduction={"climate": 80, "freshwater": 90, "aerosols": 70},
                difficulty="medium",
                time_commitment="monthly",
                cost="low",
                social_aspect=True,
                campus_specific=True,
                tags=["repair", "diy", "skills"]
            ),
            "clothing_swap": Action(
                id="clothing_swap",
                name="Join Clothing Swaps",
                description="Participate in campus clothing exchange events",
                category="clothing",
                impact_reduction={"climate": 70, "freshwater": 80, "aerosols": 60},
                difficulty="easy",
                time_commitment="monthly",
                cost="free",
                social_aspect=True,
                campus_specific=True,
                tags=["swap", "community", "social"]
            ),
            
            # Transport Actions
            "active_transport": Action(
                id="active_transport",
                name="Walk or Bike for Short Trips",
                description="Use walking or cycling for trips under 3km",
                category="transport",
                impact_reduction={"climate": 90, "aerosols": 85, "biosphere": 30},
                difficulty="easy",
                time_commitment="daily",
                cost="free",
                social_aspect=False,
                campus_specific=False,
                tags=["health", "fitness", "zero-emission"]
            ),
            "public_transport": Action(
                id="public_transport",
                name="Use Public Transport",
                description="Choose buses, trains, or campus shuttles for longer trips",
                category="transport",
                impact_reduction={"climate": 60, "aerosols": 70, "biosphere": 20},
                difficulty="easy",
                time_commitment="daily",
                cost="low",
                social_aspect=False,
                campus_specific=True,
                tags=["public", "affordable", "accessible"]
            ),
            "carpool": Action(
                id="carpool",
                name="Carpool or Rideshare",
                description="Share rides with friends or use carpooling apps",
                category="transport",
                impact_reduction={"climate": 40, "aerosols": 45},
                difficulty="medium",
                time_commitment="weekly",
                cost="low",
                social_aspect=True,
                campus_specific=True,
                tags=["social", "cost-sharing", "flexible"]
            ),
            
            # Lifestyle Actions
            "minimal_consumption": Action(
                id="minimal_consumption",
                name="Practice Mindful Consumption",
                description="Buy only what you need and choose quality over quantity",
                category="lifestyle",
                impact_reduction={"climate": 30, "biosphere": 35, "freshwater": 25, "aerosols": 40},
                difficulty="medium",
                time_commitment="daily",
                cost="free",
                social_aspect=False,
                campus_specific=False,
                tags=["mindfulness", "minimalism", "budgeting"]
            ),
            "digital_minimalism": Action(
                id="digital_minimalism",
                name="Reduce Digital Footprint",
                description="Stream less, use devices longer, choose efficient settings",
                category="lifestyle",
                impact_reduction={"climate": 15, "aerosols": 20},
                difficulty="easy",
                time_commitment="daily",
                cost="free",
                social_aspect=False,
                campus_specific=False,
                tags=["digital", "energy", "screen-time"]
            ),
            "reusable_items": Action(
                id="reusable_items",
                name="Use Reusable Items",
                description="Carry reusable water bottle, coffee cup, and shopping bags",
                category="lifestyle",
                impact_reduction={"aerosols": 60, "climate": 10, "biosphere": 20},
                difficulty="easy",
                time_commitment="daily",
                cost="low",
                social_aspect=False,
                campus_specific=False,
                tags=["reusable", "waste-reduction", "habit"]
            )
        }
        
        return actions_data
    
    def _load_resources(self) -> Dict[str, Resource]:
        """Load campus and local resources database"""
        resources_data = {
            "campus_repair_cafe": Resource(
                id="campus_repair_cafe",
                name="Campus Repair Café",
                description="Free repair services for electronics, clothing, and bikes",
                type="repair_cafe",
                location="Student Union Building",
                availability="Saturdays 10am-4pm",
                cost="free",
                related_actions=["clothing_repair", "minimal_consumption"],
                tags=["repair", "free", "community", "skills"]
            ),
            "clothing_swap_shop": Resource(
                id="clothing_swap_shop",
                name="Student Clothing Exchange",
                description="Drop off unwanted clothes, take what you need",
                type="swap_shop",
                location="Campus Sustainability Center",
                availability="Mon-Fri 9am-5pm",
                cost="free",
                related_actions=["clothing_swap", "secondhand_shopping"],
                tags=["clothing", "free", "exchange"]
            ),
            "bike_share": Resource(
                id="bike_share",
                name="Campus Bike Share",
                description="Short-term bike rental for campus and local trips",
                type="bike_share",
                location="Multiple campus locations",
                availability="24/7",
                cost="low",
                related_actions=["active_transport"],
                tags=["transport", "bike", "convenient"]
            ),
            "local_farmers_market": Resource(
                id="local_farmers_market",
                name="Weekly Farmers Market",
                description="Local, seasonal produce from regional farmers",
                type="farmers_market",
                location="Town Square",
                availability="Saturdays 8am-2pm",
                cost="medium",
                related_actions=["local_food"],
                tags=["food", "local", "seasonal", "community"]
            ),
            "campus_garden": Resource(
                id="campus_garden",
                name="Campus Community Garden",
                description="Plot rental and workshops for growing your own food",
                type="community_garden",
                location="Behind Environmental Science Building",
                availability="Daily dawn-dusk",
                cost="low",
                related_actions=["local_food", "food_waste_reduction"],
                tags=["gardening", "education", "food", "community"]
            ),
            "sustainability_workshops": Resource(
                id="sustainability_workshops",
                name="Sustainability Skill Workshops",
                description="Monthly workshops on repair, cooking, and sustainable living",
                type="workshop",
                location="Various campus locations",
                availability="Monthly events",
                cost="free",
                related_actions=["clothing_repair", "food_waste_reduction", "minimal_consumption"],
                tags=["education", "skills", "community", "free"]
            )
        }
        
        return resources_data
    
    def _build_action_graph(self) -> Dict:
        """Build graph connections between actions based on shared attributes"""
        graph = {}
        
        for action_id, action in self.actions.items():
            connections = []
            
            # Connect actions in same category
            for other_id, other_action in self.actions.items():
                if action_id != other_id:
                    similarity = self._calculate_action_similarity(action, other_action)
                    if similarity > 0.3:  # Threshold for connection
                        connections.append((other_id, similarity))
            
            # Sort by similarity
            connections.sort(key=lambda x: x[1], reverse=True)
            graph[action_id] = connections
        
        return graph
    
    def _calculate_action_similarity(self, action1: Action, action2: Action) -> float:
        """Calculate similarity between two actions"""
        similarity = 0.0
        
        # Category similarity
        if action1.category == action2.category:
            similarity += 0.3
        
        # Difficulty similarity
        if action1.difficulty == action2.difficulty:
            similarity += 0.2
        
        # Time commitment similarity
        if action1.time_commitment == action2.time_commitment:
            similarity += 0.1
        
        # Tag overlap
        common_tags = set(action1.tags) & set(action2.tags)
        tag_similarity = len(common_tags) / max(len(action1.tags), len(action2.tags), 1)
        similarity += tag_similarity * 0.3
        
        # Impact profile similarity
        impact_similarity = self._calculate_impact_similarity(
            action1.impact_reduction, action2.impact_reduction
        )
        similarity += impact_similarity * 0.1
        
        return similarity
    
    def _calculate_impact_similarity(self, impact1: Dict, impact2: Dict) -> float:
        """Calculate similarity between impact profiles"""
        if not impact1 or not impact2:
            return 0.0
        
        common_boundaries = set(impact1.keys()) & set(impact2.keys())
        if not common_boundaries:
            return 0.0
        
        differences = []
        for boundary in common_boundaries:
            diff = abs(impact1[boundary] - impact2[boundary]) / 100.0
            differences.append(diff)
        
        avg_difference = sum(differences) / len(differences)
        return 1.0 - avg_difference
    
    def get_personalized_recommendations(
        self, 
        boundary_scores: Dict[str, float], 
        user_context: Optional[Dict] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Generate personalized action recommendations based on user's boundary scores
        """
        if user_context is None:
            user_context = {}
        
        # Identify priority boundaries (highest impact scores)
        priority_boundaries = sorted(
            boundary_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        recommendations = []
        
        for action_id, action in self.actions.items():
            score = self._calculate_action_score(
                action, priority_boundaries, user_context
            )
            
            if score > 0:
                recommendations.append({
                    "action_id": action_id,
                    "action": action.name,
                    "description": action.description,
                    "category": action.category,
                    "impact_reduction": action.impact_reduction,
                    "difficulty": action.difficulty,
                    "time_commitment": action.time_commitment,
                    "cost": action.cost,
                    "social_aspect": action.social_aspect,
                    "campus_specific": action.campus_specific,
                    "tags": action.tags,
                    "recommendation_score": round(score, 2),
                    "related_resources": self._get_related_resources(action_id)
                })
        
        # Sort by recommendation score and return top recommendations
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return recommendations[:limit]
    
    def _calculate_action_score(
        self, 
        action: Action, 
        priority_boundaries: List[Tuple[str, float]], 
        user_context: Dict
    ) -> float:
        """Calculate recommendation score for an action"""
        score = 0.0
        
        # Impact relevance (how well action addresses user's worst boundaries)
        for boundary, user_score in priority_boundaries:
            if boundary in action.impact_reduction:
                # Higher user score = more room for improvement
                # Higher action impact = better recommendation
                impact_score = (user_score / 100.0) * (action.impact_reduction[boundary] / 100.0)
                score += impact_score * 10  # Scale up
        
        # User context adjustments
        difficulty_pref = user_context.get("difficulty_preference", "easy")
        if action.difficulty == difficulty_pref:
            score += 2
        elif action.difficulty == "easy" and difficulty_pref != "hard":
            score += 1
        
        time_availability = user_context.get("time_availability", "daily")
        if action.time_commitment == time_availability:
            score += 1
        
        budget_pref = user_context.get("budget_preference", "free")
        cost_mapping = {"free": 3, "low": 2, "medium": 1, "high": 0}
        budget_mapping = {"free": 3, "low": 2, "medium": 1, "high": 0}
        
        if cost_mapping.get(action.cost, 0) >= budget_mapping.get(budget_pref, 0):
            score += 1
        
        # Social preference
        social_pref = user_context.get("social_preference", True)
        if action.social_aspect == social_pref:
            score += 0.5
        
        # Campus-specific bonus for students
        if action.campus_specific and user_context.get("is_student", True):
            score += 1
        
        return score
    
    def _get_related_resources(self, action_id: str) -> List[Dict]:
        """Get campus/local resources that support this action"""
        related = []
        
        for resource_id, resource in self.resources.items():
            if action_id in resource.related_actions:
                related.append({
                    "resource_id": resource_id,
                    "name": resource.name,
                    "description": resource.description,
                    "type": resource.type,
                    "location": resource.location,
                    "availability": resource.availability,
                    "cost": resource.cost,
                    "tags": resource.tags
                })
        
        return related
    
    def get_action_details(self, action_id: str) -> Optional[Dict]:
        """Get detailed information about a specific action"""
        if action_id not in self.actions:
            return None
        
        action = self.actions[action_id]
        
        return {
            "action_id": action_id,
            "name": action.name,
            "description": action.description,
            "category": action.category,
            "impact_reduction": action.impact_reduction,
            "difficulty": action.difficulty,
            "time_commitment": action.time_commitment,
            "cost": action.cost,
            "social_aspect": action.social_aspect,
            "campus_specific": action.campus_specific,
            "tags": action.tags,
            "related_resources": self._get_related_resources(action_id),
            "similar_actions": [
                self.actions[aid].name for aid, _ in self.action_graph.get(action_id, [])[:3]
            ]
        }
    
    def get_all_resources(self) -> List[Dict]:
        """Get all available campus and local resources"""
        return [
            {
                "resource_id": resource_id,
                "name": resource.name,
                "description": resource.description,
                "type": resource.type,
                "location": resource.location,
                "availability": resource.availability,
                "cost": resource.cost,
                "related_actions": [
                    self.actions[aid].name for aid in resource.related_actions 
                    if aid in self.actions
                ],
                "tags": resource.tags
            }
            for resource_id, resource in self.resources.items()
        ]
    
    def get_actions_by_category(self, category: str) -> List[Dict]:
        """Get all actions in a specific category"""
        category_actions = []
        
        for action_id, action in self.actions.items():
            if action.category.lower() == category.lower():
                category_actions.append({
                    "action_id": action_id,
                    "name": action.name,
                    "description": action.description,
                    "impact_reduction": action.impact_reduction,
                    "difficulty": action.difficulty,
                    "tags": action.tags
                })
        
        return category_actions

# Global recommender instance
recommender = EcoBeeRecommender()

def get_recommendations(boundary_scores: Dict[str, float], user_context: Dict = None) -> List[Dict]:
    """Main function to get personalized recommendations"""
    return recommender.get_personalized_recommendations(boundary_scores, user_context)

def get_action_info(action_id: str) -> Dict:
    """Get information about a specific action"""
    return recommender.get_action_details(action_id)

def get_campus_resources() -> List[Dict]:
    """Get all campus and local resources"""
    return recommender.get_all_resources()
