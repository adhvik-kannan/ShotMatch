import os
# import logging
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

ROOT_NAME = "ece30861defaultadminuser"

# Connect to MongoDB
def connect_to_mongodb(database: str):
    try:
        mongo_uri = f"mongodb+srv://{os.getenv('USER_NAME')}:{os.getenv('PASSWORD')}@cluster0.9gpef.mongodb.net/{database}?retryWrites=true&w=majority"
        client = MongoClient(mongo_uri)
        db = client[database]
        # logger.info("Connected to MongoDB")
        return True, db
    except Exception as error:
        # logger.debug("Error connecting to MongoDB", exc_info=True)
        return False, error

# Disconnect from MongoDB
def disconnect_mongodb(client: MongoClient):
    try:
        client.close()
        # logger.info("Disconnected from MongoDB")
        return True, None
    except Exception as error:
        # logger.debug("Error disconnecting from MongoDB", exc_info=True)
        return False, error

# Define user schema
def add_user(collection: Collection, username: str, user_hash: str, is_admin: bool, user_group: str):
    try:
        if collection.find_one({"username": username}):
            # logger.info("User already exists")
            return False, "User already exists"
        user = {
            "username": username,
            "isAdmin": is_admin,
            "userHash": user_hash,
            "userGroup": user_group
        }
        collection.insert_one(user)
        # logger.info("User added: %s", user)
        return True, user
    except Exception as error:
        # logger.debug("Error adding user", exc_info=True)
        return False, error

# Remove user
def remove_user_by_name(collection: Collection, username: str):
    try:
        result = collection.delete_one({"username": username})
        if result.deleted_count == 0:
            # logger.info("User does not exist")
            return False, "User does not exist"
        # logger.info("User removed")
        return True, None
    except Exception as error:
        # logger.debug("Error removing user", exc_info=True)
        return False, error

# Fetch users
def get_all_users(collection: Collection):
    try:
        users = list(collection.find())
        # logger.info("All Users: %s", users)
        return True, users
    except Exception as error:
        # logger.debug("Error fetching users", exc_info=True)
        return False, error

# Get user by hash
def get_user_by_hash(collection: Collection, user_hash: str):
    try:
        print(user_hash)
        user = collection.find_one({"userHash": user_hash})
        if not user:
            # logger.info("User not found")
            return False, "User not found"
        # logger.info("User found: %s", user)
        return True, user
    except Exception as error:
        # logger.debug("Error fetching user", exc_info=True)
        return False, error

def get_user_by_email(collection: Collection, email: str):
    try:
        user = collection.find_one({"username": email})
        if not user:
            # logger.info("User not found")
            return False, "User not found"
        return True, user
    except Exception as error:
        # logger.debug("Error fetching user", exc_info=True)
        return False, error
        
# Define data schema 
### FIX THIS WITH WHATEVER DATA YOU NEED
def add_new_data(collection: Collection, name: str, url: str, package_id: str = None, score: str = None, 
                     version: str = None, net_score: float = None, ingestion_method: str = None,
                     readme: str = None, secret: bool = None, user_group: str = None):
    try:
        package = {
            "name": name,
            "url": url,
            "score": score,
            "version": version,
            "packageId": package_id,
            "netScore": net_score,
            "ingestionMethod": ingestion_method,
            "README": readme,
            "secret": secret,
            "userGroup": user_group
        }
        collection.insert_one(package)
        # logger.info("Package added: %s", name)
        return True, package
    except Exception as error:
        # logger.debug("Error adding package", exc_info=True)
        return False, error

# Remove Data
def remove_data_by_name_or_hash(collection: Collection, identifier: str):
    try:
        result = collection.delete_one({"$or": [{"name": identifier}, {"packageId": identifier}]})
        # logger.info("Package removed: %s", result)
        return True
    except Exception as error:
        # logger.debug("Error removing package", exc_info=True)
        return False

# Get all packages
def get_all_data(collection: Collection):
    try:
        packages = list(collection.find())
        # logger.info("All Packages: %s", packages)
        return True, packages
    except Exception as error:
        # logger.debug("Error fetching packages", exc_info=True)
        return False, error

# Get package by name or hash
def get_data_by_name_or_hash(collection: Collection, identifier: str):
    try:
        packages = list(collection.find({"$or": [{"name": identifier}, {"packageId": identifier}]}))
        if not packages:
            # logger.info("No packages found for: %s", identifier)
            return False, []
        packages.sort(key=lambda x: list(map(int, x.get("version", "0").split('.'))), reverse=True)
        return True, packages
    except Exception as error:
        # logger.debug("Error fetching packages", exc_info=True)
        return False, error

# Find package by regex
def find_package_by_regex(collection: Collection, regex: str):
    try:
        pattern = f"^{regex}"
        results = list(collection.find({"$or": [
            {"name": {"$regex": pattern, "$options": "i"}},
            {"README": {"$regex": pattern, "$options": "i"}}
        ]}))
        return True, results
    except Exception as error:
        # logger.debug("Error fetching packages", exc_info=True)
        return False, error
