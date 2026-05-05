import { useState } from "react";
import { normalizeIngredients, suggestMeals } from "../services/api";

const DEFAULT_PROFILE = {
  fullName: "",
  age: "",
  weightKg: "",
  heightCm: "",
  activity: "sedentary",
  targetGoal: "weight_loss",
};

function toNumberOrUndefined(value) {
  if (value === "" || value === null || value === undefined) {
    return undefined;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function buildAnalyzePayload(input, profile) {
  return {
    ingredients: input,
    personal_details: {
      full_name: profile.fullName || undefined,
      age: toNumberOrUndefined(profile.age),
      weight_kg: toNumberOrUndefined(profile.weightKg),
      height_cm: toNumberOrUndefined(profile.heightCm),
      activity_level: profile.activity || undefined,
      target_goal: profile.targetGoal || "maintenance",
    },
  };
}

function buildNormalizePayload(input) {
  return {
    ingredients: input,
    meal_type: "meal",
  };
}

export function usePCOS() {
  const [input, setInput] = useState("");
  const [profile, setProfile] = useState(DEFAULT_PROFILE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  const setProfileField = (field, value) => {
    setProfile((current) => ({
      ...current,
      [field]: value,
    }));
    setProfileSaved(false);
  };

  const saveProfile = () => {
    setProfileSaved(true);
  };

  const fetchMeals = async () => {
    const trimmedInput = input.trim();

    if (!trimmedInput) {
      setError("Add at least one ingredient to generate a recommendation.");
      setResult(null);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const normalized = await normalizeIngredients(
        buildNormalizePayload(trimmedInput)
      );

      if (normalized?.success === false) {
        throw new Error(normalized.error || "Unable to normalize ingredients.");
      }

      const normalizedIngredients =
        normalized?.data?.normalized_ingredients || [];

      const data = await suggestMeals({
        ...buildAnalyzePayload(trimmedInput, profile),
        ingredients: normalizedIngredients,
      });

      if (data?.success === false) {
        throw new Error(data.error || "Unable to generate meal suggestions.");
      }

      setResult(data?.data || data?.meal || data);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.error ||
          err?.message ||
          "Error fetching results"
      );
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return {
    input,
    setInput,
    profile,
    setProfileField,
    saveProfile,
    profileSaved,
    result,
    error,
    loading,
    fetchMeals,
  };
}
