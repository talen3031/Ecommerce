import axios from "axios";

function getGuestId() {
  let guestId = localStorage.getItem("guest_id");
  if (!guestId) {
    // 簡易 uuid
    guestId = "g_" + ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
    localStorage.setItem("guest_id", guestId);
  }
  return guestId;
}
export { getGuestId };


const api = axios.create({
  //baseURL: "http://localhost:5000",
  baseURL: process.env.REACT_APP_API_URL,
  withCredentials: true, // 全部請求都自動帶 cookie（可選，也可只在 /auth/refresh 加）
});

// ===== Request 攔截 =====
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ===== Response 攔截 =====
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error); // 如果 refresh 失敗，通知所有排隊的 request 失敗
    } else {
      prom.resolve(token);// 如果 refresh 成功，讓所有排隊的 request 繼續、拿到新 token
    }
  })
  failedQueue = [];
}

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    const reqUrl = originalRequest.url;
    const isAuthApi = /login|register|signup|forget|reset|refresh/i.test(reqUrl);

    if (!isAuthApi &&  // 不是登入/註冊等 API（這些不需要 refresh）
      error.response && // 有回傳錯誤 
      error.response.status === 401 && // 是 401（未授權，通常是 access token 過期）
      !originalRequest._retry   // 這個 request 沒重試過（防止無限迴圈）
      ) {

      if (isRefreshing) {
        // 有其他 request 已在跑 refresh，自己先排隊
        return new Promise(function(resolve, reject) {
          failedQueue.push({resolve, reject});
        }).then(token => {
          // 拿到新 token，重發剛剛那個 request
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true; // 標記這個 request 已經進行過一次 retry（避免無限迴圈）
      isRefreshing = true;  // 設定「正在刷新中」

      try {
        // 呼叫 /auth/refresh，瀏覽器自動帶 HttpOnly cookie
        const resp = await axios.post(
          api.defaults.baseURL + "/auth/refresh",
          {},
          { withCredentials: true }
        );
        const newAccessToken = resp.data.access_token;
        localStorage.setItem("token", newAccessToken);

        api.defaults.headers.common['Authorization'] = 'Bearer ' + newAccessToken;
        processQueue(null, newAccessToken);

        // 用新 token 重發原本請求
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
        return api(originalRequest);

      } catch (err) {
        processQueue(err, null);
        localStorage.clear();
        window.location.href = "/";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api;





