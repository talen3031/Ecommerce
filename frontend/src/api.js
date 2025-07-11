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

// ====== 這是新加的「自動登出攔截」區 ======
api.interceptors.response.use(
  response => response,
  error => {
    // 假設後端回傳 401 或錯誤訊息包含 token 過期
    if (
      error.response &&
      (error.response.status === 401 ||
       (error.response.data && (
         error.response.data.error?.toString().toLowerCase().includes("token") ||
         error.response.data.message?.toString().toLowerCase().includes("token")
       )))
    ) {
      // 清空 localStorage，導向登入頁
      localStorage.clear();
      // 可以用 window.location 立即刷新，不用 react-router navigate（因 api.js 是純 function）
      alert("登入逾時，請重新登入");
      window.location.href = "/login";
      // 直接 return 拒絕這個 promise
      return Promise.reject(new Error("登入逾時，請重新登入"));
    }
    // 其它錯誤照舊
    return Promise.reject(error);
  }
);

export default api;