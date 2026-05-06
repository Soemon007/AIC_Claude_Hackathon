# AIC_Claude_Hackathon

# PCOS Smart Meal Recommender

A personalized meal recommendation web app designed specifically for women with **PCOS (Polycystic Ovary Syndrome)**. This tool helps users make smarter dietary choices based on the ingredients they already have, while optimizing for hormonal balance, low glycemic impact, and nutritional quality.

---

## Overview

Managing PCOS through diet can be overwhelming. This project simplifies that process by:

* Taking **user-input ingredients**
* Applying a **nutrition rules engine**
* Generating **PCOS-friendly meal suggestions**
* Ensuring meals are aligned with **low GI, anti-inflammatory, and balanced nutrition principles**

---

## Core Features (Brief Technical Breakdown)

### 1. Ingredient-Driven Meal Generation Engine

* Accepts a dynamic list of user-provided ingredients as input
* Normalizes and preprocesses ingredient data (tokenization, standardization, duplicate removal)
* Matches inputs against a structured ingredient database
* Generates candidate meal combinations using rule-based and AI-assisted approaches
* Supports partial ingredient matching and substitution logic

---

### 2. PCOS-Specific Nutrition Rules Engine (`nutrition.py`)

* Integrated with nutrion API (with fallback to USDA Food Database)
* Fetches key nutrition labels of given ingredients
* Implements deterministic filtering using a rule-based system
* Each ingredient is evaluated across multiple dimensions:

  * Glycemic Index (GI)
  * Glycemic Load (GL) (optional extension)
  * Macronutrient composition (protein, fat, carbs)
  * Inflammatory score (heuristic-based)
* Uses weighted scoring or threshold-based exclusion:

  * Hard constraints (e.g., exclude very high GI foods)
  * Soft constraints (e.g., penalize low-fiber meals)
* Outputs a ranked list of ingredient combinations optimized for PCOS dietary guidelines

---

### 3. Glycemic Index (GI) Evaluation Module

* Maintains a lookup table or dataset mapping ingredients → GI values
* Computes aggregate meal GI using weighted averaging:

  * Based on carbohydrate contribution of each ingredient
* Categorizes meals into:

  * Low GI (preferred)
  * Medium GI (acceptable)
  * High GI (restricted)
* Integrates directly into scoring pipeline for meal ranking

---

### 4. AI-Augmented Meal Synthesis (`ai_client.py`)

* Uses an LLM to:

  * Generate coherent meal recipes from filtered ingredient sets
  * Suggest missing but compatible ingredients
  * Improve palatability and diversity of meals
* Prompt engineering ensures:

  * Adherence to constraints from rules engine
  * Structured output (e.g., meal name, ingredients, reasoning)
* Acts only after rule-based filtering (guardrail architecture)

---

### 5. Scoring & Ranking System

* Combines multiple metrics into a unified score:

  * GI score
  * Macronutrient balance score
  * Ingredient compatibility score
  * Rule compliance score
* Supports configurable weights for personalization
* Returns top-N ranked meal options

---

## ⚙️How It Works

1. User enters available ingredients along with a personalized profile
2. Frontend sends data to backend
3. `nutrition.py` filters ingredients based on PCOS rules
4. `ai.py` generates optimal meal combinations
5. Results are displayed to the user

---

## Example Flow

**Input:**

```
Eggs, Spinach, Rice
```

**Output:**

```
Suggested Meal: Spinach Omelette with Controlled Rice Portion
Reason: High protein, fiber-rich, moderate GI balance
```

---

## 🛠️ Tech Stack

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python, FastTrackAPI, USDA Food Data
* **AI Layer:** Gemini API (2.5 Flash Lite)

---

## Safety & Accuracy Considerations

* Ingredient validation to avoid harmful combinations
* GI score checks to maintain blood sugar stability
* Rule-based filtering before AI suggestions
* Option to flag uncertain recommendations

---

## Future Improvements

* Other personalized user profiles (insulin resistance level, food habits, allergies)
* Meal history and tracking
* Suggestions based on amount of ingredients (some ingredients may be utilized in limited amounts)

---

## Authors

Made by:

@avg03
@Soemon007

---

## Disclaimer

This project is intended for **educational and informational purposes only** and should not replace professional medical advice. Always consult a healthcare provider for dietary decisions related to PCOS.

---
