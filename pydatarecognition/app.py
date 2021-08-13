import os
from pathlib import Path
import yaml

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
import motor.motor_asyncio
from pydatarecognition.powdercif import PydanticPowderCif

COLLECTION = "cif"

app = FastAPI()
filepath = Path(os.path.abspath(__file__))
with open(os.path.join(filepath.parent, 'secret_password.yml'), 'r') as f:
    user_secrets = yaml.safe_load(f)
username = user_secrets['username']
password = user_secrets['password']
client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://{username}:{password}@sidewinder.uc5ro.mongodb.net/?retryWrites=true&w=majority')
db = client.test




@app.post("/", response_description="Add new CIF", response_model=PydanticPowderCif)
async def create_cif(powdercif: PydanticPowderCif = Body(...)):
    powdercif = jsonable_encoder(powdercif)
    new_cif = await db[COLLECTION].insert_one(powdercif)
    created_cif = await db[COLLECTION].find_one({"_id": new_cif.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_cif)


@app.get(
    "/", response_description="List all cifs", response_model=List[PydanticPowderCif]
)
async def list_cifs():
    cifs = await db[COLLECTION].find().to_list(1000)
    return cifs


@app.get(
    "/{id}", response_description="Get a single CIF", response_model=PydanticPowderCif
)
async def show_cif(id: str):
    if (cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.put("/{id}", response_description="Update a CIF", response_model=PydanticPowderCif)
async def update_cif(id: str, cif: PydanticPowderCif = Body(...)):
    cif = {k: v for k, v in cif.dict().items() if v is not None}

    if len(cif) >= 1:
        update_result = await db[COLLECTION].update_one({"_id": id}, {"$set": cif})

        if update_result.modified_count == 1:
            if (
                updated_cif := await db[COLLECTION].find_one({"_id": id})
            ) is not None:
                return updated_cif

    if (existing_cif := await db[COLLECTION].find_one({"_id": id})) is not None:
        return existing_cif

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")


@app.delete("/{id}", response_description="Delete a CIF")
async def delete_cif(id: str):
    delete_result = await db[COLLECTION].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"CIF {id} not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="localhost", reload=True)