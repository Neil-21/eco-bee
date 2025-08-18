import json

BOUNDARY_LIMITS = {
    "climate": 50.0,             # kg CO2-eq per functional unit (worst case)
    "biodiversity": 1.0,         # species lost per unit
    "land_use": 100.0,           # m²-year
    "water": 500.0,              # m³ freshwater
    "nutrient_pollution": 10.0,  # kg N/P
    "chemical_pollution": 5.0,   # kg toxic eq
    "air_quality": 0.1,          # kg PM2.5 eq
    "ocean_health": 20.0,        # kg CO2 eq / acidification
    "ozone_layer": 0.01           # kg CFC-11 eq
}

# Category -> specific activity mapping
CATEGORY_TO_SPECIFIC = {
    "mobility": {
        "car": "car_petrol_km",  # default petrol
    },
}

# Load lookup JSON with impact factors
with open("lookup.json") as f:
    LOOKUP = json.load(f)


def normalise_score_by_category(category_inputs):
    per_boundary_scores = {k: 0 for k in BOUNDARY_LIMITS} #initialize scores for each boundary to 0

    # resolve ambiguities and accumulate impacts
    for category, activities in category_inputs.items():
        for generic, amount in activities.items():
            specific_key = CATEGORY_TO_SPECIFIC.get(category, {}).get(generic, generic)

            # access nested JSON: LOOKUP[category][specific_key]
            impacts = LOOKUP.get(category, {}).get(specific_key)
            if impacts is None:
                print(f"Warning: {specific_key} not in lookup under category {category}")
                continue

            for boundary, impact_value in impacts.items():
                boundary_name = boundary.split("_")[0]
                if boundary_name in per_boundary_scores:
                    per_boundary_scores[boundary_name] += impact_value * amount

    # normalise to 0-100, where 100 = best, 0 = worst
    normalised_scores = {}
    for boundary, total in per_boundary_scores.items():
        limit = BOUNDARY_LIMITS[boundary]
        score = max(0, min(100, 100 * (1 - total / limit))) #0 is worst, 100 is best
        normalised_scores[boundary] = score

    # composite: average of all boundaries
    composite = sum(normalised_scores.values()) / len(normalised_scores)

    return {"per_boundary_scores": normalised_scores, "composite": composite}



# Example usage
category_inputs = {
    "mobility": {"car": 50},
    "food": {"beef": 2},
    "fashion": {"cotton_shirt": 1}
}

scores = normalise_score_by_category(category_inputs)
print(scores)
