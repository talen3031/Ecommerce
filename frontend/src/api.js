import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  //baseURL : "http://127.0.0.1:5000"
});
//console.log("API URL: ", process.env.REACT_APP_API_URL);
// 自動帶 JWT Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;   