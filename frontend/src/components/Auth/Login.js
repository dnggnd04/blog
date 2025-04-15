import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, useLocation } from 'react-router-dom';

function Login() {
    const [user_name, setUserName] = useState('');
    const [password, setPassword] = useState('');
    const location = useLocation(); // Lấy location
    const navigate = useNavigate();

    
    const handleSubmit = (event) => {
        event.preventDefault();
        axios
            .post('http://localhost:8000/login', { user_name, password })
            .then((response) => {
                // Lưu trữ access_token vào LocalStorage
                localStorage.setItem('access_token', response.data.data.access_token);
                console.log('Đăng nhập thành công:');
                const from = location.state?.from?.pathname || '/'; // Lấy đường dẫn ban đầu
                navigate(from, { replace: true }); // Chuyển hướng về đường dẫn ban đầu
            })
            .catch((error) => {
                console.error('Lỗi đăng nhập:', error);
                alert('Tên đăng nhập hoặc mật khẩu không đúng.');
            });
    };

    return (
        <div>
            <h2>Đăng nhập</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Tên đăng nhập:</label>
                    <input type="text" value={user_name} onChange={(e) => setUserName(e.target.value)} />
                </div>
                <div>
                    <label>Mật khẩu:</label>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                </div>
                <button type="submit">Đăng nhập</button>
            </form>
            <div>
                <p>Haven't have an account? <a href='/register'>register</a></p>
            </div>
        </div>
    );
}

export default Login;