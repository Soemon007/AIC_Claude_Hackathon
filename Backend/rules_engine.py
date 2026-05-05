"""
PCOS Rule Engine
----------------
Scores ingredients for PCOS-friendliness and personal goal alignment.
"""

GOAL_PROFILES = {
    "weight_loss": {
        "display_name": "Weight Loss",
        "macro_focus": ["protein", "fiber", "glycemic control"],
        "scoring_bias": {
            "carb_penalty": 0.8,
            "sugar_penalty": 0.8,
            "protein_bonus": 0.8,
            "fiber_bonus": 0.8,
            "fat_penalty": 0.2,
        },
    },
    "energy": {
        "display_name": "Energy Support",
        "macro_focus": ["steady carbohydrates", "protein", "fiber"],
        "scoring_bias": {
            "carb_penalty": 0.3,
            "sugar_penalty": 0.7,
            "protein_bonus": 0.6,
            "fiber_bonus": 0.7,
            "fat_penalty": 0.1,
        },
    },
    "fertility": {
        "display_name": "Fertility Support",
        "macro_focus": ["glycemic balance", "whole foods", "protein"],
        "scoring_bias": {
            "carb_penalty": 0.5,
            "sugar_penalty": 0.8,
            "protein_bonus": 0.6,
            "fiber_bonus": 0.7,
            "fat_penalty": 0.1,
        },
    },
    "maintenance": {
        "display_name": "General PCOS Support",
        "macro_focus": ["balanced meals", "fiber", "protein"],
        "scoring_bias": {
            "carb_penalty": 0.4,
            "sugar_penalty": 0.7,
            "protein_bonus": 0.5,
            "fiber_bonus": 0.7,
            "fat_penalty": 0.1,
        },
    },
}

GOAL_ALIASES = {
    "fat_loss": "weight_loss",
    "lose_weight": "weight_loss",
    "weight loss": "weight_loss",
    "energy": "energy",
    "more_energy": "energy",
    "fertility": "fertility",
    "fertility_support": "fertility",
    "general_health": "maintenance",
    "maintenance": "maintenance",
}

HARMFUL_FOODS = {
    "french fries",
    "chips",
    "cola",
    "processed meat",
    "white bread",
    "cake",
    "cookies",
}

PROTEIN_FORWARD_FOODS = {
    "eggs",
    "egg",
    "greek yogurt",
    "tofu",
    "tempeh",
    "chicken",
    "salmon",
    "tuna",
    "turkey",
    "lentils",
    "beans",
    "chickpeas",
    "cottage cheese",
}

FIBER_FORWARD_FOODS = {
    "spinach",
    "broccoli",
    "kale",
    "chia seeds",
    "flaxseed",
    "oats",
    "lentils",
    "beans",
    "chickpeas",
    "berries",
    "avocado",
}


def compute_pcos_risk(nutrition_data: dict, personal_details: dict | None = None) -> dict:
    """
    nutrition_data format:
    {
        "food_name": {
            "carbs": float,
            "sugar": float,
            "fiber": float,
            "protein": float,
            "fat": float,
            "gi": float
        }
    }

    personal_details format:
    {
        "height_cm": float,
        "weight_kg": float,
        "target_goal": "weight_loss" | "energy" | "fertility" | "maintenance"
    }
    """

    user_context = build_user_context(personal_details or {})
    goal_bias = user_context["goal_profile"]["scoring_bias"]
    ingredient_scores = []

    for name, data in nutrition_data.items():
        gi = safe_float(data.get("gi"), 55)
        sugar = safe_float(data.get("sugar"), 0)
        fiber = safe_float(data.get("fiber"), 0)
        carbs = safe_float(data.get("carbs"), 0)
        protein = safe_float(data.get("protein"), 0)
        fat = safe_float(data.get("fat"), 0)

        gi_s = gi_score(gi)
        sugar_s = sugar_score(sugar)
        carb_s = carb_load_score(carbs)
        protein_s = protein_score(protein)
        fiber_s = fiber_score(fiber)
        fat_s = fat_score(fat)
        proc_s = processing_score(name)

        base_score = (
            0.28 * gi_s +
            0.22 * sugar_s +
            0.20 * proc_s +
            0.18 * carb_s +
            0.12 * fat_s
        )
        protective_adjustment = (
            -0.18 * goal_bias["protein_bonus"] * protein_s
            -0.18 * goal_bias["fiber_bonus"] * fiber_s
        )
        goal_adjustment = (
            0.15 * goal_bias["carb_penalty"] * max(carb_s - 4, 0)
            + 0.12 * goal_bias["sugar_penalty"] * max(sugar_s - 4, 0)
            + 0.08 * goal_bias["fat_penalty"] * fat_s
        )

        final_score = base_score + goal_adjustment + protective_adjustment
        final_score = clamp(final_score, 0, 10)

        flags = generate_flags(
            gi_s=gi_s,
            sugar_s=sugar_s,
            proc_s=proc_s,
            carb_s=carb_s,
            protein_s=protein_s,
            fiber_s=fiber_s,
        )

        recommendation = classify_ingredient(
            final_score=final_score,
            protein_s=protein_s,
            fiber_s=fiber_s,
            proc_s=proc_s,
            gi_s=gi_s,
            sugar_s=sugar_s,
        )

        ingredient_scores.append({
            "name": name,
            "gi_score": gi_s,
            "sugar_score": sugar_s,
            "processing_score": proc_s,
            "carb_load_score": carb_s,
            "protein_score": protein_s,
            "fiber_score": fiber_s,
            "fat_score": fat_s,
            "final_score": round(final_score, 2),
            "recommendation": recommendation,
            "flags": flags,
            "carbs": carbs,
            "protein": protein,
            "fiber": fiber,
            "fat": fat,
            "goal_alignment": score_goal_alignment(
                protein_s=protein_s,
                fiber_s=fiber_s,
                sugar_s=sugar_s,
                carb_s=carb_s,
                proc_s=proc_s,
                goal=user_context["target_goal"],
            ),
        })

    total_score = weighted_score(ingredient_scores)
    risk_level = classify_risk(total_score)
    summary_flags = aggregate_flags(ingredient_scores)

    return {
        "ingredient_scores": ingredient_scores,
        "total_score": round(total_score, 2),
        "risk_level": risk_level,
        "summary_flags": summary_flags,
        "user_context": user_context,
        "recommendation_summary": build_recommendation_summary(
            ingredient_scores,
            summary_flags,
            user_context,
        ),
    }


