import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Register() {
    const [user_name, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [full_name, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        axios
            .post('http://localhost:8000/register', { user_name, password, full_name, email })
            .then((response) => {
                // Xử lý đăng ký thành công
                console.log('Đăng ký thành công:', response.data);
                navigate('/login'); // Chuyển hướng đến trang đăng nhập
            })
            .catch((error) => {
                // Xử lý lỗi đăng ký
                console.error('Lỗi đăng ký:', error);
                alert('Đăng ký thất bại. Vui lòng thử lại.');
            });
    };

    return (
        <div>
            <h2>Đăng ký</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Tên đăng nhập:</label>
                    <input type="text" value={user_name} onChange={(e) => setUsername(e.target.value)} />
                </div>
                <div>
                    <label>Họ và tên:</label>
                    <input type="text" value={full_name} onChange={(e) => setFullName(e.target.value)} />
                </div>
                <div>
                    <label>Email:</label>
                    <input type="text" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
                <div>
                    <label>Mật khẩu:</label>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
                </div>
                <button type="submit">Đăng ký</button>
            </form>
            <p>Already have an account? <a href='/login'>login</a></p>
        </div>
    );
}

export default Register;