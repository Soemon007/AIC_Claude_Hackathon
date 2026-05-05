import json
import os
from typing import List, Dict, Any

# 1. Load the JSON data dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "data", "harmful_foods.json")

with open(JSON_PATH, "r", encoding="utf-8") as file:
    PCOS_DATA = json.load(file)

def filter_ingredients(normalized_ingredients: List[str], meal_type: str) -> Dict[str, Any]:
    """
    Evaluates ingredients against PCOS medical rules.
    Returns good ingredients, limited ingredients (with context), and removed items.
    """
    meal_type = meal_type.lower() # e.g., "breakfast", "lunch", "dinner"
    
    good_ingredients = []
    limited_ingredients = []
    removed_ingredients = [] # Important for showing UI warnings
    
    strict_avoid_list = PCOS_DATA.get("strict_avoid", [])
    limit_data_dict = PCOS_DATA.get("limit_or_swap", {})
    
    for item in normalized_ingredients:
        item_lower = item.lower()
        
        # Rule 1: Is it strictly banned? (e.g., "maida", "maggi")
        if item_lower in strict_avoid_list:
            removed_ingredients.append({
                "ingredient": item,
                "reason": "Highly processed or inflammatory. Strongly worsens PCOS insulin resistance."
            })
            continue
            
        # Rule 2: Is it in the limit/swap list? (e.g., "white rice")
        if item_lower in limit_data_dict:
            item_data = limit_data_dict[item_lower]
            limits_by_time = item_data.get("max_limit", {})
            
            # Extract the specific limit for this meal time
            specific_limit = limits_by_time.get(meal_type, "Use very sparingly")
            
            # SMART FEATURE: If the limit is 0 for this specific meal time, ban it for this meal!
            if "avoid" in specific_limit.lower() or "0g" in specific_limit.lower() or "0ml" in specific_limit.lower():
                removed_ingredients.append({
                    "ingredient": item,
                    "reason": f"Not recommended for {meal_type}. {item_data.get('pcos_reason', '')}",
                    "suggested_swap": item_data.get("swap", "")
                })
            else:
                # It is allowed, but in limits
                limited_ingredients.append({
                    "ingredient": item,
                    "allowed_limit": specific_limit,
                    "suggested_swap": item_data.get("swap", ""),
                    "reasoning": item_data.get("pcos_reason", "")
                })
            continue
            
        # Rule 3: If it passes both lists, it is safe to eat!
        good_ingredients.append(item)
        
    return {
        "good_ingredients": good_ingredients,
        # "limited_ingredients": limited_ingredients,
        # "removed_ingredients": removed_ingredients
    }

# --- Quick Test (You can delete this before submission) ---
if __name__ == "__main__":
    # Simulating a user's normalized input for a DINNER meal
    test_ingredients = ["chicken", "spinach", "white rice", "maggi", "tomato", "potato"]
    test_meal_time = "dinner"
    
    result = filter_ingredients(test_ingredients, test_meal_time)
    
    print(json.dumps(result, indent=2))