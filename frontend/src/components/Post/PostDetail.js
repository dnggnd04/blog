import React from 'react';
import CommentList from './CommentList';
import CommentForm from './CommentForm';
import styled from 'styled-components';
import UserProfileLink from './UserProfileLink';

const PostDetailWrapper = styled.div`
    font-family: sans-serif;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 800px; /* Giới hạn chiều rộng */
    margin: 0 auto; /* Căn giữa màn hình */
`;

const PostArticle = styled.article`
    border: 1px solid #ddd;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    background-color: #fff;
`;

const PostTitle = styled.h2`
    font-size: 24px;
    margin-bottom: 10px;
    color: #333;
`;

const PostContent = styled.p`
    font-size: 16px;
    color: #555;
    line-height: 1.6;
`;

const LikeButton = styled.button`
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

function PostDetail({ post, likes, onLike, comments, onComment }) {
    if (!post) {
        return <div>Đang tải...</div>;
    }

    return (
        <PostDetailWrapper>
            <PostArticle>
                <UserProfileLink userId={post.author_id} avatar={post.avatar} full_name={post.full_name} />
                <PostTitle>{post.title}</PostTitle>
                <PostContent>{post.content}</PostContent>
                <LikeButton onClick={onLike}>Like ({likes})</LikeButton>
                <CommentList comments={comments} />
                <CommentForm postId={post.id} onComment={onComment} />
            </PostArticle>
        </PostDetailWrapper>
    );
}

export default PostDetail;
