import axios from "axios";

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "/api",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshQueue = [];

const processQueue = (error, token = null) => {
  refreshQueue.forEach(p =>
    error ? p.reject(error) : p.resolve(token)
  );
  refreshQueue = [];
};

instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (originalRequest.url.includes("/refresh")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(instance(originalRequest));
            },
            reject,
          });
        });
      }

      isRefreshing = true;

      try {
        const res = await instance.post("/refresh");
        
        const newToken = res.data.data.access_token;

        localStorage.setItem("access_token", newToken);
        processQueue(null, newToken);

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return instance(originalRequest);
      } catch (err) {
        processQueue(err, null);
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export const sendRequest = (url, method, data = {}) =>
  instance({
    url,
    method,
    ...(method === "get" ? { params: data } : { data }),
  }).then(res => res.data);

  export const sendFormdata = (url, method, data) => {
    return new Promise((resolve, reject) => {
        const obj = {
            url: url,
            method: method,
            headers: {'Content-Type': 'multipart/form-data'}
        };
        if (method === 'get') {
            obj['params'] = data;
        } else {
            obj['data'] = data;
        }
        instance(obj)
            .then((response) => {
                
                resolve(response.data); // Trả về dữ liệu từ phản hồi
            })
            .catch((error) => {
                reject(error); // Trả về lỗi nếu có
            });
    });
};

export default instance;