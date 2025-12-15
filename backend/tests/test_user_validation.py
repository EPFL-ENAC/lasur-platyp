import pytest
from pydantic import ValidationError
from api.models.users import AppUserDraftValidated


def test_valid_user_data():
    """Test that valid user data passes validation"""
    user = AppUserDraftValidated(
        username="john_doe",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        password="SecurePassword123!"
    )
    assert user.username == "john_doe"
    assert user.first_name == "John"
    assert user.last_name == "Doe"


def test_username_with_special_chars():
    """Test that username with allowed special characters passes"""
    user = AppUserDraftValidated(
        username="john.doe-123",
        email="john@example.com",
        first_name="John",
        last_name="Doe",
        password="SecurePassword123!"
    )
    assert user.username == "john.doe-123"


def test_name_with_apostrophe():
    """Test that names with apostrophes pass validation"""
    user = AppUserDraftValidated(
        username="test_user",
        email="test@example.com",
        first_name="O'Brien",
        last_name="D'Angelo",
        password="SecurePassword123!"
    )
    assert user.first_name == "O'Brien"
    assert user.last_name == "D'Angelo"


def test_name_with_hyphen():
    """Test that hyphenated names pass validation"""
    user = AppUserDraftValidated(
        username="test_user",
        email="test@example.com",
        first_name="Jean-Paul",
        last_name="Saint-Pierre",
        password="SecurePassword123!"
    )
    assert user.first_name == "Jean-Paul"
    assert user.last_name == "Saint-Pierre"


def test_name_with_accents():
    """Test that names with accented characters pass validation"""
    user = AppUserDraftValidated(
        username="test_user",
        email="test@example.com",
        first_name="François",
        last_name="Müller",
        password="SecurePassword123!"
    )
    assert user.first_name == "François"
    assert user.last_name == "Müller"


def test_username_too_short():
    """Test that username shorter than 3 characters fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="ab",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "Username must be between 3 and 50 characters" in str(exc_info.value)


def test_username_too_long():
    """Test that username longer than 50 characters fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="a" * 51,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "Username must be between 3 and 50 characters" in str(exc_info.value)


def test_username_with_invalid_chars():
    """Test that username with invalid characters fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="user@name",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "Username can only contain letters, numbers, dots, hyphens, and underscores" in str(exc_info.value)


def test_username_with_spaces():
    """Test that username with spaces fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="user name",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "Username can only contain letters, numbers, dots, hyphens, and underscores" in str(exc_info.value)


def test_empty_username():
    """Test that empty username fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "Username cannot be empty" in str(exc_info.value)


def test_empty_first_name():
    """Test that empty first name fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "First name cannot be empty" in str(exc_info.value)


def test_empty_last_name():
    """Test that empty last name fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="John",
            last_name="",
            password="SecurePassword123!"
        )
    assert "Last name cannot be empty" in str(exc_info.value)


def test_first_name_too_long():
    """Test that first name longer than 100 characters fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="a" * 101,
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "First name must be at most 100 characters" in str(exc_info.value)


def test_last_name_too_long():
    """Test that last name longer than 100 characters fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="John",
            last_name="a" * 101,
            password="SecurePassword123!"
        )
    assert "Last name must be at most 100 characters" in str(exc_info.value)


def test_first_name_with_numbers():
    """Test that first name with numbers fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="John123",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "First name can only contain letters, spaces, hyphens, and apostrophes" in str(exc_info.value)


def test_last_name_with_numbers():
    """Test that last name with numbers fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="John",
            last_name="Doe123",
            password="SecurePassword123!"
        )
    assert "Last name can only contain letters, spaces, hyphens, and apostrophes" in str(exc_info.value)


def test_first_name_with_special_chars():
    """Test that first name with special characters (except allowed ones) fails"""
    with pytest.raises(ValidationError) as exc_info:
        AppUserDraftValidated(
            username="test_user",
            email="test@example.com",
            first_name="John@",
            last_name="Doe",
            password="SecurePassword123!"
        )
    assert "First name can only contain letters, spaces, hyphens, and apostrophes" in str(exc_info.value)


def test_username_trimmed():
    """Test that username is trimmed of whitespace"""
    user = AppUserDraftValidated(
        username="  john_doe  ",
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="SecurePassword123!"
    )
    assert user.username == "john_doe"


def test_names_trimmed():
    """Test that names are trimmed of whitespace"""
    user = AppUserDraftValidated(
        username="test_user",
        email="test@example.com",
        first_name="  John  ",
        last_name="  Doe  ",
        password="SecurePassword123!"
    )
    assert user.first_name == "John"
    assert user.last_name == "Doe"
