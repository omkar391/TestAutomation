import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserCredentials(BaseModel):
    """User credentials schema for authentication test cases."""

    email: EmailStr = Field(description="User login email address")
    password: str = Field(description="User login password")
    username: Optional[str] = Field(default=None, description="Display name expected on the page")
    is_valid: bool = Field(default=True, description="Flag indicating if credentials should succeed")
    expected_error: Optional[str] = Field(default=None, description="Expected error message if invalid")


class UserRegistration(BaseModel):
    """User details schema for account registration scenarios."""

    name: str
    email: EmailStr
    password: str
    title: str = "Mr"  # 'Mr' or 'Mrs'
    birth_day: str = "15"
    birth_month: str = "July"
    birth_year: str = "1990"
    first_name: str
    last_name: str
    company: str = "Enterprise QA Solutions"
    address1: str = "100 Automation Blvd"
    address2: Optional[str] = "Suite 400"
    country: str = "United States"
    state: str = "California"
    city: str = "San Francisco"
    zipcode: str = "94105"
    mobile_number: str = "14155551234"


class ProductData(BaseModel):
    """Catalog product representation for verification."""

    product_id: Optional[str] = None
    name: str
    price: Optional[str] = None
    category: Optional[str] = None
    quantity: int = 1


class TestUsersRepository:
    """Repository loader for test user datasets."""

    def __init__(self, json_path: Optional[Path] = None):
        path = json_path or (Path(__file__).parent / "users.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.valid_user: UserCredentials = UserCredentials(**data["valid_user"])
        self.invalid_users: List[UserCredentials] = [
            UserCredentials(**item) for item in data["invalid_users"]
        ]
        self.existing_user_signup: UserCredentials = UserCredentials(**data["existing_user_signup"])


def get_test_users() -> TestUsersRepository:
    """Helper to load standard test user repository."""
    return TestUsersRepository()
