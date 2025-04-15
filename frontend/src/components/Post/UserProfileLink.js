import React from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';

const UserContainer = styled.div`
    display: flex;
    align-items: center;
    cursor: pointer;
    &:hover {
        opacity: 0.8;
    }
`;

const UserAvatar = styled.img`
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    margin-right: 10px;
`;

const UserName = styled.span`
    font-size: 18px;
    font-weight: bold;
    color: #333;
`;

function UserProfileLink({ userId, avatar, full_name }) {
    const navigate = useNavigate();

    const handleClick = () => {
        navigate(`/users/${userId}`);
    };

    return (
        <UserContainer onClick={handleClick}>
            <UserAvatar src={avatar} alt="Avatar" />
            <UserName>{full_name}</UserName>
        </UserContainer>
    );
}

export default UserProfileLink;
