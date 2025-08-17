import json
from typing import Dict, List

# Simple ecoscore stub: normalise values to 0-100 and average

# Example factor tables would map categories/materials to boundary pressure scores
# For prototype we provide a tiny inline table
FACTOR_TABLE = {
    "meal": {
        "plant-based": 10,
        "mixed": 50,
        "meat-heavy": 90,
        "snack": 40,
        "drink": 20
    },
    "outfit": {
        "mostly natural": 20,
        "mostly synthetic": 70,
        "mixed": 45
    }
}

def score_item(item: Dict) -> Dict:
    t = item.get('type')
    cat = item.get('category')
    base = FACTOR_TABLE.get(t, {}).get(cat, 50)
    # Normalise to 0-100 (already in 0-100)
    return {"per_boundary": {"composite": base}, "composite": base}

def score_batch(items: List[Dict]) -> Dict:
    results = [score_item(i) for i in items]
    composites = [r['composite'] for r in results]
    overall = sum(composites)/len(composites) if composites else 0
    return {"items": results, "composite": overall}

if __name__ == '__main__':
    test_items = [{"type": "meal", "category": "meat-heavy"}, {"type": "outfit", "category": "mostly synthetic"}]
    print(json.dumps(score_batch(test_items), indent=2))
