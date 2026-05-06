def build_meal_prompt(meal: dict) -> str:
    allowed_ingredients = meal.get("meal_ingredients", [])
    avoid_ingredients = meal.get("avoid", [])
    reasoning = meal.get("reasoning", {})
    goal = reasoning.get("goal", "General PCOS Support")
    macro_focus = reasoning.get("macro_focus", [])
    user_context = reasoning.get("user_context", {})

    return f"""
You are a clinical-style nutrition assistant specializing in practical, evidence-aligned PCOS-friendly meal design.

Your task is to create one professional-quality meal recommendation using only the provided approved ingredients as the core of the dish.

APPROVED INGREDIENTS:
{allowed_ingredients}

INGREDIENTS TO AVOID:
{avoid_ingredients}

MEAL SELECTION CONTEXT:
{reasoning}

PERSONALIZATION CONTEXT:
- Primary goal: {goal}
- Macro focus: {macro_focus}
- User profile summary: {user_context}

Requirements:
1. Create exactly one realistic, appetizing, home-cook-friendly meal.
2. Prioritize PCOS-supportive principles such as higher protein, higher fiber, balanced blood-sugar response, and lower reliance on refined carbohydrates.
3. Tailor the meal toward the user's primary goal while staying PCOS-conscious.
4. Use the approved ingredients as the foundation of the meal.
5. Reflect the macro focus in the meal composition and in the explanation.
6. Do not include any ingredient from the avoid list.
7. You may add a small number of common pantry items only when necessary for a coherent recipe, such as olive oil, salt, pepper, garlic, lemon, or basic spices.
8. Keep the recipe simple, practical, and concise.
9. The meal name should sound polished and cookbook-quality, not generic.
10. The explanation of why the meal is good for PCOS should be specific, professional, and medically cautious. Do not claim to treat, cure, or diagnose anything.
11. When relevant, mention how the meal supports the user's goal, such as satiety for weight loss, steadier energy, or metabolic balance for fertility support.

Return output as ONLY valid JSON with this exact structure:
{{
  "meal_name": "string",
  "ingredients": ["string", "string"],
  "recipe": ["step 1", "step 2", "step 3"],
  "why_good_for_pcos": "string"
}}

Output rules:
- No markdown.
- No code fences.
- No commentary before or after the JSON.
- "ingredients" must be an array of concise ingredient strings.
- "recipe" must contain 3 to 5 clear step strings.
- Ensure the JSON is syntactically valid.
""".strip()
