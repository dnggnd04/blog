import React, { useState } from 'react';
import styled from 'styled-components';
import { Link, useNavigate } from 'react-router-dom';
import { sendRequest } from '../../utils/axiosConfig';

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
                };
                await sendRequest('/register', 'post', registerRequest);
                console.log('Đăng ký thành công');
                navigate('/login');
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };
        callApi();
    };

    return (
        <PageWrapper>
            <RegisterCard>
                <Title>Tạo tài khoản mới ✨</Title>
                <Subtitle>Tham gia cộng đồng blog ngay hôm nay</Subtitle>

                <Form onSubmit={handleSubmit}>
                    <FormGroup>
                        <Label>Họ và tên</Label>
                        <Input
                            type="text"
                            value={full_name}
                            onChange={(e) => setFullName(e.target.value)}
                            placeholder="Nhập họ và tên của bạn"
                            required
                        />
                    </FormGroup>

                    <FormGroup>
                        <Label>Tên đăng nhập</Label>
                        <Input
                            type="text"
                            value={user_name}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Chọn tên đăng nhập"
                            required
                        />
                    </FormGroup>

                    <FormGroup>
                        <Label>Email</Label>
                        <Input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="example@gmail.com"
                            required
                        />
                    </FormGroup>

                    <FormGroup>
                        <Label>Mật khẩu</Label>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Nhập mật khẩu (ít nhất 6 ký tự)"
                            required
                        />
                    </FormGroup>

                    <RegisterButton type="submit">
                        Đăng ký ngay
                    </RegisterButton>
                </Form>

                <FooterText>
                    Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
                </FooterText>
            </RegisterCard>
        </PageWrapper>
    );
}

export default Register;

const PageWrapper = styled.div`
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    font-family: sans-serif;
    padding: 20px; /* Thêm padding để tránh chạm viền trên mobile */
`;

const RegisterCard = styled.div`
    width: 400px; /* Tăng nhẹ chiều rộng vì có nhiều field hơn login */
    background-color: #fff;
    padding: 32px;
    border-radius: 16px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
`;

const Title = styled.h2`
    text-align: center;
    font-size: 24px;
    margin-bottom: 8px;
    color: #333;
`;

const Subtitle = styled.p`
    text-align: center;
    font-size: 14px;
    color: #666;
    margin-bottom: 24px;
`;

const Form = styled.form`
    display: flex;
    flex-direction: column;
    gap: 16px;
`;

const FormGroup = styled.div`
    display: flex;
    flex-direction: column;
`;

const Label = styled.label`
    font-size: 13px;
    margin-bottom: 6px;
    color: #444;
`;

const Input = styled.input`
    padding: 10px 12px;
    font-size: 14px;
    border-radius: 8px;
    border: 1px solid #ccc;
    outline: none;
    transition: all 0.2s ease;

    &:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
`;

const RegisterButton = styled.button`
    margin-top: 8px;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
    color: white;
    background-color: #6366f1;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s ease;

    &:hover {
        background-color: #4f46e5;
    }
`;

const FooterText = styled.p`
    margin-top: 20px;
    text-align: center;
    font-size: 14px;
    color: #666;

    a {
        color: #6366f1;
        font-weight: 500;
        text-decoration: none;
    }

    a:hover {
        text-decoration: underline;
    }
`;