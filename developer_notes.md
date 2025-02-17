# Developer notes
The notes below on **Google Cloud Storage Development** and **FastAPI** were
written by former Billinge Group member Zachary Thatcher. The notes decribe
how one should setup a Google Cloud Platform (GCP) account and proceed, just
as they describe how to set up FastAPI related to the use of Mongo Databases.

### Google Cloud Storage Development
The pydantic model now automatically exports all numpy arrays to google cloud when they are json serialized.
This should only affect use on the mongo server, since local running of the application leaves out these arrays
when serializing to the cache.  
  
If you would like to develop for the mongo database, you should set up your own GCP service account and put the key
in the project's pydatarecognition folder with the name 'testing-cif-datarec-secret'. Instructions on how to do so 
can be found below.
- create a GCP account and in the top right, go to console
- when in the console, go to the three hexagons in the top left, click, and select new project
- go through the steps, and make sure the project is active
- on the LHS, select the triple bar icon for the dropdown, and go to API's and Services, and go to library
- search google cloud storage and google cloud storage json api, click on each of them, and enable them
- on the LHS, select the triple bar icon for the dropdown, and go to API's and Services, and select service account
- create a new service account with an arbitrary name, as a role, go to basic -> owner and select, skip the final step
- go to keys, click add key, select json, create
- rename this json file to 'testing-cif-datarec-secret.json' and place it in pydatarecognition/pydatarecognition
  
### FastAPI Development
- update your dependencies
  ```shell
  conda install --file requirements/run.txt
  ```
- Add a secret username and password to a yml file in the pydatarecognition folder named secret_password.yml
  - These should take the following form (you replace the <>, removing the <>)
  ```yaml
  username: <username>
  password: <password>
  ```
- run the following command from the base dir terminal to run the app
  ```shell
  uvicorn pydatarecognition.app:app --reload
  ```
- go to the following in your browser to see (and try out) the API
  ```shell
  http://127.0.0.1:8000/docs
  ```
- the \_\_name__=="\_\_main__" section of mongo_utils.py is currently set up to export example cif data to group mongodb
  atlas instance, which is different from the URI currently hardcoded into the fastapi app
  - Be wary of this and feel free to develop in your own free mongo atlas instance (or locally with no need for username
    or password)
- start to make the app look more like the following project https://github.com/markqiu/fastapi-mongodb-realworld-example-app
