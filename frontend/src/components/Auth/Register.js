import React, { useState } from 'react';
import { sendRequest } from '../../utils/axiosConfig';
import { useNavigate } from 'react-router-dom';

function Register() {
    const [user_name, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [full_name, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();
        const callApi = async () => {
            try {
                const registerRequest = {
                    full_name: full_name,
                    user_name: user_name,
                    email: email,
                    password: password
                }
                await sendRequest('/register', 'post', registerRequest)
                console.log('Đăng ký thành công:');
                navigate('/login');
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };

        callApi()
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