import React from 'react';
import styled from 'styled-components';

const FooterWrapper = styled.footer`
    background-color: #333;
    color: #fff;
    text-align: center;
    padding: 20px 0;
    margin-top: 20px;
    border-top: 3px solid #4CAF50;
`;

const FooterText = styled.p`
    font-size: 16px;
    margin: 0;
`;

function Footer() {
    return (
        <FooterWrapper>
            <FooterText>&copy; {new Date().getFullYear()} Blog của tôi</FooterText>
        </FooterWrapper>
    );
}

export default Footer;
