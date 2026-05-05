"""
Meal Builder
------------
Transforms scored ingredients into a structured, personalized meal brief.
"""


def build_meal(rule_engine_output: dict) -> dict:
    """
    Input: output from compute_pcos_risk()

    Output:
    {
        "meal_ingredients": [...],
        "avoid": [...],
        "reasoning": {...}
    }
    """

    ingredient_scores = rule_engine_output.get("ingredient_scores", [])
    user_context = rule_engine_output.get("user_context", {})
    recommendation_summary = rule_engine_output.get("recommendation_summary", {})

    prioritized, moderate, avoid = categorize_ingredients(ingredient_scores)
    selected = select_balanced_ingredients(prioritized, moderate)

    selected_names = list({item["name"]: item for item in selected}.values())

    reasoning = {
        "goal": recommendation_summary.get("goal"),
        "macro_focus": recommendation_summary.get("macro_focus", []),
        "risk_level": rule_engine_output.get("risk_level"),
        "summary_flags": rule_engine_output.get("summary_flags", []),
        "user_context": {
            "target_goal": user_context.get("target_goal"),
            "bmi": user_context.get("bmi"),
            "bmi_category": user_context.get("bmi_category"),
            "validation_notes": user_context.get("validation_notes", []),
        },
        "selected_traits": summarize_selected_traits(selected_names),
        "used_good": [i["name"] for i in prioritized],
        "limited_moderate": [i["name"] for i in moderate],
        "avoided": [i["name"] for i in avoid],
    }

    return {
        "meal_ingredients": [i["name"] for i in selected_names],
        "avoid": [i["name"] for i in avoid],
        "reasoning": reasoning,
    }


def categorize_ingredients(ingredient_scores: list[dict]):
    prioritized = []
    moderate = []
    avoid = []

    for item in ingredient_scores:
        recommendation = item.get("recommendation")

        if recommendation == "prioritize":
            prioritized.append(item)
        elif recommendation == "use_in_moderation":
            moderate.append(item)
        else:
            avoid.append(item)

    prioritized.sort(
        key=lambda x: (
            x.get("final_score", 10),
            -x.get("protein_score", 0),
            -x.get("fiber_score", 0),
        )
    )
    moderate.sort(key=lambda x: x.get("final_score", 10))
    avoid.sort(key=lambda x: x.get("final_score", 0), reverse=True)

    return prioritized, moderate, avoid


def select_balanced_ingredients(prioritized: list[dict], moderate: list[dict]) -> list[dict]:
    selected = []

    protein_lead = next((item for item in prioritized if item.get("protein_score", 0) >= 3), None)
    fiber_lead = next((item for item in prioritized if item.get("fiber_score", 0) >= 3), None)

    if protein_lead:
        selected.append(protein_lead)
    if fiber_lead and fiber_lead["name"] not in [item["name"] for item in selected]:
        selected.append(fiber_lead)

    for item in prioritized:
        if item["name"] not in [chosen["name"] for chosen in selected]:
            selected.append(item)
        if len(selected) >= 4:
            break

    if len(selected) < 3:
        for item in moderate:
            if item["name"] not in [chosen["name"] for chosen in selected]:
                selected.append(item)
            if len(selected) >= 4:
                break

    return selected[:4]


def summarize_selected_traits(selected_items: list[dict]) -> list[str]:
    traits = set()

    for item in selected_items:
        if item.get("protein_score", 0) >= 3:
            traits.add("protein-forward")
        if item.get("fiber_score", 0) >= 3:
            traits.add("fiber-rich")
        if item.get("sugar_score", 0) <= 4:
            traits.add("lower-sugar")
        if item.get("processing_score", 0) <= 4:
            traits.add("minimally-processed leaning")

    return sorted(traits)


if __name__ == "__main__":
    sample_rule_output = {
        "ingredient_scores": [
            {
                "name": "eggs",
                "final_score": 2.2,
                "recommendation": "prioritize",
                "protein_score": 3,
                "fiber_score": 0,
                "sugar_score": 1,
                "processing_score": 2,
            },
            {
                "name": "spinach",
                "final_score": 1.8,
                "recommendation": "prioritize",
                "protein_score": 0,
                "fiber_score": 3,
                "sugar_score": 1,
                "processing_score": 2,
            },
            {
                "name": "cheese",
                "final_score": 5.1,
                "recommendation": "use_in_moderation",
                "protein_score": 2,
                "fiber_score": 0,
                "sugar_score": 1,
                "processing_score": 4,
            },
        ],
        "risk_level": "low",
        "summary_flags": ["protein_supportive", "fiber_supportive"],
        "user_context": {
            "target_goal": "weight_loss",
            "bmi": 27.1,
            "bmi_category": "overweight",
        },
        "recommendation_summary": {
            "goal": "Weight Loss",
            "macro_focus": ["protein", "fiber", "glycemic control"],
        },
    }

    import json
    print(json.dumps(build_meal(sample_rule_output), indent=2))
