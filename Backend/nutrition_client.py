import difflib
import os

try:
    import requests
except ImportError:
    requests = None


REQUEST_TIMEOUT_SECONDS = float(os.getenv("NUTRITION_HTTP_TIMEOUT", "4"))
OPENFOODFACTS_PAGE_SIZE = int(os.getenv("OPENFOODFACTS_PAGE_SIZE", "5"))
MIN_MATCH_CONFIDENCE = float(os.getenv("NUTRITION_MIN_MATCH_CONFIDENCE", "0.55"))


# Simple in-memory cache
CACHE = {}


# Fallback nutrition data (per 100g)
FALLBACK_DB = {
    "french fries": {"carbs": 35, "sugar": 0.5, "fiber": 3, "protein": 4, "fat": 15, "gi": 75},
    "burger": {"carbs": 30, "sugar": 5, "fiber": 2, "protein": 17, "fat": 12, "gi": 66},
    "white rice": {"carbs": 28, "sugar": 0.1, "fiber": 0.4, "protein": 2.7, "fat": 0.3, "gi": 73},
    "brown rice": {"carbs": 23, "sugar": 0.4, "fiber": 1.8, "protein": 2.6, "fat": 0.9, "gi": 50},
    "cola": {"carbs": 11, "sugar": 11, "fiber": 0, "protein": 0, "fat": 0, "gi": 63},
    "eggs": {"carbs": 1.1, "sugar": 0.4, "fiber": 0, "protein": 13, "fat": 10, "gi": 0},
    "spinach": {"carbs": 3.6, "sugar": 0.4, "fiber": 2.2, "protein": 2.9, "fat": 0.4, "gi": 15},
    "oats": {"carbs": 66, "sugar": 1, "fiber": 10.6, "protein": 16.9, "fat": 6.9, "gi": 55},
    "greek yogurt": {"carbs": 3.9, "sugar": 3.2, "fiber": 0, "protein": 10, "fat": 5, "gi": 11},
}


GI_HINTS = {
    "berries": 25,
    "broccoli": 15,
    "brown rice": 50,
    "chickpeas": 28,
    "chips": 70,
    "cookies": 77,
    "egg": 0,
    "eggs": 0,
    "french fries": 75,
    "greek yogurt": 11,
    "kale": 15,
    "lentils": 32,
    "oats": 55,
    "processed meat": 48,
    "salmon": 0,
    "spinach": 15,
    "tofu": 15,
    "white bread": 75,
    "white rice": 73,
}


def get_nutrition_for_ingredients(ingredients: list[str]) -> dict:
    results = {}

    for item in ingredients:
        normalized_name = normalize_name(item)

        if normalized_name in CACHE:
            results[normalized_name] = CACHE[normalized_name]
            continue

        data = (
            fetch_from_openfoodfacts(normalized_name)
            or fetch_from_usda(normalized_name)
            or fallback_nutrition(normalized_name)
        )

        CACHE[normalized_name] = data
        results[normalized_name] = data

    return results


def normalize_name(name: str) -> str:
    return " ".join(str(name).lower().strip().split())


def fetch_from_openfoodfacts(ingredient: str) -> dict | None:
    if requests is None:
        print("[NUTRITION ERROR][openfoodfacts]: requests dependency is not installed.")
        return None

    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": ingredient,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": OPENFOODFACTS_PAGE_SIZE,
        }

        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()

        products = data.get("products") or []
        best_product, confidence = select_best_product_match(ingredient, products)

        if not best_product or confidence < MIN_MATCH_CONFIDENCE:
            return None

        nutriments = best_product.get("nutriments", {})
        standardized = standardize_nutrition(nutriments)

        if not standardized:
            return None

        standardized["gi"] = infer_gi(ingredient)
        standardized["source"] = "openfoodfacts"
        standardized["confidence"] = round(confidence, 2)
        standardized["matched_name"] = best_product.get("product_name") or best_product.get("generic_name") or ingredient
        return standardized

    except Exception as exc:
        print(f"[NUTRITION ERROR][openfoodfacts]: {exc}")
        return None


def fetch_from_usda(ingredient: str) -> dict | None:
    """
    Stub for future USDA integration.
    """

    return None


def select_best_product_match(ingredient: str, products: list[dict]) -> tuple[dict | None, float]:
    best_product = None
    best_score = 0.0

    for product in products:
        candidate_name = normalize_name(
            product.get("product_name")
            or product.get("generic_name")
            or product.get("product_name_en")
            or ""
        )

        if not candidate_name:
            continue

        score = match_score(ingredient, candidate_name)
        if score > best_score:
            best_product = product
            best_score = score

    return best_product, best_score


def match_score(query: str, candidate: str) -> float:
    exact_bonus = 0.2 if query == candidate else 0.0
    contains_bonus = 0.1 if query in candidate or candidate in query else 0.0

    query_tokens = set(query.split())
    candidate_tokens = set(candidate.split())
    token_overlap = len(query_tokens & candidate_tokens) / max(len(query_tokens), 1)
    similarity = difflib.SequenceMatcher(None, query, candidate).ratio()

    return min(1.0, (0.55 * similarity) + (0.35 * token_overlap) + exact_bonus + contains_bonus)


def standardize_nutrition(nutriments: dict) -> dict | None:
    try:
        standardized = {
            "carbs": safe_float(nutriments.get("carbohydrates_100g"), None),
            "sugar": safe_float(nutriments.get("sugars_100g"), None),
            "fiber": safe_float(nutriments.get("fiber_100g"), None),
            "protein": safe_float(nutriments.get("proteins_100g"), None),
            "fat": safe_float(nutriments.get("fat_100g"), None),
        }

        if standardized["carbs"] is None:
            return None

        for key, value in standardized.items():
            if value is None:
                standardized[key] = 0.0

        return standardized
    except Exception as exc:
        print(f"[NUTRITION ERROR][standardize]: {exc}")
        return None


def fallback_nutrition(ingredient: str) -> dict:
    fallback = FALLBACK_DB.get(ingredient)

    if fallback:
        return {
            **fallback,
            "source": "fallback_db",
            "confidence": 0.7,
            "matched_name": ingredient,
        }

    return {
        "carbs": 20.0,
        "sugar": 2.0,
        "fiber": 1.0,
        "protein": 2.0,
        "fat": 5.0,
        "gi": infer_gi(ingredient, default=55),
        "source": "fallback_estimate",
        "confidence": 0.25,
        "matched_name": ingredient,
    }


def infer_gi(ingredient: str, default: float = 55) -> float:
    normalized = normalize_name(ingredient)

    if normalized in GI_HINTS:
        return float(GI_HINTS[normalized])

    for key, gi_value in GI_HINTS.items():
        if key in normalized:
            return float(gi_value)

    return float(default)


def safe_float(value, default: float | None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
