import axios from "axios";

const api = axios.create({
  //baseURL: "http://127.0.0.1:5000"
  baseURL: process.env.REACT_APP_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 只針對 JWT 過期自動登出，帳密錯誤不會 alert
api.interceptors.response.use(
  response => response,
  error => {
    if (
      error.response &&
      error.response.status === 401 &&
      (
        (error.response.data?.error?.toString().toLowerCase().includes("token")) ||
        (error.response.data?.message?.toString().toLowerCase().includes("token"))
      )
    ) {
      localStorage.clear();
      alert("登入逾時，請重新登入");
      window.location.href = "/login";
      return Promise.reject(new Error("登入逾時，請重新登入"));
    }
    return Promise.reject(error);
  }
);

export default api;
