import difflib
import json
from pathlib import Path
import re


_DATA_DIR = Path(__file__).resolve().parent / "data"
_SYNONYMS_PATH = _DATA_DIR / "synonyms.json"

with _SYNONYMS_PATH.open("r", encoding="utf-8") as f:
    SYNONYM_MAP = json.load(f)



STANDARD_INGREDIENTS = list(set(SYNONYM_MAP.values())) + [
    "chicken", "egg", "apple", "banana", "broccoli", "cucumber"
]

def clean_string(item: str) -> str:
    """Removes special characters, extra spaces, and converts to lowercase."""
    item = item.lower().strip()
    item = re.sub(r'[^a-z\s]', '', item) # Remove anything that isn't a letter or space
    return item

def normalize_ingredient(raw_ingredient: str) -> str:
    """Normalizes a single ingredient string."""
    cleaned = clean_string(raw_ingredient)
    
    # Check 1: Direct translation from Hinglish to English
    if cleaned in SYNONYM_MAP:
        return SYNONYM_MAP[cleaned]
    
    # Check 2: Is it already a standard English word or close to one? (Fuzzy matching)
    # cutoff=0.8 means it needs to be an 80% match (handles typos like "tometo" -> "tomato")
    closest_matches = difflib.get_close_matches(cleaned, STANDARD_INGREDIENTS, n=1, cutoff=0.8)
    
    if closest_matches:
        return closest_matches[0]
    
    # Check 3: If we don't know it, return the cleaned version. 
    # Let the Spoonacular/Edamam API try to figure it out.
    return cleaned

if __name__ == "__main__":
    test_ingredients = [
        "tometo", "aloo", "cucmber", "chiken", "pyazz", "apple", "banana", "cheeni"
    ]
    
    for ing in test_ingredients:
        normalized = normalize_ingredient(ing)
        print(f"Raw: '{ing}' -> Normalized: '{normalized}'")