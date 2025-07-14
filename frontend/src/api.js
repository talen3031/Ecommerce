  
import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  //baseURL: "http://127.0.0.1:5000" // 或用你的 API_URL
});

// 自動帶 JWT Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 攔截所有回應（成功或失敗都檢查 token 狀態）
api.interceptors.response.use(
  response => {
    // ===【自動登出攔截】===
    const reqUrl = response.config && response.config.url;
    const isAuthApi = reqUrl && (/login|register|signup|forget|reset/i).test(reqUrl);

    if (
      !isAuthApi &&
      response.data &&
      (
        (typeof response.data.msg === "string" && response.data.msg.toLowerCase().includes("token")) ||
        (typeof response.data.message === "string" && response.data.message.toLowerCase().includes("token"))
      )
    ) {
      // 只在 msg/message 包含 "expired/invalid/過期/無效/失效" 時才觸發
      const text = response.data.msg || response.data.message || "";
      if (/expired|invalid|失效|過期|無效/i.test(text) && localStorage.getItem("token")) {
        localStorage.clear();
        window.location.href = "/";
        return;
      }
    }
    return response;
  },
  error => {
    const reqUrl = error.config && error.config.url;
    const isAuthApi = reqUrl && (/login|register|signup|forget|reset/i).test(reqUrl);

    if (
      !isAuthApi &&
      error.response &&
      (error.response.status === 401 ||
        (error.response.data && (
          (typeof error.response.data.error === "string" && error.response.data.error.toLowerCase().includes("token")) ||
          (typeof error.response.data.message === "string" && error.response.data.message.toLowerCase().includes("token"))
        )))
    ) {
      if (localStorage.getItem("token")) {
        localStorage.clear();
        window.location.href = "/";
        return;
      }
    }
    return Promise.reject(error);
  }
);

export default api;
