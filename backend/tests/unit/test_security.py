from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False
