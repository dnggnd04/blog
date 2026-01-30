import React, { useState } from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { sendRequest } from '../../utils/axiosConfig';
import { useNavigate, useLocation } from 'react-router-dom';

function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const location = useLocation(); // Lấy location
    const navigate = useNavigate();

    
    const handleSubmit = (event) => {
        event.preventDefault();
        const callApi = async () => {
            try {
                const loginRequest = {
                    user_name: username,
                    password: password
                }
                const response = await sendRequest('/login', 'post', loginRequest)
                
                localStorage.setItem('access_token', response.data.access_token);
                console.log('Đăng nhập thành công:');
                const from = location.state?.from?.pathname || '/'; // Lấy đường dẫn ban đầu
                navigate(from, { replace: true }); // Chuyển hướng về đường dẫn ban đầu
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };

        callApi()
    };

    return (
        <PageWrapper>
            <LoginCard>
                <Title>Welcome back 👋</Title>
                <Subtitle>Đăng nhập để tiếp tục</Subtitle>

                <Form onSubmit={handleSubmit}>
                    <FormGroup>
                        <Label>Tên đăng nhập</Label>
                        <Input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Nhập tên đăng nhập"
                        />
                    </FormGroup>

                    <FormGroup>
                        <Label>Mật khẩu</Label>
                        <Input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Nhập mật khẩu"
                        />
                    </FormGroup>

                    <LoginButton type="submit">
                        Đăng nhập
                    </LoginButton>
                </Form>

                <FooterText>
                    Chưa có tài khoản? <Link to="/register">Đăng ký</Link>
                </FooterText>
            </LoginCard>
        </PageWrapper>
    );
}

export default Login;



const PageWrapper = styled.div`
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    font-family: sans-serif;
`;

const LoginCard = styled.div`
    width: 380px;
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

const LoginButton = styled.button`
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
