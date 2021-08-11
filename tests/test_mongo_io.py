from pathlib import Path

import pytest
from pydatarecognition.cif_io import cif_read
from pydatarecognition.powdercif import PydanticPowderCif


def test_pydantic_export_import(cif_mongodb_client, mongo_cif_source_filepath):
    if cif_mongodb_client:
        db = cif_mongodb_client['test']
        coll = db['cif_json']
        mongo_collections = list(coll.find({}))
        mongo_collections = [PydanticPowderCif(**doc) for doc in mongo_collections]
        ciffiles = Path(mongo_cif_source_filepath).glob("*.cif")
        file_collections = []
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            pcd = cif_read(ciffile_path)
            file_collections.append(pcd)
        for mongo_doc in mongo_collections:
            file_doc = [filedoc for filedoc in file_collections if mongo_doc.id == filedoc.id][0]
            for key, value in mongo_doc:
                if key in file_doc:
                    if key is 'ttheta':
                        # ttheta is not cached, and therefore will mismatch on runs that involve caching, as the cache is created alongside mongodb
                        continue
                    assert file_doc._get_value(key) == value
    else:
        pytest.skip('Could not initialize DB')