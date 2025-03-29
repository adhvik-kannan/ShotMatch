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
def add_new_data(collection: Collection, name: str, front_results: any, side_results: any, overall_score: any, mode: str, date: str):
    try:
        package = {
            "name": name,
            "front_results": front_results,
            "side_results": side_results,
            "overall_score": overall_score,
            "mode": mode,
            "date": date
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


if __name__ == "__main__":
    success, db = connect_to_mongodb("nba_players")
    if not success:
        print("Error connecting to MongoDB")
        exit(1)
    nba_players = db["stephen_curry"]
    success, players = get_data_by_name_or_hash(nba_players, "Stephen Curry")
    if not success:
        print("Error fetching players")
        exit(1)
    print(success)
    print(players)
    # Add user
    # success, user = add_user(db["users"], "test", "test", False, "test")
    # if not success:
    #     print("Error adding user")
    #     exit(1)

    # Get all users
    # success, users = get_all_users(db["users"])
    # if not success:
    #     print("Error fetching users")
    #     exit(1)
    # print(users)

    # Get user by hash
    # success, user = get_user_by_hash(db["users"], "test")
    # if not success:
    #     print("Error fetching user")
    #     exit(1)
    # print(user)

    # Add package
    # success, package = add_new_data(db["data"], "test", "test", "test", "test", "test", "test", "test", False, "test")
    # if not success:
    #     print("Error adding package")
    #     exit(1)

    # Get all packages
    # success, packages = get_all_data(db["data"])
    # if not success:
    #     print("Error fetching packages")
    #     exit(1)
    # print(packages)

    # Get package by name or hash
    # success, package = get_data_by_name_or_hash(db["data"], "test")
    # if not success:
    #     print("Error fetching package")
    #     exit(1)
    # print(package)

    # Find package by regex
    # success, packages = find_package_by_regex(db["data"], "test")
    # if not success:
    #     print("Error fetching package")
    #     exit(1)
    # print(packages)

    # Remove user
    # success, error = remove_user_by_name(db["users"], "test")
    # if not success:
    #     print("Error removing user")
    #     exit(1)

    # Remove package
    # success = remove_data_by_name_or_hash(db["data"], "test")
    # if not success:
    #     print("Error removing package")
    #     exit(1)

    success, error = disconnect_mongodb(db)
    # if not success: