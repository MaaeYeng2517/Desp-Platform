from datetime import datetime

from backend.app.security import (
    create_access_token,
    create_csrf_token,
    decode_token,
    generate_api_key,
    hash_api_key,
    hash_password,
    verify_csrf_token,
    verify_password,
)


def test_password_hashing_is_one_way():
    password = "correct horse battery staple"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)


def test_api_key_is_hashed_with_prefix():
    plain_key, prefix, digest = generate_api_key()

    assert prefix == plain_key[:16]
    assert digest == hash_api_key(plain_key)
    assert digest != plain_key
    assert len(plain_key) > 40


def test_csrf_token_is_signed():
    token = create_csrf_token()

    assert verify_csrf_token(token, token)
    assert not verify_csrf_token("invalid", token)


def test_access_token_can_be_decoded():
    token = create_access_token({"user_id": "user-1", "tenant_id": "tenant-1"})
    payload = decode_token(token, "access")

    assert payload["user_id"] == "user-1"
    assert datetime.fromtimestamp(payload["exp"]) > datetime.utcnow()
