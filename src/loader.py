from pymongo import MongoClient

from mongo_secrets import MONGO_HOST, MONGO_DB, MONGO_USER, MONGO_PASS, MONGO_PORT


def load_data(collection_name=None, data=None, reinsert=False):
    # MongoDB Cloud setup.
    # client = MongoClient(
    #     f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}?retryWrites=true&w=majority")
    # On-premise setup.
    client = MongoClient(
        f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]

    if reinsert:
        db.drop_collection(collection_name)

    if collection_name not in db.collection_names():
        db.create_collection(collection_name)
        collection = db[collection_name]
        collection.insert_many(data)
        print(f"{collection_name} collection was inserted into MongoDB")

    client.close()
