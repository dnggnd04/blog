import React, { useState, useEffect  } from 'react';
import { sendRequest } from '../../utils/axiosConfig';
import UserProfile from './UserProfile';

function Profile() {
    const [user, setUser] = useState(null);

    useEffect(() => { 
        const callApi = async () => {
          try {
            const res = await sendRequest('users/me', 'get', {});
            setUser(res.data);
          } catch (error) {
            console.error('Lỗi khi lấy thông tin người dùng:', error);
          }
        };
    
        callApi();
    }, []);

    if (!user) {
        return <div>Loading...</div>;
    }

    return <UserProfile user={user} isOwnProfile={true} />
}

export default Profile;