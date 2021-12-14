import os

from pandas import DataFrame
from pymongo import MongoClient

from mongo_secrets import MONGO_HOST, MONGO_DB, MONGO_PORT

sources = {
    "A1-osoby": {
        "columns": ["datum"]
    },
    "A1-vyleceni": {
        "columns": ["datum"]
    },
    "A1-hospitalizace": {
        "columns": ["datum", "pocet_hosp"]
    },
    "A1-kraj-okres-testy": {
        "columns": ["datum", "prirustkovy_pocet_testu_okres"]
    },

    "A3-ockovani-profese": {
        "columns": ["datum", "poradi_davky", "vakcina", "kraj_nazev", "vekova_skupina", "pohlavi"]
    },

    "B2-osoby": {
        "columns": ["datum", "kraj_nuts_kod"]
    },
    "B2-umrti": {
        "columns": ["datum", "kraj_nuts_kod"]
    },
    "B2-ockovani-profese": {
        "columns": ["datum", "poradi_davky", "vakcina", "kraj_nuts_kod"]
    },

    "C1-osoby": {
        "columns": ["datum", "vek", "kraj_nuts_kod", "okres_lau_kod"]
    },
    "C1-ockovani-profese": {
        "columns": ["datum", "vekova_skupina", "poradi_davky", "vakcina", "kraj_nuts_kod", "orp_bydliste_kod"]
    },
    "C1-obce": {
        "columns": ["kraj_nuts_kod", "kraj_nazev", "okres_lau_kod", "orp_kod"]
    },
    "C1-130142-21data043021": {
        "columns": ["hodnota", "vek_txt", "vuzemi_txt"]
    },

    "V1-osoby": {
        "columns": ["datum", "vek", "okres_lau_kod"]
    },
    "V1-obce": {
        "columns": ["okres_lau_kod", "okres_nazev"]
    },
    "V1-130142-21data043021": {
        "columns": ["hodnota", "vek_txt", "vuzemi_txt"]
    },

    "V2-osoby": {
        "columns": ["datum", "pohlavi"]
    },
}


def load_data():
    # MongoDB Cloud setup.
    # client = MongoClient(
    #     f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}?retryWrites=true&w=majority")
    # On-premise setup.
    client = MongoClient(
        f"mongodb://{MONGO_HOST}:{MONGO_PORT}")
    db = client[MONGO_DB]

    # For each wanted CSV file, extract data from MongoDB and write them into CSV file.
    for source, columns in sources.items():
        if source[3:] not in db.list_collection_names():
            continue

        projection = dict({})
        for column in list(columns.values())[0]:
            projection[column] = 1
        projection["_id"] = False

        df = DataFrame(db[source[3:]].find({}, projection=dict(projection)))
        df.to_csv(f"{os.path.join('data-part2', source)}.csv", index=False)
        print(f"{os.path.join('data-part2', source)}.csv was created")
    client.close()
