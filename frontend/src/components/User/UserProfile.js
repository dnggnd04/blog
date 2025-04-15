import React, { useState } from "react";
import styled from "styled-components";
import { sendFormdata } from "../../utils/axiosConfig";

const UserProfileWrapper = styled.div`
  font-family: sans-serif;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
`;

const UserInfo = styled.div`
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const UserName = styled.h2`
  font-size: 24px;
  margin-bottom: 10px;
  color: #333;
  text-align: center;
`;

const UserEmail = styled.p`
  font-size: 16px;
  color: #555;
  margin-bottom: 10px;
  text-align: center;
`;

const AvatarContainer = styled.div`
  position: relative;
  width: 100px;
  height: 100px;
  margin-bottom: 10px;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
  
  &:hover .overlay {
    opacity: 1; /* Khi hover, dấu + sẽ hiện */
  }
`;

const UserAvatar = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
`;

const Overlay = styled.label`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 123, 255, 0.6); /* Xanh dương nhạt */
  color: white;
  font-size: 40px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0; /* Mặc định ẩn */
  transition: opacity 0.3s ease;

  &:hover {
    background: rgba(0, 123, 255, 0.8);
  }
`;

const HiddenFileInput = styled.input`
  display: none;
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.img`
  max-width: 80%;
  max-height: 80%;
`;

function UserProfile({ user, isOwnProfile }) {
  const [avatar, setAvatar] = useState(user.avatar);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleUpload = async (event) => {
    const avatar = event.target.files[0];
    if (avatar) {
        const objectURL = URL.createObjectURL(avatar);
        setAvatar(objectURL); 
        const formData = new FormData()
        formData.append('avatar', avatar)
        const res = await sendFormdata('/users/me/avatar', 'put', formData)
        console.log(res.data);
        
    }
  };

  const handleAvatarClick = () => {
    if (!isOwnProfile) {
      setIsModalOpen(true);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <UserProfileWrapper>
      <UserInfo>
        <UserName>Thông tin người dùng</UserName>
        <AvatarContainer onClick={handleAvatarClick}>
          <UserAvatar src={avatar} alt="Avatar" />
          {isOwnProfile && (
            <Overlay className="overlay">
              +
              <HiddenFileInput type="file" accept="image/*" onChange={handleUpload} />
            </Overlay>
          )}
        </AvatarContainer>
        <UserName>{user.full_name}</UserName>
        <UserEmail>Email: {user.email}</UserEmail>
      </UserInfo>
      {isModalOpen && (
        <Modal onClick={closeModal}>
          <ModalContent src={avatar} alt="Avatar lớn" />
        </Modal>
      )}
    </UserProfileWrapper>
  );
}

export default UserProfile;