def build_user_context(personal_details: dict) -> dict:
    height_cm = safe_float(personal_details.get("height_cm"), 0)
    weight_kg = safe_float(personal_details.get("weight_kg"), 0)
    target_goal = normalize_goal(personal_details.get("target_goal"))
    bmi = calculate_bmi(weight_kg, height_cm)
    validation_notes = validate_personal_details(height_cm, weight_kg)

    return {
        "height_cm": height_cm or None,
        "weight_kg": weight_kg or None,
        "target_goal": target_goal,
        "goal_profile": GOAL_PROFILES[target_goal],
        "bmi": bmi,
        "bmi_category": classify_bmi(bmi),
        "validation_notes": validation_notes,
    }


def normalize_goal(goal: str | None) -> str:
    if not goal:
        return "maintenance"

    normalized = str(goal).strip().lower().replace("-", "_")
    return GOAL_ALIASES.get(normalized, "maintenance")


def calculate_bmi(weight_kg: float, height_cm: float) -> float | None:
    if weight_kg <= 0 or height_cm <= 0:
        return None

    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 1)


def classify_bmi(bmi: float | None) -> str | None:
    if bmi is None:
        return None
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "healthy"
    if bmi < 30:
        return "overweight"
    return "obesity"


def validate_personal_details(height_cm: float, weight_kg: float) -> list[str]:
    notes = []

    if height_cm and not 120 <= height_cm <= 230:
        notes.append("height_outside_typical_adult_range")

    if weight_kg and not 30 <= weight_kg <= 300:
        notes.append("weight_outside_typical_adult_range")

    return notes


def gi_score(gi: float) -> int:
    if gi >= 70:
        return 9
    if gi >= 55:
        return 6
    return 2


def sugar_score(sugar: float) -> int:
    if sugar >= 15:
        return 9
    if sugar >= 8:
        return 6
    if sugar >= 3:
        return 4
    return 1


def carb_load_score(carbs: float) -> int:
    if carbs >= 30:
        return 8
    if carbs >= 20:
        return 6
    if carbs >= 10:
        return 4
    return 2


def protein_score(protein: float) -> int:
    if protein >= 15:
        return 4
    if protein >= 8:
        return 3
    if protein >= 4:
        return 2
    return 0


def fiber_score(fiber: float) -> int:
    if fiber >= 8:
        return 4
    if fiber >= 5:
        return 3
    if fiber >= 2:
        return 2
    return 0


def fat_score(fat: float) -> int:
    if fat >= 20:
        return 4
    if fat >= 12:
        return 2
    return 0


def processing_score(name: str) -> int:
    normalized = normalize_food_name(name)
    if normalized in HARMFUL_FOODS:
        return 9
    if normalized in PROTEIN_FORWARD_FOODS or normalized in FIBER_FORWARD_FOODS:
        return 2
    return 4


