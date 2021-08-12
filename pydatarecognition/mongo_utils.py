from pathlib import Path
import json

from pydatarecognition.cif_io import cif_read
from pymongo import MongoClient


def cifs_to_mongo(mongo_db_uri: str, mongo_db_name: str, mongo_collection_name: str, cif_filepath: str) -> MongoClient:
    """
    Adds all cifs found in the cif_filepath directory to the collection pointed to by the uri, db, and collection name
    @param mongo_db_uri: First arg to MongoClient of pymongo. Can be localhost or atlas server e.g.
    mongodb+srv://<username>:<password>@<clustername>.uc5ro.mongodb.net/<databasename>?retryWrites=true&w=majority
    @param mongo_db_name: Database in mongodb to upload CIF data to
    @param mongo_collection_name: Collection in mongodb to upload CIF data to
    @param cif_filepath: Directory containing CIFs that will be uploaded in it's entirety
    @return: Client at the level specified in the URI (e.g. database level if <databasename> provided)
    """
    client = MongoClient(mongo_db_uri, serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client[mongo_db_name]
    col = db[mongo_collection_name]
    ciffiles = Path(cif_filepath).glob("*.cif")
    for ciffile in ciffiles:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        pcd = cif_read(ciffile_path)
        dict = json.loads(pcd.json(by_alias=True))
        col.insert_one(dict)
    return client


if __name__ == "__main__":
    import os
    with open('secret_password.txt', 'r') as f:
        password = f.read()
    client = cifs_to_mongo(f'mongodb+srv://zthatcher:{password}@cluster0.9bj1h.mongodb.net/?retryWrites=true&w=majority', "test",
                            "cif", os.path.join(os.pardir, 'docs\\examples\\cifs'))
    db = client["test"]
    coll = db["cif"]
    mongo_collections = list(coll.find({}))
    pass
