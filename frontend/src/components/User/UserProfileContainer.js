import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import UserProfile from './UserProfile';
import { sendRequest } from '../../utils/axiosConfig';


function UserProfileContainer() {
    const { userId } = useParams();
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        const callApi = async () => {
          try {
            const res = await sendRequest(`users/${userId}`, 'get', {});
            setUser(res.data);
          } catch (error) {
            console.error('Lỗi khi lấy thông tin người dùng:', error);
          }
        };
    
        callApi();
    }, [userId]);

    if (!user) {
        return <div>Loading...</div>;
    }

    return <UserProfile user={user} isOwnProfile={false} />
}

export default UserProfileContainer;