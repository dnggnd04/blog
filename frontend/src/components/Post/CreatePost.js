import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendRequest } from '../../utils/axiosConfig';
import styled from 'styled-components';

const CreatePostWrapper = styled.div`
    font-family: sans-serif;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	max-width: 800px;
    width: 100%;
    margin-bottom: 20px
`;

const Form = styled.form`
    border: 1px solid #ddd;
    padding: 20px;
    border-radius: 8px;
    background-color: #fff;
`;

const Label = styled.label`
    font-size: 16px;
    color: #333;
    margin-bottom: 5px;
    display: block;
`;

const Input = styled.input`
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
`;

const TextArea = styled.textarea`
    width: 100%;
    padding: 10px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    resize: vertical;
`;

const SubmitButton = styled.button`
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    &:hover {
        background-color: #45a049;
    }
`;

function CreatePost({ onPostCreated }) {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const navigate = useNavigate();

    const handleSubmit = (event) => {
        event.preventDefault();

        const callApi = async () => {
            try {
                const postRequest = {
                    title: title,
                    content: content
                }
                const res = await sendRequest('/posts', 'post', postRequest);
                onPostCreated(res.data)
                setTitle('')
                setContent('')
                navigate('/');
            } catch (error) {
                console.error('Lỗi khi đăng bài:', error);
                alert('Đăng bài thất bại. Vui lòng thử lại.');
            }
        }
        callApi();
    };

    return (
        <CreatePostWrapper>
            <h2>Đăng bài mới</h2>
            <Form onSubmit={handleSubmit}>
                <div>
                    <Label>Tiêu đề:</Label>
                    <Input type="text" value={title} onChange={(e) => setTitle(e.target.value)} />
                </div>
                <div>
                    <Label>Nội dung:</Label>
                    <TextArea value={content} onChange={(e) => setContent(e.target.value)} />
                </div>
                <SubmitButton type="submit">Đăng bài</SubmitButton>
            </Form>
        </CreatePostWrapper>
    );
}

export default CreatePost;