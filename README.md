# pydatarecognition

[![tests](https://circleci.com/github/Billingegroup/pydatarecognition.svg?style=shield&circle-token=b187a993ea69930d37388bf61dccaf499456a481)](<test>)  
###Development
- Create/activate new conda env
  ```shell
  conda create -n pydatarecognition python>=3.6
  conda activate pydatarecognition
  ```
- Install dependencies (assuming source)
  ```shell
  conda install --file requirements/run.tx
  pip install -r requirements/pip_requirements.txt
  conda install --file requirements/test.txt
  ```

  
###FastAPI Development
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
