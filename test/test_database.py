import pytest
import mongomock
from src.database import (
    add_new_data, remove_data_by_name_or_hash, get_all_data,
    get_data_by_name_or_hash, find_package_by_regex,
    add_user, remove_user_by_name, get_all_users, get_user_by_hash
)
from pymongo import MongoClient

@pytest.fixture
def mock_db():
    """Creates a mock MongoDB database."""
    client = mongomock.MongoClient()
    db = client.test_database
    return db

def test_add_new_package(mock_db):
    """Test adding a new package."""
    package_collection = mock_db.packages
    result, package = add_new_data(package_collection, "TestPkg", "http://example.com", "123")
    assert result is True
    assert package["name"] == "TestPkg"

def test_remove_package_by_name_or_hash(mock_db):
    """Test removing a package by name or hash."""
    package_collection = mock_db.packages
    package_collection.insert_one({"name": "TestPkg", "packageId": "123"})
    result = remove_data_by_name_or_hash(package_collection, "TestPkg")
    assert result is True
    assert package_collection.count_documents({}) == 0

def test_get_all_packages(mock_db):
    """Test retrieving all packages."""
    package_collection = mock_db.packages
    package_collection.insert_many([
        {"name": "Pkg1", "packageId": "111"},
        {"name": "Pkg2", "packageId": "222"}
    ])
    result, packages = get_all_data(package_collection)
    assert result is True
    assert len(packages) == 2

def test_add_user(mock_db):
    """Test adding a user."""
    user_collection = mock_db.users
    result, user = add_user(user_collection, "admin", "hash123", True, "group1")
    assert result is True
    assert user["username"] == "admin"

def test_get_user_by_name(mock_db):
    """Test retrieving a user by name."""
    user_collection = mock_db.users
    user_collection.insert_one({"username": "admin", "userHash": "hash123", "isAdmin": True})
    result, user = get_user_by_hash(user_collection, "hash123")
    assert result is True
    assert user["username"] == "admin"
