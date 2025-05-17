import axios from 'axios';

const instance = axios.create({
    baseURL: process.env.REACT_APP_API_URL, // Thay đổi URL API của bạn
    // timeout: 10000, // Thời gian chờ tối đa (10 giây)
    headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    },
});

instance.interceptors.request.use(
    (config) => {
        
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

instance.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        if (error.response && error.response.status === 401) {
            // Xử lý lỗi 401 (Unauthorized)
            // Ví dụ: Chuyển hướng người dùng về trang đăng nhập
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const sendRequest = (url, method, data) => {
    return new Promise((resolve, reject) => {
        const obj = {
            url: url,
            method: method,
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