from pymongo import MongoClient

from mongo_secrets import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_USER, MONGO_PASS


def load_data(collection_name=None, data=None):
    client = MongoClient(
        f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}?retryWrites=true&w=majority")
    db = client[MONGO_DB]

    if collection_name not in db.collection_names():
        db.create_collection(collection_name)

    collection = db[collection_name]
    collection.insert_many(data)
