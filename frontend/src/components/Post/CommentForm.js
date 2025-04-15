import React, { useState } from 'react';
import axios from 'axios';
import styled from 'styled-components';
import { sendRequest } from '../../utils/axiosConfig';


const CommentFormWrapper = styled.div`
    margin-top: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const CommentTextArea = styled.textarea`
    width: 100%;
    height: 100px;
    margin-top: 10px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    resize: vertical;
    &:focus {
        border-color: #4CAF50;
        outline: none;
    }
`;

const CommentButton = styled.button`
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    margin-top: 10px;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    &:hover {
        background-color: #45a049;
    }
`;

const CommentLabel = styled.label`
    font-size: 18px;
    color: #333;
    display: block;
    margin-bottom: 10px;
`;

function CommentForm({ postId, onComment }) {
    const [commentText, setCommentText] = useState('');

    return (
        <CommentFormWrapper>
            <CommentLabel htmlFor="commentTextArea">Nhập bình luận của bạn:</CommentLabel>
            <CommentTextArea
                id="commentTextArea"
                placeholder="Nhập bình luận..."
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
            />
            <CommentButton onClick={() => {
                onComment(commentText)
                setCommentText('')
            }}>Gửi bình luận</CommentButton>
        </CommentFormWrapper>
    );
}

export default CommentForm;
