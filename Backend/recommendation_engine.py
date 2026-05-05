from ai_client import generate_website_meal_response
from meal_builder import build_meal
from prompt_builder import build_meal_prompt
from rules_engine import compute_pcos_risk


def build_personalized_meal_recommendation(
    nutrition_data: dict,
    personal_details: dict | None = None,
) -> dict:
    """
    End-to-end pipeline for website use.

    Input:
    - nutrition_data: normalized ingredient nutrition objects
    - personal_details: height, weight, target goal, etc.

    Output:
    - website-deliverable response with supporting recommendation metadata
    """

    rule_output = compute_pcos_risk(nutrition_data, personal_details or {})
    meal_brief = build_meal(rule_output)
    prompt = build_meal_prompt(meal_brief)
    website_response = generate_website_meal_response(prompt)

    if website_response.get("success"):
        website_response["data"]["recommendation_context"] = {
            "goal": rule_output["recommendation_summary"]["goal"],
            "macro_focus": rule_output["recommendation_summary"]["macro_focus"],
            "risk_level": rule_output["risk_level"],
            "prioritize": rule_output["recommendation_summary"]["prioritize"],
            "moderate": rule_output["recommendation_summary"]["moderate"],
            "avoid": rule_output["recommendation_summary"]["avoid"],
            "user_profile": {
                "target_goal": rule_output["user_context"]["target_goal"],
                "bmi": rule_output["user_context"]["bmi"],
                "bmi_category": rule_output["user_context"]["bmi_category"],
                "validation_notes": rule_output["user_context"]["validation_notes"],
            },
        }

    return website_response
