import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import api, { sendRequest } from '../../utils/axiosConfig';
import PostDetail from './PostDetail';
import websocketUrl from '../../utils/websocketConfig'

function PostDetailContainer() {
    const { id } = useParams();
    const [post, setPost] = useState(null);
    const [likes, setLikes] = useState(0);
    const [comments, setComments] = useState([]);

    useEffect(() => {
        const callApi = async (id) => {
            try {
                const res = await Promise.all([
                    sendRequest(`/posts/${id}`),
                    sendRequest(`/posts/${id}/comments`)
                ]);
                console.log(res);
                
                setPost(res[0].data);
                setLikes(res[0].data.like_count || 0);
                const temp_comments = res[1].data
                setComments(temp_comments.reverse() || []);
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };
        callApi(id)

        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const wsUrl = `${protocol}://${window.location.host}/ws`;
        const socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WS PARSED:", data);
                if (data.type === 'like' && data.post_id === parseInt(id)) {
                    setLikes(data.like_count);
                }

                if (data.type === 'comment' && data.post_id === parseInt(id)) {
                    setComments((prevComments) => {
                        if (!prevComments.some((comment) => comment.id === data.id)) {
                            return [...prevComments, data];
                        }
                        return prevComments;
                    });
                }
            } catch (error) {
                console.error('Lỗi xử lý WebSocket:', error);
            }
        };

	return () => {
		socket.close();
	}
    }, [id]);

    const handleLike = () => {
        const callApi = async () => {
            try {
                const likeRequest = {
                    post_id: id
                }
                await sendRequest('/likes', 'post', likeRequest)
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };

        callApi(id)
    };

    const handleComment = (commentText) => {
        const callApi = async (id) => {
            try {
                const commentRequest = {
                    content: commentText,
                    post_id: id
                }

                await sendRequest('/comments', 'post', commentRequest)
            } catch (error) {
                console.error('Lỗi khi gọi API:', error);
            }
        };

        callApi(id)
    };

    return <PostDetail post={post} likes={likes} onLike={handleLike} comments={comments} onComment={handleComment} />;

}

export default PostDetailContainer;
