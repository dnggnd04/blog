import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendRequest } from '../../utils/axiosConfig';
import PostList from './PostList';
import styled from 'styled-components';
import CreatePost from './CreatePost';
import websocketUrl from '../../utils/websocketConfig'

const PostListContainerWrapper = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
`;

function PostListContainer() {
	const [posts, setPosts] = useState([]);
	const navigate = useNavigate()

	useEffect(() => {

		const callApi = async () => {
			try {
				const res = await Promise.all([
					sendRequest('/posts', 'get', {})
				])
				
				if (res[0].data) {
					const updatedPosts = res[0].data.map((post) => ({
						...post,
						likes: post.like_count || 0
					}))
					setPosts(updatedPosts)
				} 
			} catch (error) {
				console.error('Lỗi khi lấy dữ liệu bài viết:', error);
			}
		}

		callApi()

                const protocol = window.location.protocol === "https:" ? "wss" : "ws";
                const wsUrl = `${protocol}://${window.location.host}/ws`;
		const socket = new WebSocket(wsUrl);

                socket.onmessage = (event) => {
                         try {
				const data = JSON.parse(event.data);

				if (data.type === 'like') {
					setPosts((prevPosts) =>
						prevPosts.map((post) =>
							post.id === data.post_id
								? { ...post, likes: data.like_count }
								: post
						)
					);
				}
                         } catch (error) {
                                console.error('Lỗi xử lý WebSocket:', error);
                         }
                  };

                  return () => {
                         socket.close();
                  }

	}, []);

	const handleLike = (postId) => {

		const callApi = async (postId) => {
			try {
				const likeRequest = {
					post_id: postId
				}
				await sendRequest('/likes', 'post', likeRequest)
			} catch (error) {
				
			}
		}
		callApi(postId)
    };
  
	const handleComment = (url) => {
		navigate(url)
	}

	const handlePostCreated = (newPost) => {
        setPosts((prevPosts) => [newPost, ...prevPosts]);
    };

	// return <PostList posts={posts} onLike={handleLike} onComment={handleComment} />;
	return (
        <PostListContainerWrapper>
            <CreatePost onPostCreated={handlePostCreated} />
            <PostList posts={posts} onLike={handleLike} onComment={handleComment} />
        </PostListContainerWrapper>
    );
}

export default PostListContainer;
