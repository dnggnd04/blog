// import React from 'react';
// import styled from 'styled-components';
// import { Link } from 'react-router-dom';

// const PostListWrapper = styled.div`
//     font-family: sans-serif;
//     padding: 20px;
//     background-color: #f9f9f9;
//     border-radius: 8px;
//     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
//     max-width: 800px;
//     margin: 20px auto;
//     display: flex;
//     flex-direction: column;
//     align-items: center;
// `;

// const PostItem = styled.div`
//     border: 1px solid #ddd;
//     padding: 20px;
//     margin-bottom: 20px;
//     border-radius: 8px;
//     background-color: #fff;
//     transition: box-shadow 0.3s ease;
//     width: 100%;
//     &:hover {
//         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
//     }
// `;

// const PostTitle = styled.h2`
//     font-size: 20px;
//     margin-bottom: 10px;
//     color: #333;
// `;

// const PostContent = styled.p`
//     font-size: 16px;
//     color: #555;
//     line-height: 1.6;
//     margin-bottom: 10px;
// `;

// const ActionButtons = styled.div`
//     display: flex;
//     gap: 10px;
// `;

// const LikeButton = styled.button`
//     background-color: #4CAF50;
//     border: none;
//     color: white;
//     padding: 10px 20px;
//     font-size: 16px;
//     cursor: pointer;
//     border-radius: 4px;
//     transition: background-color 0.3s ease;
//     &:hover {
//         background-color: #45a049;
//     }
// `;

// const CommentButton = styled.button`
//     background-color: #008CBA;
//     border: none;
//     color: white;
//     padding: 10px 20px;
//     font-size: 16px;
//     cursor: pointer;
//     border-radius: 4px;
//     transition: background-color 0.3s ease;
//     &:hover {
//         background-color: #007bb5;
//     }
// `;

// function PostList({ posts, onLike, onComment }) {
//     if (!posts) {
//         return <div>Đang tải...</div>;
//     }

//     return (
//         <PostListWrapper>
//             {posts.map((post) => (
//                 <PostItem key={post.id}>
//                     <Link to={`/posts/${post.id}`}>
//                         <PostTitle>{post.title}</PostTitle>
//                     </Link>
//                     <PostContent>{post.content}</PostContent>
//                     <ActionButtons>
//                         <LikeButton onClick={() => onLike(post.id)}>Like ({post.likes || 0})</LikeButton>
//                         <CommentButton onClick={() => onComment(`/posts/${post.id}`)}>Comment</CommentButton>
//                     </ActionButtons>
//                 </PostItem>
//             ))}
//         </PostListWrapper>
//     );
// }

// export default PostList;


import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import UserProfileLink from './UserProfileLink';

const PostListWrapper = styled.div`
    font-family: sans-serif;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 800px;
    margin: 20px auto;
    display: flex;
    flex-direction: column;
    align-items: center;
`;

const PostItem = styled.div`
    border: 1px solid #ddd;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    background-color: #fff;
    transition: box-shadow 0.3s ease;
    width: 100%;
    &:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
`;

const PostTitle = styled.h2`
    font-size: 20px;
    margin-bottom: 10px;
    color: #333;
`;

const PostContent = styled.p`
    font-size: 16px;
    color: #555;
    line-height: 1.6;
    margin-bottom: 10px;
`;

const ActionButtons = styled.div`
    display: flex;
    gap: 10px;
`;

const LikeButton = styled.button`
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

const CommentButton = styled.button`
    background-color: #008CBA;
    border: none;
    color: white;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.3s ease;
    &:hover {
        background-color: #007bb5;
    }
`;

function PostList({ posts, onLike, onComment }) {
    if (!posts) {
        return <div>Đang tải...</div>;
    }

    return (
        <PostListWrapper>
            {posts.map((post) => (
                <PostItem key={post.id}>
                    {/* Hiển thị Avatar + Tên người dùng */}
                    <UserProfileLink userId={post.author_id} avatar={post.avatar} full_name={post.full_name} />

                    {/* Tiêu đề bài viết */}
                    <Link to={`/posts/${post.id}`}>
                        <PostTitle>{post.title}</PostTitle>
                    </Link>

                    {/* Nội dung bài viết */}
                    <PostContent>{post.content}</PostContent>

                    {/* Nút Like & Comment */}
                    <ActionButtons>
                        <LikeButton onClick={() => onLike(post.id)}>Like ({post.likes || 0})</LikeButton>
                        <CommentButton onClick={() => onComment(`/posts/${post.id}`)}>Comment</CommentButton>
                    </ActionButtons>
                </PostItem>
            ))}
        </PostListWrapper>
    );
}

export default PostList;
