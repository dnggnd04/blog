import React from 'react';
import styled from 'styled-components';
import UserProfileLink from './UserProfileLink'

const CommentListWrapper = styled.div`
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
`;

const CommentItem = styled.li`
  background-color: #fff;
  border-radius: 4px;
  padding: 10px 15px;
  margin-bottom: 10px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  list-style: none;
  display: flex;
  align-items: center;  /* Căn avatar thẳng với nội dung */
  gap: 10px;  /* Tạo khoảng cách hợp lý */
`;

const CommentHeader = styled.h3`
  font-size: 20px;
  margin-bottom: 20px;
  color: #333;
`;

const CommentContent = styled.span`
  color: #777;
  flex: 1; /* Để nội dung comment không bị chồng chéo */
`;

const CommentList = ({ comments }) => {
    return (
        <CommentListWrapper>
            <CommentHeader>Bình luận</CommentHeader>
            <ul>
                {comments.map((comment) => (
                    <CommentItem key={comment.id}>
                        <UserProfileLink userId={comment.author_id} avatar={comment.avatar} full_name={comment.full_name} />
                        <CommentContent>{comment.content}</CommentContent>
                    </CommentItem>
                ))}
            </ul>
        </CommentListWrapper>
    );
};

export default CommentList;
