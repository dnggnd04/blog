import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const HeaderWrapper = styled.header`
    background-color: #333;
    color: #fff;
    padding: 20px 0;
    border-bottom: 3px solid #4CAF50;
`;

const HeaderTitle = styled.h1`
    font-size: 28px;
    margin: 0;
    text-align: center;
`;

const Nav = styled.nav`
    text-align: center;
    margin-top: 10px;
`;

const NavLink = styled(Link)`
    color: #fff;
    text-decoration: none;
    margin: 0 15px;
    font-size: 18px;
    transition: color 0.3s ease;
    &:hover {
        color: #4CAF50;
    }
`;

function Header() {
    return (
        <HeaderWrapper>
            <HeaderTitle>Blog của tôi</HeaderTitle>
            <Nav>
                <NavLink to="/">Trang chủ</NavLink>
                <NavLink to="/about">Giới thiệu</NavLink>
                <NavLink to="/contact">Liên hệ</NavLink>
                <NavLink to="/profile">Profile</NavLink>
            </Nav>
        </HeaderWrapper>
    );
}

export default Header;