def generate_flags(
    gi_s: int,
    sugar_s: int,
    proc_s: int,
    carb_s: int,
    protein_s: int,
    fiber_s: int,
) -> list[str]:
    flags = []

    if gi_s >= 7:
        flags.append("high_gi")
    if sugar_s >= 7:
        flags.append("high_sugar")
    if proc_s >= 7:
        flags.append("ultra_processed")
    if carb_s >= 7:
        flags.append("high_carb_load")
    if protein_s >= 3:
        flags.append("protein_supportive")
    if fiber_s >= 3:
        flags.append("fiber_supportive")

    return flags


def classify_ingredient(
    final_score: float,
    protein_s: int,
    fiber_s: int,
    proc_s: int = 0,
    gi_s: int = 0,
    sugar_s: int = 0,
) -> str:
    if proc_s >= 8 or gi_s >= 8 or sugar_s >= 8 or final_score >= 6:
        return "limit_or_avoid"
    if final_score <= 3.5 or (final_score <= 4.5 and (protein_s >= 3 or fiber_s >= 3)):
        return "prioritize"
    if final_score <= 6.5:
        return "use_in_moderation"
    return "limit_or_avoid"


def score_goal_alignment(
    protein_s: int,
    fiber_s: int,
    sugar_s: int,
    carb_s: int,
    proc_s: int,
    goal: str,
) -> str:
    if goal == "weight_loss":
        if proc_s >= 8 or sugar_s >= 6 or carb_s >= 8:
            return "less_aligned_for_weight_loss"
        if protein_s >= 3 or fiber_s >= 3:
            return "supports_satiety"
    elif goal == "energy":
        if sugar_s >= 6:
            return "may_cause_energy_swings"
        if sugar_s <= 4 and (protein_s >= 2 or fiber_s >= 2):
            return "supports_steady_energy"
    elif goal == "fertility":
        if proc_s >= 8 or sugar_s >= 6:
            return "less_aligned_for_fertility_support"
        if sugar_s <= 4 and fiber_s >= 2:
            return "supports_metabolic_balance"

    return "general_support"


def weighted_score(ingredient_scores: list[dict]) -> float:
    total_weight = sum(food_weight_for_scoring(item) for item in ingredient_scores)
    if total_weight == 0:
        return 0

    weighted_sum = sum(
        item["final_score"] * food_weight_for_scoring(item)
        for item in ingredient_scores
    )
    return weighted_sum / total_weight


def food_weight_for_scoring(item: dict) -> float:
    carbs = safe_float(item.get("carbs"), 0)
    protein = safe_float(item.get("protein"), 0)
    fat = safe_float(item.get("fat"), 0)
    return max(carbs + protein + (fat * 0.5), 1)


def classify_risk(score: float) -> str:
    if score >= 7:
        return "high"
    if score >= 4.5:
        return "moderate"
    return "low"


def aggregate_flags(ingredient_scores: list[dict]) -> list[str]:
    all_flags = set()
    for item in ingredient_scores:
        for flag in item.get("flags", []):
            all_flags.add(flag)
    return sorted(all_flags)


def build_recommendation_summary(
    ingredient_scores: list[dict],
    summary_flags: list[str],
    user_context: dict,
) -> dict:
    prioritized = [i["name"] for i in ingredient_scores if i["recommendation"] == "prioritize"]
    moderate = [i["name"] for i in ingredient_scores if i["recommendation"] == "use_in_moderation"]
    avoid = [i["name"] for i in ingredient_scores if i["recommendation"] == "limit_or_avoid"]

    return {
        "goal": user_context["goal_profile"]["display_name"],
        "macro_focus": user_context["goal_profile"]["macro_focus"],
        "prioritize": prioritized,
        "moderate": moderate,
        "avoid": avoid,
        "main_flags": summary_flags,
    }


def normalize_food_name(name: str) -> str:
    return str(name).lower().strip()


def safe_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


if __name__ == "__main__":
    sample_input = {
        "french fries": {
            "carbs": 35,
            "sugar": 0.5,
            "fiber": 3,
            "protein": 4,
            "fat": 15,
            "gi": 75,
        },
        "spinach": {
            "carbs": 4,
            "sugar": 0.4,
            "fiber": 3,
            "protein": 3,
            "fat": 0.3,
            "gi": 15,
        },
        "eggs": {
            "carbs": 1,
            "sugar": 0.2,
            "fiber": 0,
            "protein": 13,
            "fat": 10,
            "gi": 0,
        },
    }

    profile = {
        "height_cm": 165,
        "weight_kg": 74,
        "target_goal": "weight_loss",
    }

    result = compute_pcos_risk(sample_input, profile)

    import json
    print(json.dumps(result, indent=2))
