import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const normalizeIngredients = async (payload) => {
  const res = await axios.post(`${API_BASE_URL}/normalize`, payload);
  return res.data;
};

export const suggestMeals = async (payload) => {
  const res = await axios.post(`${API_BASE_URL}/suggest`, payload);
  return res.data;
};
