import json
import re


def extract_json_object(raw_text: str) -> dict:
    """
    Extract the first valid JSON object from an AI response.
    Handles cases where the model adds prose or code fences.
    """

    if not raw_text or not raw_text.strip():
        raise ValueError("AI output is empty.")

    cleaned = raw_text.strip()

    # Remove common markdown code fences without assuming perfect formatting.
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in AI output.")

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON returned by AI: {exc}") from exc


def normalize_meal_payload(ai_payload: dict) -> dict:
    """
    Validate and normalize the meal JSON into a consistent backend shape.
    """

    meal_name = str(ai_payload.get("meal_name", "")).strip()
    why_good = str(ai_payload.get("why_good_for_pcos", "")).strip()
    ingredients = ai_payload.get("ingredients", [])
    recipe_steps = ai_payload.get("recipe", [])

    if not meal_name:
        raise ValueError("Missing required field: meal_name")

    if not why_good:
        raise ValueError("Missing required field: why_good_for_pcos")

    if not isinstance(ingredients, list) or not ingredients:
        raise ValueError("Field 'ingredients' must be a non-empty list.")

    if not isinstance(recipe_steps, list) or not recipe_steps:
        raise ValueError("Field 'recipe' must be a non-empty list.")

    normalized_ingredients = [
        str(item).strip()
        for item in ingredients
        if str(item).strip()
    ]

    normalized_steps = [
        str(step).strip()
        for step in recipe_steps
        if str(step).strip()
    ]

    if not normalized_ingredients:
        raise ValueError("No usable ingredients found in AI output.")

    if not normalized_steps:
        raise ValueError("No usable recipe steps found in AI output.")

    return {
        "meal_name": meal_name,
        "ingredients": normalized_ingredients,
        "recipe": normalized_steps,
        "why_good_for_pcos": why_good,
    }


def format_meal_for_website(normalized_meal: dict) -> dict:
    """
    Convert normalized meal data into a website-deliverable response.
    """

    ingredients = normalized_meal["ingredients"]
    recipe_steps = normalized_meal["recipe"]

    return {
        "success": True,
        "data": {
            "title": normalized_meal["meal_name"],
            "description": normalized_meal["why_good_for_pcos"],
            "ingredients": [
                {
                    "id": index + 1,
                    "label": ingredient
                }
                for index, ingredient in enumerate(ingredients)
            ],
            "recipe_steps": [
                {
                    "step": index + 1,
                    "instruction": instruction
                }
                for index, instruction in enumerate(recipe_steps)
            ],
            "meta": {
                "ingredient_count": len(ingredients),
                "step_count": len(recipe_steps),
                "diet_focus": "PCOS-friendly"
            }
        },
        "error": None
    }


def parse_ai_meal_output(raw_text: str) -> dict:
    """
    Full pipeline:
    raw AI output -> extracted JSON -> normalized meal -> website payload
    """

    ai_payload = extract_json_object(raw_text)
    normalized_meal = normalize_meal_payload(ai_payload)
    return format_meal_for_website(normalized_meal)


def build_error_response(message: str) -> dict:
    return {
        "success": False,
        "data": None,
        "error": message
    }
