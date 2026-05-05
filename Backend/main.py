from fastapi import FastAPI
app = FastAPI()
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent / "Backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from nutrition_client import get_nutrition_for_ingredients
from recommendation_engine import build_personalized_meal_recommendation
from normalizer import normalize_ingredients
from rule_engine import filter_ingredients


def parse_ingredients(raw_ingredients) -> list[str]:
    if isinstance(raw_ingredients, list):
        return [str(item).strip() for item in raw_ingredients if str(item).strip()]

    if isinstance(raw_ingredients, str):
        normalized = raw_ingredients
        for separator in [",", "\n"]:
            normalized = normalized.replace(separator, "|")
        return [item.strip() for item in normalized.split("|") if item.strip()]

    return []


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/suggest")
def run_backend_logic(payload: dict) -> dict:
    """
    Main orchestration function for the FastAPI endpoint.

    Expected payload:
    {
        "ingredients": "eggs, spinach" | ["eggs", "spinach"],
        "personal_details": {...}
    }
    """

    ingredients = parse_ingredients(payload.get("ingredients", []))
    personal_details = payload.get("personal_details") or {}

    if not ingredients:
        return {
            "success": False,
            "data": None,
            "error": "At least one ingredient is required.",
        }

    nutrition_data = get_nutrition_for_ingredients(ingredients)
    return build_personalized_meal_recommendation(nutrition_data, personal_details)


@app.post("/normalize")
def normalize_ingredients_endpoint(payload: dict) -> dict:
    """
    Normalizes ingredient input and applies PCOS filtering rules.

    Expected payload:
    {
        "ingredients": "eggs, spinach" | ["eggs", "spinach"],
        "meal_type": "breakfast" | "lunch" | "dinner"
    }
    """

    ingredients = parse_ingredients(payload.get("ingredients", []))
    meal_type = str(payload.get("meal_type", "meal")).strip() or "meal"

    if not ingredients:
        return {
            "success": False,
            "data": None,
            "error": "At least one ingredient is required.",
        }

    normalized = normalize_ingredients(ingredients)
    filtered = filter_ingredients(normalized, meal_type)

    return {
        "success": True,
        "data": {
            "raw_ingredients": ingredients,
            "normalized_ingredients": normalized,
            "filtered": filtered,
            "meal_type": meal_type,
        },
        "error": None,
    }