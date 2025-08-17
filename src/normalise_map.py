# ecoscore/normalise_map.py
from typing import Dict

_food_map: Dict[str, str] = {
    "steak": "beef",
    "ground_beef": "beef",
    "burger": "beef",
    "chook": "chicken",
    "poultry": "chicken",
    "brown_rice": "rice",
    "white_rice": "rice",
}

_fashion_map: Dict[str, str] = {
    "tee": "tshirt",
    "t-shirt": "tshirt",
    "denim_pants": "jeans",
}

_mobility_map: Dict[str, str] = {
    "uber": "car",
    "lyft": "car",
    "tube": "train",
    "subway": "train",
}

def canonicalise_food(x: str) -> str:
    x = (x or "").strip().lower().replace(" ", "_")
    return _food_map.get(x, x)

def canonicalise_fashion(x: str) -> str:
    x = (x or "").strip().lower().replace(" ", "_")
    return _fashion_map.get(x, x)

def canonicalise_mobility(x: str) -> str:
    x = (x or "").strip().lower().replace(" ", "_")
    return _mobility_map.get(x, x)