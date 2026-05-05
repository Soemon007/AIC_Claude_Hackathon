import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const analyzeIngredients = async (payload) => {
  const res = await axios.post(`${API_BASE_URL}/analyze`, payload);
  return res.data;
};
