from app.services.auth.passwords import (
    hash_password,
    verify_password,
)


def test_password_hash_is_not_plaintext():
    password = "SecurePassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password


def test_password_verification_succeeds_for_correct_password():
    password = "SecurePassword123!"

    hashed_password = hash_password(password)

    assert verify_password(
        password,
        hashed_password,
    )


def test_password_verification_fails_for_wrong_password():
    password = "SecurePassword123!"

    hashed_password = hash_password(password)

    assert not verify_password(
        "WrongPassword123!",
        hashed_password,
    )