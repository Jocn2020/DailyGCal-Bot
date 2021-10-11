import os
from dotenv import load_dotenv
from types import new_class
import pymongo

# Replace the uri string with your MongoDB deployment's connection string.
load_dotenv('./bot-env/pyvenv.cfg')
conn_str = os.environ.get('ATLAS_URI')
# set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
main_db = client["main"]

def store_new_user(new_user, database):
    user_col = main_db[database]
    current_user = user_col.find_one({"id": new_user["id"]})
    if current_user:
        newvalues = { "$set": new_user }
        user_col.update(current_user, newvalues)
    else:
        user_col.insert_one(new_user)

def remove_user(user_id, database):
    user_col = main_db[database]
    delete_query = {"id": user_id}
    user_col.delete_one(delete_query)

def get_user_cred(user_id, database):
    user_col = main_db[database]
    return user_col.find_one({"id": user_id})

def get_all_user(database):
    return [user for user in main_db[database].find({})]

try:
    print(client.list_database_names())
except Exception:
    print("Unable to connect to the server.")